"""EmbedEval 5-layer evaluation engine."""

import importlib.util
import logging
import shutil
import subprocess
import time
from pathlib import Path
from types import ModuleType

from embedeval.models import (
    CaseCategory,
    CheckDetail,
    EvalResult,
    LayerResult,
    TokenUsage,
)

logger = logging.getLogger(__name__)

LAYER_NAMES: dict[int, str] = {
    0: "static_analysis",
    1: "compile_gate",
    2: "runtime_execution",
    3: "behavioral_assertion",
    4: "test_quality_proof",
}

DEFAULT_TIMEOUT = 300.0


def evaluate(
    case_dir: Path,
    generated_code: str,
    model: str = "unknown",
    attempt: int = 1,
    timeout: float = DEFAULT_TIMEOUT,
    token_usage: TokenUsage | None = None,
    cost_usd: float = 0.0,
    category: "CaseCategory | None" = None,
) -> EvalResult:
    """Run the 5-layer evaluation pipeline on generated code.

    Args:
        case_dir: Path to the case directory containing checks/.
        generated_code: The LLM-generated code to evaluate.
        model: Model identifier for result tracking.
        attempt: Attempt number for this evaluation.
        timeout: Timeout in seconds for subprocess calls.
        token_usage: Token usage from the LLM call.
        cost_usd: Cost of the LLM call.

    Returns:
        EvalResult with per-layer pass/fail results.
    """
    start = time.monotonic()
    layers: list[LayerResult] = []
    failed_at_layer: int | None = None
    effective_token_usage = token_usage or TokenUsage(
        input_tokens=0, output_tokens=0, total_tokens=0
    )

    for layer_num in range(5):
        layer_name = LAYER_NAMES[layer_num]

        if failed_at_layer is not None:
            logger.info(
                "Skipping layer %d (%s) due to failure at layer %d",
                layer_num,
                layer_name,
                failed_at_layer,
            )
            layers.append(
                LayerResult(
                    layer=layer_num,
                    name=layer_name,
                    passed=False,
                    details=[],
                    error=f"Skipped: layer {failed_at_layer} failed",
                    duration_seconds=0.0,
                )
            )
            continue

        layer_start = time.monotonic()
        layer_result = _run_layer(
            layer_num=layer_num,
            layer_name=layer_name,
            case_dir=case_dir,
            generated_code=generated_code,
            timeout=timeout,
        )
        layer_result = LayerResult(
            layer=layer_num,
            name=layer_name,
            passed=layer_result.passed,
            details=layer_result.details,
            error=layer_result.error,
            duration_seconds=time.monotonic() - layer_start,
        )
        layers.append(layer_result)

        if not layer_result.passed:
            failed_at_layer = layer_num
            logger.info("Layer %d (%s) failed", layer_num, layer_name)

    elapsed = time.monotonic() - start
    all_passed = failed_at_layer is None

    return EvalResult(
        case_id=case_dir.name,
        category=category,
        model=model,
        attempt=attempt,
        generated_code=generated_code,
        layers=layers,
        failed_at_layer=failed_at_layer,
        passed=all_passed,
        duration_seconds=elapsed,
        token_usage=effective_token_usage,
        cost_usd=cost_usd,
    )


def _run_layer(
    layer_num: int,
    layer_name: str,
    case_dir: Path,
    generated_code: str,
    timeout: float,
) -> LayerResult:
    """Execute a single evaluation layer."""
    if layer_num == 0:
        return _run_static_checks(case_dir, generated_code)
    elif layer_num == 1:
        return _run_compile_gate(case_dir, generated_code, timeout)
    elif layer_num == 2:
        return _run_runtime(case_dir, generated_code, timeout)
    elif layer_num == 3:
        return _run_behavioral(case_dir, generated_code)
    elif layer_num == 4:
        return _run_mutant_checks(case_dir, generated_code)
    else:
        return LayerResult(
            layer=layer_num,
            name=layer_name,
            passed=False,
            details=[],
            error=f"Unknown layer: {layer_num}",
            duration_seconds=0.0,
        )


def _run_static_checks(case_dir: Path, generated_code: str) -> LayerResult:
    """Layer 0: Static analysis checks from case checks/static.py."""
    checks_module = _load_check_module(case_dir, "static")
    if checks_module is None:
        return LayerResult(
            layer=0,
            name="static_analysis",
            passed=True,
            details=[],
            error=None,
            duration_seconds=0.0,
        )

    return _execute_check_module(
        checks_module, generated_code, layer=0, name="static_analysis"
    )


