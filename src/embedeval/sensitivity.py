"""Prompt sensitivity analysis for benchmark robustness measurement.

Generates paraphrased prompt variants and measures how stable benchmark
results are across different phrasings of the same task.
"""

import logging
import random
import re
from pathlib import Path

from pydantic import BaseModel, Field

from embedeval.evaluator import evaluate
from embedeval.llm_client import call_model
from embedeval.models import CaseCategory, EvalResult
from embedeval.runner import Filters, discover_cases, filter_cases

logger = logging.getLogger(__name__)


class CaseSensitivity(BaseModel):
    """Sensitivity result for a single case across prompt variants."""

    case_id: str
    category: CaseCategory | None = None
    original_passed: bool
    variant_results: list[bool]
    robustness: float = Field(ge=0.0, le=1.0)


class SensitivityReport(BaseModel):
    """Prompt sensitivity analysis results."""

    model: str
    total_cases: int
    variants_per_case: int
    avg_robustness: float = Field(ge=0.0, le=1.0)
    cases: list[CaseSensitivity]
    most_sensitive: list[str]
    most_robust: list[str]


def generate_variants(prompt: str, n: int = 3) -> list[str]:
    """Generate n deterministic prompt variants by structural transformation.

    Variant strategies:
    1. Reorder requirement bullet points
    2. Change instruction framing (imperative → descriptive)
    3. Remove output format hint
    """
    variants: list[str] = []

    # Strategy 1: Reorder numbered/bulleted requirements
    lines = prompt.split("\n")
    bullet_groups = _find_bullet_groups(lines)
    if bullet_groups and len(variants) < n:
        reordered = _reorder_bullets(lines, bullet_groups)
        variants.append("\n".join(reordered))

    # Strategy 2: Replace imperative verbs with descriptive framing
    if len(variants) < n:
        rephrased = _rephrase_imperatives(prompt)
        if rephrased != prompt:
            variants.append(rephrased)

    # Strategy 3: Remove "Output ONLY" instruction line
    if len(variants) < n:
        trimmed = _remove_output_instruction(prompt)
        if trimmed != prompt:
            variants.append(trimmed)

    # Pad with original if not enough variants
    while len(variants) < n:
        variants.append(prompt)

    return variants[:n]


def calculate_robustness(
    original_passed: bool,
    variant_results: list[bool],
) -> float:
    """Calculate robustness score for a single case.

    1.0 = all variants agree with original (fully robust)
    0.0 = all variants disagree (maximally sensitive)
    """
    if not variant_results:
        return 1.0
    agreements = sum(1 for v in variant_results if v == original_passed)
    return agreements / len(variant_results)


def run_sensitivity_analysis(
    cases_dir: Path,
    model: str,
    sample_size: int = 30,
    variants_per_case: int = 3,
    seed: int = 42,
) -> SensitivityReport:
    """Run benchmark with prompt variants and measure stability.

    Args:
        cases_dir: Path to cases directory.
        model: LLM model identifier.
        sample_size: Number of cases to sample (0 = all public cases).
        variants_per_case: Number of prompt variants per case.
        seed: Random seed for reproducible sampling.

    Returns:
        SensitivityReport with per-case and aggregate robustness scores.
    """
    all_cases = discover_cases(cases_dir)
    from embedeval.models import Visibility

    public_cases = filter_cases(all_cases, Filters(visibility=Visibility.PUBLIC))

    rng = random.Random(seed)
    if 0 < sample_size < len(public_cases):
        selected = rng.sample(public_cases, sample_size)
    else:
        selected = list(public_cases)

    logger.info(
        "Sensitivity analysis: %d cases, %d variants each",
        len(selected),
        variants_per_case,
    )

    results: list[CaseSensitivity] = []

    for case_dir, meta in selected:
        prompt_file = case_dir / "prompt.md"
        if not prompt_file.is_file():
            continue

        original_prompt = prompt_file.read_text(encoding="utf-8")

        # Run original
        orig_response = call_model(model=model, prompt=original_prompt)
        orig_result = evaluate(
            case_dir=case_dir,
            generated_code=orig_response.generated_code,
            model=model,
            category=meta.category,
        )

        # Run variants
        variants = generate_variants(original_prompt, variants_per_case)
        variant_passed: list[bool] = []
        for variant in variants:
            v_response = call_model(model=model, prompt=variant)
            v_result = evaluate(
                case_dir=case_dir,
                generated_code=v_response.generated_code,
                model=model,
                category=meta.category,
            )
            variant_passed.append(v_result.passed)

        robustness = calculate_robustness(orig_result.passed, variant_passed)

        results.append(
            CaseSensitivity(
                case_id=meta.id,
                category=meta.category,
                original_passed=orig_result.passed,
                variant_results=variant_passed,
                robustness=robustness,
            )
        )
        logger.info(
            "Case %s: original=%s, variants=%s, robustness=%.2f",
            meta.id,
            orig_result.passed,
            variant_passed,
            robustness,
        )

    avg_robustness = (
        sum(c.robustness for c in results) / len(results) if results else 1.0
    )

    sorted_by_robustness = sorted(results, key=lambda c: c.robustness)
    most_sensitive = [c.case_id for c in sorted_by_robustness[:5] if c.robustness < 1.0]
    most_robust = [
        c.case_id for c in sorted_by_robustness[-5:] if c.robustness == 1.0
    ]

    return SensitivityReport(
        model=model,
        total_cases=len(results),
        variants_per_case=variants_per_case,
        avg_robustness=avg_robustness,
        cases=results,
        most_sensitive=most_sensitive,
        most_robust=most_robust,
    )


# --- Internal helpers ---


def _find_bullet_groups(lines: list[str]) -> list[tuple[int, int]]:
    """Find contiguous groups of bullet/numbered lines."""
    groups: list[tuple[int, int]] = []
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        is_bullet = bool(
            re.match(r"^(\d+[\.\)]\s|[-*]\s|•\s)", stripped)
        )
        if is_bullet:
            if start is None:
                start = i
        else:
            if start is not None and i - start >= 3:
                groups.append((start, i))
            start = None
    if start is not None and len(lines) - start >= 3:
        groups.append((start, len(lines)))
    return groups


def _reorder_bullets(
    lines: list[str], groups: list[tuple[int, int]]
) -> list[str]:
    """Reverse the order of bullets in the first group."""
    if not groups:
        return lines
    start, end = groups[0]
    result = list(lines)
    result[start:end] = reversed(lines[start:end])
    return result


def _rephrase_imperatives(prompt: str) -> str:
    """Replace the first matching imperative verb with a descriptive alternative."""
    replacements = [
        (r"\bWrite\b", "Implement"),
        (r"\bCreate\b", "Develop"),
        (r"\bImplement\b", "Construct"),
        (r"\bConfigure\b", "Set up"),
        (r"\bEnsure\b", "Make sure"),
    ]
    for pattern, replacement in replacements:
        result, count = re.subn(pattern, replacement, prompt, count=1)
        if count > 0:
            return result
    return prompt


def _remove_output_instruction(prompt: str) -> str:
    """Remove lines containing output format instructions."""
    lines = prompt.split("\n")
    filtered = [
        line
        for line in lines
        if not re.search(
            r"Output\s+ONLY|output\s+only|ONLY\s+the\s+complete",
            line,
            re.IGNORECASE,
        )
    ]
    return "\n".join(filtered)
