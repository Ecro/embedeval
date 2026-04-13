"""EmbedEval benchmark runner."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from embedeval.evaluator import evaluate
from embedeval.llm_client import call_model
from embedeval.models import (
    CaseCategory,
    CaseMetadata,
    CaseTier,
    CheckDetail,
    DifficultyTier,
    EvalResult,
    LayerResult,
    TokenUsage,
    Visibility,
)

logger = logging.getLogger(__name__)


@dataclass
class Filters:
    """Filtering criteria for benchmark case selection."""

    categories: list[CaseCategory] = field(default_factory=list)
    difficulties: list[DifficultyTier] = field(default_factory=list)
    tiers: list[CaseTier] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    visibility: Visibility | None = None
    # ISO date string; only include cases created after this date
    after_date: str | None = None
    case_ids: list[str] | None = None  # explicit case ID whitelist (for retest-only)


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
        if filters.case_ids is not None and meta.id not in filters.case_ids:
            continue
        if filters.categories and meta.category not in filters.categories:
            continue
        if filters.difficulties and meta.difficulty not in filters.difficulties:
            continue
        if filters.tiers and meta.tier not in filters.tiers:
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


def _inject_board_target(prompt: str, meta: CaseMetadata) -> str:
    """Inject build target board information into the prompt.

    Adds a target board line so the LLM knows which board to write code for.
    """
    board = meta.build_board or "native_sim"
    return prompt.rstrip() + "\n\nTarget board: " + board + "\n"


def _make_error_result(
    meta: CaseMetadata,
    model: str,
    attempt: int,
    exc: BaseException,
) -> EvalResult:
    """Synthesize a FAIL@L0 EvalResult for an unhandled per-case error."""
    error_msg = f"{type(exc).__name__}: {exc}"
    result = EvalResult(
        case_id=meta.id,
        category=meta.category,
        model=model,
        attempt=attempt,
        generated_code="",
        layers=[
            LayerResult(
                layer=0,
                name="static_analysis",
                passed=False,
                details=[
                    CheckDetail(
                        check_name="llm_call",
                        passed=False,
                        expected="LLM response",
                        actual=error_msg[:500],
                        check_type="llm_error",
                    )
                ],
                error=error_msg[:500],
                duration_seconds=0.0,
            )
        ],
        failed_at_layer=0,
        passed=False,
        total_score=0.0,
        duration_seconds=0.0,
        token_usage=TokenUsage(
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
        ),
        cost_usd=0.0,
    )
    result.tier = meta.tier
    result.reasoning_types = meta.reasoning_types
    return result


def _load_checkpoint(path: Path) -> dict[str, EvalResult]:
    """Load previously completed results from a JSONL checkpoint file.

    Returns a mapping of case_id -> EvalResult for cases that were
    already evaluated in a prior (interrupted) invocation.
    """
    if not path.is_file():
        return {}
    completed: dict[str, EvalResult] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            result = EvalResult.model_validate(data)
            completed[result.case_id] = result
        except Exception as exc:  # noqa: BLE001
            logger.warning("Ignoring bad checkpoint line: %s", exc)
    logger.info(
        "Loaded %d completed case(s) from checkpoint %s",
        len(completed),
        path,
    )
    return completed


def _append_checkpoint(path: Path, result: EvalResult) -> None:
    """Append one EvalResult as a single JSONL line to the checkpoint."""
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result.model_dump(mode="json"), ensure_ascii=False))
        f.write("\n")


def _run_single_case(
    *,
    meta: CaseMetadata,
    case_dir: Path,
    prompt: str,
    context_files: list[str],
    model: str,
    attempt: int,
    feedback_rounds: int,
) -> EvalResult:
    """Evaluate one case/attempt — extracted so the caller can wrap it
    in a broad try/except without duplicating the happy-path logic."""
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
    result.tier = meta.tier
    result.reasoning_types = meta.reasoning_types

    # Compiler feedback loop: retry with error context on early failures
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
                for d in failed_layer.details
                if not d.passed
            )
            error_info = (
                "\n".join(filter(None, [error_msg, failed_details])) or "Check failed"
            )
            feedback_prompt = (
                f"Your previous code had the following error:\n"
                f"```\n{error_info[:800]}\n```\n\n"
                f"Original task:\n{prompt}\n\n"
                f"Please fix the code and output ONLY the complete"
                f" corrected C source file."
            )
            fb_response = call_model(model=model, prompt=feedback_prompt)
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

    return result


def run_benchmark(
    cases_dir: Path,
    model: str,
    filters: Filters | None = None,
    attempts: int = 1,
    feedback_rounds: int = 0,
    include_private: bool = False,
    extra_cases_dirs: list[Path] | None = None,
    checkpoint_path: Path | None = None,
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
        include_private: If True, include private (held-out) cases.
            Defaults to False for contamination prevention.
        extra_cases_dirs: Additional directories to discover cases from
            (e.g., private cases from a separate repo).
        checkpoint_path: Optional path to a JSONL checkpoint file.
            If the file exists, previously completed cases are loaded
            and skipped. Each newly completed case is appended
            immediately so the run can resume after an interruption.

    Returns:
        List of EvalResult for all case/attempt combinations.
    """
    effective_filters = filters or Filters()
    if not include_private and effective_filters.visibility is None:
        effective_filters.visibility = Visibility.PUBLIC
    all_cases = discover_cases(cases_dir)
    for extra_dir in extra_cases_dirs or []:
        all_cases.extend(discover_cases(extra_dir))
    selected = filter_cases(all_cases, effective_filters)

    if not selected:
        logger.warning("No cases selected after filtering")
        return []

    # Load checkpoint from a prior interrupted run (if any)
    completed: dict[str, EvalResult] = {}
    if checkpoint_path is not None:
        completed = _load_checkpoint(checkpoint_path)

    results: list[EvalResult] = list(completed.values())
    total_tasks = len(selected) * attempts
    skipped = 0

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
            # Skip cases already completed in a prior (interrupted) run
            if meta.id in completed:
                skipped += 1
                progress.advance(task, advance=attempts)
                continue

            prompt = _load_prompt(case_dir)
            prompt = _inject_board_target(prompt, meta)
            context_files = _collect_context_files(case_dir)

            for attempt in range(1, attempts + 1):
                progress.update(
                    task,
                    description=f"[{meta.id}] attempt {attempt}/{attempts}",
                )

                try:
                    result = _run_single_case(
                        meta=meta,
                        case_dir=case_dir,
                        prompt=prompt,
                        context_files=context_files,
                        model=model,
                        attempt=attempt,
                        feedback_rounds=feedback_rounds,
                    )
                except Exception as exc:  # noqa: BLE001
                    # Catch ANY per-case error (UnicodeDecodeError,
                    # network timeouts, JSON parse failures, etc.) so
                    # one broken case doesn't kill the entire run.
                    logger.exception(
                        "Case %s attempt %d: unhandled %s — recording FAIL@L0",
                        meta.id,
                        attempt,
                        type(exc).__name__,
                    )
                    result = _make_error_result(meta, model, attempt, exc)

                results.append(result)
                progress.advance(task)

                # Checkpoint: persist immediately so crashes don't
                # discard hours of prior progress.
                if checkpoint_path is not None:
                    _append_checkpoint(checkpoint_path, result)

                status = "PASS" if result.passed else f"FAIL@L{result.failed_at_layer}"
                logger.info(
                    "Case %s attempt %d: %s",
                    meta.id,
                    attempt,
                    status,
                )

    if skipped:
        logger.info(
            "Resumed from checkpoint: %d cases skipped, %d new",
            skipped,
            len(results) - len(completed),
        )
    logger.info("Benchmark complete: %d results", len(results))
    return results