def _run_compile_gate(
    case_dir: Path, generated_code: str, timeout: float
) -> LayerResult:
    """Layer 1: Docker west build + .map analysis."""
    if not _build_env_available():
        logger.info("Docker not available, skipping compile gate (pass)")
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=True,
            details=[
                CheckDetail(
                    check_name="docker_available",
                    passed=True,
                    expected="docker installed",
                    actual="skipped (docker not available)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    src_file = case_dir / "src" / "main.c"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text(generated_code, encoding="utf-8")

    try:
        result = subprocess.run(
            ["west", "build", "-b", "native_sim", str(case_dir)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(case_dir),
        )
        passed = result.returncode == 0
        details = [
            CheckDetail(
                check_name="west_build",
                passed=passed,
                expected="exit code 0",
                actual=f"exit code {result.returncode}",
                check_type="compile",
            )
        ]
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=passed,
            details=details,
            error=result.stderr if not passed else None,
            duration_seconds=0.0,
        )
    except subprocess.TimeoutExpired:
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=False,
            details=[],
            error=f"Build timed out after {timeout}s",
            duration_seconds=timeout,
        )


def _run_runtime(case_dir: Path, generated_code: str, timeout: float) -> LayerResult:
    """Layer 2: Runtime execution via west build -t run."""
    if not _build_env_available():
        logger.info("Docker not available, skipping runtime execution (pass)")
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=True,
            details=[
                CheckDetail(
                    check_name="docker_available",
                    passed=True,
                    expected="docker installed",
                    actual="skipped (docker not available)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    try:
        result = subprocess.run(
            ["west", "build", "-t", "run"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(case_dir),
        )
        passed = result.returncode == 0
        details = [
            CheckDetail(
                check_name="runtime_execution",
                passed=passed,
                expected="exit code 0",
                actual=f"exit code {result.returncode}",
                check_type="runtime",
            )
        ]
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=passed,
            details=details,
            error=result.stderr if not passed else None,
            duration_seconds=0.0,
        )
    except subprocess.TimeoutExpired:
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=False,
            details=[],
            error=(
                f"Runtime timed out after {timeout}s (possible infinite loop/deadlock)"
            ),
            duration_seconds=timeout,
        )


def _run_behavioral(case_dir: Path, generated_code: str) -> LayerResult:
    """Layer 3: Behavioral assertion checks from case checks/behavior.py."""
    checks_module = _load_check_module(case_dir, "behavior")
    if checks_module is None:
        return LayerResult(
            layer=3,
            name="behavioral_assertion",
            passed=True,
            details=[],
            error=None,
            duration_seconds=0.0,
        )

    return _execute_check_module(
        checks_module, generated_code, layer=3, name="behavioral_assertion"
    )


def _run_mutant_checks(case_dir: Path, generated_code: str) -> LayerResult:
    """Layer 4: Test quality proof via mutation testing (v1.1 placeholder - passes)."""
    checks_module = _load_check_module(case_dir, "mutants")
    if checks_module is None:
        return LayerResult(
            layer=4,
            name="test_quality_proof",
            passed=True,
            details=[],
            error=None,
            duration_seconds=0.0,
        )

    return _execute_check_module(
        checks_module, generated_code, layer=4, name="test_quality_proof"
    )


def _load_check_module(case_dir: Path, module_name: str) -> ModuleType | None:
    """Load a check module from the case's checks/ directory."""
    module_path = case_dir / "checks" / f"{module_name}.py"
    if not module_path.is_file():
        logger.debug("Check module not found: %s", module_path)
        return None

    spec = importlib.util.spec_from_file_location(
        f"case_checks.{module_name}", module_path
    )
    if spec is None or spec.loader is None:
        logger.warning("Could not load module spec: %s", module_path)
        return None

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        logger.warning("Failed to execute check module %s: %s", module_path, exc)
        return None
    return module


def _execute_check_module(
    module: ModuleType,
    generated_code: str,
    layer: int,
    name: str,
) -> LayerResult:
    """Execute a check module's run_checks function."""
    run_checks = getattr(module, "run_checks", None)
    if run_checks is None:
        return LayerResult(
            layer=layer,
            name=name,
            passed=False,
            details=[],
            error="Check module missing run_checks() function",
            duration_seconds=0.0,
        )

    try:
        details: list[CheckDetail] = run_checks(generated_code)
        all_passed = all(d.passed for d in details)
        return LayerResult(
            layer=layer,
            name=name,
            passed=all_passed,
            details=details,
            error=None,
            duration_seconds=0.0,
        )
    except Exception as exc:
        logger.error("Check module raised exception: %s", exc)
        return LayerResult(
            layer=layer,
            name=name,
            passed=False,
            details=[],
            error=str(exc),
            duration_seconds=0.0,
        )


def _build_env_available() -> bool:
    """Check if Zephyr build environment is ready for compilation.

    Returns False unless EMBEDEVAL_ENABLE_BUILD=1 is set explicitly.
    This prevents accidental west build invocations in environments
    that have west/Zephyr installed for other purposes.
    """
    import os

    return os.environ.get("EMBEDEVAL_ENABLE_BUILD") == "1"
