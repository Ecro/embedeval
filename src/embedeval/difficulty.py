"""Item Response Theory (IRT) difficulty calibration.

Estimates empirical difficulty and discrimination parameters for each test case
based on multi-model benchmark results. Compares assigned difficulty labels
(easy/medium/hard) against empirical performance to find mislabeled cases.
"""

import logging
import math
from collections import defaultdict

from pydantic import BaseModel, Field

from embedeval.models import DifficultyTier, EvalResult

logger = logging.getLogger(__name__)


class IRTParams(BaseModel):
    """Empirical difficulty parameters for a test case."""

    case_id: str
    difficulty_b: float = Field(description="Empirical difficulty (0=easy, 1=hard)")
    discrimination_a: float = Field(
        ge=0.0,
        description="Discrimination power (higher = better differentiator)",
    )
    empirical_pass_rate: float = Field(ge=0.0, le=1.0)
    assigned_difficulty: DifficultyTier
    suggested_difficulty: DifficultyTier
    is_mislabeled: bool


class DifficultyReport(BaseModel):
    """Difficulty calibration report."""

    total_cases: int
    models_used: list[str]
    items: list[IRTParams]
    mislabel_count: int
    mislabel_rate: float = Field(ge=0.0, le=1.0)
    floor_cases: list[str] = Field(
        description="Cases all models pass (too easy, no discrimination)"
    )
    ceiling_cases: list[str] = Field(
        description="Cases all models fail (too hard or broken)"
    )


def calibrate_difficulty(
    results: list[EvalResult],
) -> DifficultyReport:
    """Calibrate IRT parameters from multi-model benchmark results.

    Groups results by case_id, computes empirical pass rate across all models,
    then estimates difficulty (b) and discrimination (a) parameters.

    Difficulty (b): 1 - empirical_pass_rate (higher = harder)
    Discrimination (a): variance of per-model pass rates (higher = more discriminating)

    Args:
        results: EvalResult list from one or more models.

    Returns:
        DifficultyReport with per-case parameters and mislabel analysis.
    """
    # Group by case_id → model → pass/fail
    case_model_results: dict[str, dict[str, list[bool]]] = defaultdict(
        lambda: defaultdict(list)
    )
    case_difficulty: dict[str, DifficultyTier] = {}

    for r in results:
        case_model_results[r.case_id][r.model].append(r.passed)
        if r.case_id not in case_difficulty:
            # Extract difficulty from case_id prefix matching metadata
            # Use the first result's metadata if available
            case_difficulty[r.case_id] = _infer_difficulty(r)

    models = sorted(
        {r.model for r in results}
    )

    items: list[IRTParams] = []
    floor_cases: list[str] = []
    ceiling_cases: list[str] = []

    for case_id in sorted(case_model_results):
        model_passes = case_model_results[case_id]

        # Per-model pass rate
        per_model_rates: list[float] = []
        for model in models:
            if model in model_passes:
                attempts = model_passes[model]
                per_model_rates.append(sum(attempts) / len(attempts))

        if not per_model_rates:
            continue

        empirical_pass_rate = sum(per_model_rates) / len(per_model_rates)
        difficulty_b = 1.0 - empirical_pass_rate

        # Discrimination: std dev of per-model pass rates
        if len(per_model_rates) >= 2:
            mean = sum(per_model_rates) / len(per_model_rates)
            variance = sum((r - mean) ** 2 for r in per_model_rates) / len(
                per_model_rates
            )
            discrimination_a = math.sqrt(variance)
        else:
            discrimination_a = 0.0

        assigned = case_difficulty.get(case_id, DifficultyTier.MEDIUM)
        suggested = _suggest_difficulty(empirical_pass_rate)
        is_mislabeled = assigned != suggested

        if empirical_pass_rate == 1.0:
            floor_cases.append(case_id)
        elif empirical_pass_rate == 0.0:
            ceiling_cases.append(case_id)

        items.append(
            IRTParams(
                case_id=case_id,
                difficulty_b=difficulty_b,
                discrimination_a=discrimination_a,
                empirical_pass_rate=empirical_pass_rate,
                assigned_difficulty=assigned,
                suggested_difficulty=suggested,
                is_mislabeled=is_mislabeled,
            )
        )

    mislabel_count = sum(1 for item in items if item.is_mislabeled)
    mislabel_rate = mislabel_count / len(items) if items else 0.0

    return DifficultyReport(
        total_cases=len(items),
        models_used=models,
        items=items,
        mislabel_count=mislabel_count,
        mislabel_rate=mislabel_rate,
        floor_cases=floor_cases,
        ceiling_cases=ceiling_cases,
    )


def _suggest_difficulty(pass_rate: float) -> DifficultyTier:
    """Suggest difficulty tier based on empirical pass rate.

    Thresholds based on METHODOLOGY.md expected pass rates:
    - easy: >80% pass rate
    - medium: 40-80% pass rate
    - hard: <40% pass rate
    """
    if pass_rate > 0.8:
        return DifficultyTier.EASY
    elif pass_rate >= 0.4:
        return DifficultyTier.MEDIUM
    else:
        return DifficultyTier.HARD


def _infer_difficulty(result: EvalResult) -> DifficultyTier:
    """Infer difficulty from EvalResult metadata or case_id pattern."""
    # If the result has no metadata, default to medium
    return DifficultyTier.MEDIUM
