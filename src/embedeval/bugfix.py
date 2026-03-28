"""Bug fix scenario: evaluate LLM ability to diagnose and repair embedded code defects.

Reuses existing negatives.py mutations as seeded bugs. Applies mutations to
reference solutions, then asks the LLM to find and fix the bug.
"""

import importlib.util
import logging
from pathlib import Path
from types import ModuleType

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from embedeval.evaluator import evaluate
from embedeval.llm_client import call_model
from embedeval.models import CaseMetadata, EvalResult, Visibility
from embedeval.runner import Filters, discover_cases, filter_cases

logger = logging.getLogger(__name__)

BUGFIX_PROMPT_TEMPLATE = """\
The following {platform} C code for an embedded system has a bug.
Category: {category} — {title}

## Buggy Code

```c
{buggy_code}
```

## Bug Hint

{description}

## Task

Find and fix the bug in the code above.
Output ONLY the complete corrected C source file.
"""


class BugfixCase:
    """A single bug fix test case derived from a mutation."""

    def __init__(
        self,
        case_id: str,
        mutation_name: str,
        buggy_code: str,
        description: str,
        case_dir: Path,
        metadata: CaseMetadata,
    ):
        self.case_id = case_id
        self.mutation_name = mutation_name
        self.buggy_code = buggy_code
        self.description = description
        self.case_dir = case_dir
        self.metadata = metadata

    @property
    def bugfix_id(self) -> str:
        return f"{self.case_id}:{self.mutation_name}"


def discover_bugfix_cases(
    cases_dir: Path,
    filters: Filters | None = None,
    include_private: bool = False,
) -> list[BugfixCase]:
    """Discover all bugfix cases from negatives.py must_fail mutations.

    For each case with checks/negatives.py:
    1. Load reference/main.c
    2. Load NEGATIVES list
    3. For each must_fail mutation: apply to reference → create BugfixCase
    """
    all_cases = discover_cases(cases_dir)
    effective_filters = filters or Filters()
    if not include_private and effective_filters.visibility is None:
        effective_filters.visibility = Visibility.PUBLIC
    selected = filter_cases(all_cases, effective_filters)

    bugfix_cases: list[BugfixCase] = []

    for case_dir, meta in selected:
        negatives_path = case_dir / "checks" / "negatives.py"
        reference_path = case_dir / "reference" / "main.c"

        if not negatives_path.is_file() or not reference_path.is_file():
            continue

        reference_code = reference_path.read_text(encoding="utf-8")
        negatives_module = _load_negatives_module(negatives_path)
        if negatives_module is None:
            continue

        negatives_list = getattr(negatives_module, "NEGATIVES", [])

        for neg in negatives_list:
            if "must_fail" not in neg:
                continue

            mutation_fn = neg.get("mutation")
            if mutation_fn is None:
                continue

            try:
                buggy_code = mutation_fn(reference_code)
            except Exception as exc:
                logger.warning(
                    "Mutation %s failed on %s: %s",
                    neg.get("name", "unknown"),
                    meta.id,
                    exc,
                )
                continue

            bugfix_cases.append(
                BugfixCase(
                    case_id=meta.id,
                    mutation_name=neg.get("name", "unknown"),
                    buggy_code=buggy_code,
                    description=neg.get("description", "Find and fix the bug."),
                    case_dir=case_dir,
                    metadata=meta,
                )
            )

    logger.info("Discovered %d bugfix cases", len(bugfix_cases))
    return bugfix_cases


def generate_bugfix_prompt(bugfix_case: BugfixCase) -> str:
    """Generate a standardized bug fix prompt."""
    return BUGFIX_PROMPT_TEMPLATE.format(
        platform=bugfix_case.metadata.platform.value,
        category=bugfix_case.metadata.category.value,
        title=bugfix_case.metadata.title,
        buggy_code=bugfix_case.buggy_code,
        description=bugfix_case.description,
    )


def run_bugfix_benchmark(
    cases_dir: Path,
    model: str,
    filters: Filters | None = None,
    include_private: bool = False,
) -> list[EvalResult]:
    """Run bug fix scenario benchmark.

    Discovers bugfix cases, generates prompts with buggy code,
    calls LLM to fix, evaluates the fixed code with existing checks.
    """
    bugfix_cases = discover_bugfix_cases(
        cases_dir, filters=filters, include_private=include_private
    )

    if not bugfix_cases:
        logger.warning("No bugfix cases found")
        return []

    results: list[EvalResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            f"Bugfix: {len(bugfix_cases)} cases", total=len(bugfix_cases)
        )

        for bc in bugfix_cases:
            progress.update(task, description=f"[bugfix] {bc.bugfix_id}")

            prompt = generate_bugfix_prompt(bc)
            response = call_model(model=model, prompt=prompt)

            result = evaluate(
                case_dir=bc.case_dir,
                generated_code=response.generated_code,
                model=model,
                token_usage=response.token_usage,
                cost_usd=response.cost_usd,
                category=bc.metadata.category,
            )

            # Tag the result with bugfix metadata
            result.case_id = bc.bugfix_id

            results.append(result)
            progress.advance(task)

            status = "PASS" if result.passed else f"FAIL@L{result.failed_at_layer}"
            logger.info("Bugfix %s: %s", bc.bugfix_id, status)

    logger.info(
        "Bugfix benchmark complete: %d/%d passed",
        sum(1 for r in results if r.passed),
        len(results),
    )
    return results


def _load_negatives_module(path: Path) -> ModuleType | None:
    """Load a negatives.py module."""
    spec = importlib.util.spec_from_file_location("negatives", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        logger.warning("Failed to load negatives module %s: %s", path, exc)
        return None
    return module
