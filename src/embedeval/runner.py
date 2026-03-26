"""EmbedEval benchmark runner."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from embedeval.evaluator import evaluate
from embedeval.llm_client import _extract_code, call_model
from embedeval.models import CaseCategory, CaseMetadata, DifficultyTier, EvalResult, Visibility

logger = logging.getLogger(__name__)


@dataclass
class Filters:
    """Filtering criteria for benchmark case selection."""

    categories: list[CaseCategory] = field(default_factory=list)
    difficulties: list[DifficultyTier] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    visibility: Visibility | None = None
    after_date: str | None = None  # ISO date string; only include cases created after this date


def load_case_metadata(case_dir: Path) -> CaseMetadata | None:
    """Load case metadata from a case directory's metadata.yaml.

    Args:
        case_dir: Path to the case directory.

    Returns:
        CaseMetadata if valid, None if metadata is missing or invalid.
    """
    metadata_file = case_dir / "metadata.yaml"
    if not metadata_file.is_file():
        logger.warning("No metadata.yaml in %s", case_dir)
        return None

    try:
        raw = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            logger.warning("Invalid metadata format in %s", case_dir)
            return None
        return CaseMetadata(**raw)
    except Exception as exc:
        logger.warning("Failed to parse metadata in %s: %s", case_dir, exc)
        return None


def discover_cases(cases_dir: Path) -> list[tuple[Path, CaseMetadata]]:
    """Discover all valid case directories under cases_dir.

    Args:
        cases_dir: Root directory containing case subdirectories.

    Returns:
        List of (case_dir, metadata) tuples for valid cases.
    """
    if not cases_dir.is_dir():
        logger.warning("Cases directory does not exist: %s", cases_dir)
        return []

    cases: list[tuple[Path, CaseMetadata]] = []
    for case_dir in sorted(cases_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        metadata = load_case_metadata(case_dir)
        if metadata is not None:
            cases.append((case_dir, metadata))

    logger.info("Discovered %d cases in %s", len(cases), cases_dir)
    return cases


def filter_cases(
    cases: list[tuple[Path, CaseMetadata]],
    filters: Filters,
) -> list[tuple[Path, CaseMetadata]]:
    """Filter cases by category, difficulty, and tags.

    Args:
        cases: List of (case_dir, metadata) tuples.
        filters: Filtering criteria.

    Returns:
        Filtered list of cases.
    """
    filtered: list[tuple[Path, CaseMetadata]] = []
    for case_dir, meta in cases:
        if filters.categories and meta.category not in filters.categories:
            continue
        if filters.difficulties and meta.difficulty not in filters.difficulties:
            continue
        if filters.tags and not any(tag in meta.tags for tag in filters.tags):
            continue
        if filters.visibility is not None and meta.visibility != filters.visibility:
            continue
        if filters.after_date and meta.created_date:
            try:
                from datetime import date as _date
                _date.fromisoformat(filters.after_date)
                _date.fromisoformat(meta.created_date)
            except ValueError:
                pass  # skip filter on invalid format
            else:
                if meta.created_date <= filters.after_date:
                    continue
        filtered.append((case_dir, meta))

    logger.info(
        "Filtered %d -> %d cases",
        len(cases),
        len(filtered),
    )
    return filtered


def _load_prompt(case_dir: Path) -> str:
    """Load the prompt file from a case directory."""
    prompt_file = case_dir / "prompt.md"
    if prompt_file.is_file():
        return prompt_file.read_text(encoding="utf-8")

    prompt_txt = case_dir / "prompt.txt"
    if prompt_txt.is_file():
        return prompt_txt.read_text(encoding="utf-8")

    return f"Generate Zephyr RTOS code for case: {case_dir.name}"


def _collect_context_files(case_dir: Path) -> list[str]:
    """Collect context files from the case directory."""
    context_dir = case_dir / "context"
    if not context_dir.is_dir():
        return []
    return [str(f) for f in sorted(context_dir.iterdir()) if f.is_file()]


def run_benchmark(
    cases_dir: Path,
    model: str,
    filters: Filters | None = None,
    attempts: int = 1,
    feedback_rounds: int = 0,
) -> list[EvalResult]:
    """Run the benchmark pipeline: discover, filter, LLM call, evaluate.

    Args:
        cases_dir: Root directory containing case subdirectories.
        model: Model identifier for LLM calls.
        filters: Optional filtering criteria.
        attempts: Number of attempts per case (for pass@k calculation).
        feedback_rounds: Number of compiler-feedback retry rounds (0 = disabled).
            When > 0 and a case fails at L0 or L1, the error message is fed back
            to the LLM for up to `feedback_rounds` additional attempts.

    Returns:
        List of EvalResult for all case/attempt combinations.
    """
    effective_filters = filters or Filters()
    all_cases = discover_cases(cases_dir)
    selected = filter_cases(all_cases, effective_filters)

    if not selected:
        logger.warning("No cases selected after filtering")
        return []

    results: list[EvalResult] = []
    total_tasks = len(selected) * attempts

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            f"Running {len(selected)} cases x {attempts} attempts",
            total=total_tasks,
        )

        for case_dir, meta in selected:
            prompt = _load_prompt(case_dir)
            context_files = _collect_context_files(case_dir)

            for attempt in range(1, attempts + 1):
                progress.update(
                    task,
                    description=f"[{meta.id}] attempt {attempt}/{attempts}",
                )

                llm_response = call_model(
                    model=model,
                    prompt=prompt,
                    context_files=context_files,
                )

                result = evaluate(
                    case_dir=case_dir,
                    generated_code=llm_response.generated_code,
                    model=model,
                    attempt=attempt,
                    token_usage=llm_response.token_usage,
                    cost_usd=llm_response.cost_usd,
                    category=meta.category,
                )

                # Compiler feedback loop: retry with error context on early layer failures
                if (
                    feedback_rounds > 0
                    and not result.passed
                    and result.failed_at_layer is not None
                    and result.failed_at_layer <= 1
                ):
                    for feedback_round in range(feedback_rounds):
                        failed_layer = result.layers[result.failed_at_layer]
                        error_msg = failed_layer.error or ""
                        failed_details = "\n".join(
                            f"- {d.check_name}: expected={d.expected}, actual={d.actual}"
                            for d in failed_layer.details if not d.passed
                        )
                        error_info = "\n".join(filter(None, [error_msg, failed_details])) or "Check failed"
                        feedback_prompt = (
                            f"Your previous code had the following error:\n"
                            f"```\n{error_info[:800]}\n```\n\n"
                            f"Original task:\n{prompt}\n\n"
                            f"Please fix the code and output ONLY the complete corrected C source file."
                        )
                        fb_response = call_model(
                            model=model, prompt=feedback_prompt
                        )
                        generated_code = fb_response.generated_code
                        result = evaluate(
                            case_dir=case_dir,
                            generated_code=generated_code,
                            model=model,
                            attempt=attempt,
                            token_usage=fb_response.token_usage,
                            cost_usd=fb_response.cost_usd,
                            category=meta.category,
                        )
                        logger.info(
                            "Feedback round %d/%d for case %s: %s",
                            feedback_round + 1,
                            feedback_rounds,
                            meta.id,
                            "PASS" if result.passed else f"FAIL@L{result.failed_at_layer}",
                        )
                        if result.passed:
                            break

                results.append(result)
                progress.advance(task)

                status = "PASS" if result.passed else f"FAIL@L{result.failed_at_layer}"
                logger.info(
                    "Case %s attempt %d: %s",
                    meta.id,
                    attempt,
                    status,
                )

    logger.info("Benchmark complete: %d results", len(results))
    return results
