"""Ablation study: measure contribution of each evaluation layer.

Computes pass rates under different layer configurations to quantify
how much each layer contributes to the benchmark's discriminative power.
"""

import logging
from collections import defaultdict

from pydantic import BaseModel, Field

from embedeval.models import EvalResult

logger = logging.getLogger(__name__)


class AblationConfig(BaseModel):
    """A layer configuration for ablation analysis."""

    name: str
    layers_used: list[int] = Field(description="Layer numbers included in this config")
    pass_rate: float = Field(ge=0.0, le=1.0)
    cases_passed: int
    total_cases: int


class AblationReport(BaseModel):
    """Ablation study results."""

    model: str
    configs: list[AblationConfig]
    layer_contributions: dict[str, float] = Field(
        description="Layer name → delta (how much adding this layer reduces pass rate)"
    )


def run_ablation(
    results: list[EvalResult],
    model: str | None = None,
) -> AblationReport:
    """Calculate pass rates under different layer configurations.

    Configurations tested:
    - L0 only (static analysis)
    - L0 + L3 (static + heuristic, no compilation)
    - L0 + L1 (static + compile)
    - L0 + L1 + L3 (static + compile + heuristic)
    - Full (L0-L4)

    Args:
        results: EvalResult list (single model recommended).
        model: Model to filter for. If None, uses all results.

    Returns:
        AblationReport with per-config pass rates and layer contributions.
    """
    if model:
        results = [r for r in results if r.model == model]

    effective_model = model or (results[0].model if results else "unknown")

    # Group by case_id, take best attempt
    by_case: dict[str, EvalResult] = {}
    for r in results:
        if r.case_id not in by_case or r.passed:
            by_case[r.case_id] = r

    total = len(by_case)
    if total == 0:
        return AblationReport(
            model=effective_model,
            configs=[],
            layer_contributions={},
        )

    configs_spec = [
        ("L0 only", [0]),
        ("L0 + L3", [0, 3]),
        ("L0 + L1", [0, 1]),
        ("L0 + L1 + L3", [0, 1, 3]),
        ("Full (L0-L4)", [0, 1, 2, 3, 4]),
    ]

    configs: list[AblationConfig] = []
    pass_rates: dict[str, float] = {}

    for name, layers in configs_spec:
        passed = 0
        for result in by_case.values():
            if _passes_config(result, layers):
                passed += 1
        rate = passed / total
        pass_rates[name] = rate
        configs.append(
            AblationConfig(
                name=name,
                layers_used=layers,
                pass_rate=rate,
                cases_passed=passed,
                total_cases=total,
            )
        )

    # Layer contributions: how much adding each layer reduces pass rate
    contributions: dict[str, float] = {}

    l0_rate = pass_rates.get("L0 only", 0.0)
    l0_l3_rate = pass_rates.get("L0 + L3", 0.0)
    l0_l1_rate = pass_rates.get("L0 + L1", 0.0)
    l0_l1_l3_rate = pass_rates.get("L0 + L1 + L3", 0.0)

    contributions["L1 (compile)"] = round(l0_rate - l0_l1_rate, 4)
    contributions["L3 (heuristic)"] = round(l0_rate - l0_l3_rate, 4)
    contributions["L1+L3 combined"] = round(l0_rate - l0_l1_l3_rate, 4)

    return AblationReport(
        model=effective_model,
        configs=configs,
        layer_contributions=contributions,
    )


def _passes_config(result: EvalResult, layers: list[int]) -> bool:
    """Check if a result passes under a specific layer configuration.

    A result passes if all specified layers passed (or were skipped).
    """
    for layer_num in layers:
        if layer_num < len(result.layers):
            layer = result.layers[layer_num]
            if layer.error and "Skipped" in layer.error:
                continue
            if not layer.passed:
                return False
    return True
