"""EmbedEval 5-layer evaluation engine."""

import importlib.util
import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from types import ModuleType
from typing import Any

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
    3: "static_heuristic",
    4: "test_quality_proof",
}

DEFAULT_TIMEOUT = 300.0
# Embedded firmware runs forever (while(1) + k_sleep). L2 captures output
# for a short window, then kills the process and validates what was printed.
RUNTIME_TIMEOUT = 10.0


def _extract_build_errors(stdout: str, stderr: str) -> str:
    """Extract meaningful error lines from build output.

    Build logs can be very long. Instead of blindly truncating the tail,
    extract lines containing 'error:' or 'fatal error:' which carry the
    actual compiler diagnostics, then append the tail for context.
    """
    combined = stdout + "\n" + stderr
    lines = combined.splitlines()

    error_lines = [
        line for line in lines
        if any(marker in line.lower() for marker in (
            "error:", "fatal error:", "undefined reference", "no such file",
            "undeclared", "linker command failed",
        ))
    ]

    if error_lines:
        # Error lines first (most valuable), then tail for context
        error_section = "\n".join(error_lines[:30])
        tail_section = "\n".join(lines[-10:])
        return f"{error_section}\n\n--- build tail ---\n{tail_section}"

    # No recognizable error lines — fall back to tail
    return "\n".join(lines[-40:])


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

    # Shared build directory: created once, used by L1 (compile) and L2 (runtime),
    # cleaned up after all layers complete.
    build_dir: Path | None = None
    if _get_build_mode() != "skip" and (case_dir / "CMakeLists.txt").is_file():
        build_dir = _prepare_build_dir(case_dir, generated_code)

    try:
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
            build_dir=build_dir,
        )
        # Calculate weighted score for the layer
        details = layer_result.details
        total_weight = sum(d.weight for d in details)
        earned_weight = sum(d.weight for d in details if d.passed)
        layer_score = earned_weight / total_weight if total_weight > 0 else 1.0

        layer_result = LayerResult(
            layer=layer_num,
            name=layer_name,
            passed=layer_result.passed,
            details=details,
            error=layer_result.error,
            duration_seconds=time.monotonic() - layer_start,
            score=layer_score,
        )
        layers.append(layer_result)

        if not layer_result.passed and layer_num < 4:
            # L4 (mutation meta-verification) failures don't cascade or
            # affect overall pass/fail — they test benchmark quality, not
            # LLM quality.
            failed_at_layer = layer_num
            logger.info("Layer %d (%s) failed", layer_num, layer_name)

    finally:
        if build_dir is not None:
            shutil.rmtree(build_dir, ignore_errors=True)

    elapsed = time.monotonic() - start
    all_passed = failed_at_layer is None

    scored_layers = [ly for ly in layers if ly.details and ly.layer != 4]
    total_score = (
        sum(ly.score for ly in scored_layers) / len(scored_layers)
        if scored_layers
        else 1.0
    )

    return EvalResult(
        case_id=case_dir.name,
        category=category,
        model=model,
        attempt=attempt,
        generated_code=generated_code,
        layers=layers,
        failed_at_layer=failed_at_layer,
        passed=all_passed,
        total_score=total_score,
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
    build_dir: Path | None = None,
) -> LayerResult:
    """Execute a single evaluation layer."""
    if layer_num == 0:
        return _run_static_checks(case_dir, generated_code)
    elif layer_num == 1:
        return _run_compile_gate(case_dir, generated_code, timeout, build_dir)
    elif layer_num == 2:
        is_esp = _is_esp_idf_case(case_dir)
        is_stm32 = _is_stm32_case(case_dir)
        if is_esp or is_stm32:
            platform = "ESP-IDF" if is_esp else "STM32"
            return LayerResult(
                layer=2,
                name="runtime_execution",
                passed=True,
                details=[
                    CheckDetail(
                        check_name="runtime_skip",
                        passed=True,
                        expected="runtime execution",
                        actual=f"skipped ({platform} QEMU not configured)",
                        check_type="environment",
                    )
                ],
                error=None,
                duration_seconds=0.0,
            )
        return _run_runtime(case_dir, generated_code, timeout, build_dir)
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
    case_dir: Path, generated_code: str, timeout: float,
    build_dir: Path | None = None,
) -> LayerResult:
    """Layer 1: Compile gate — dispatches to ESP-IDF, STM32, or Zephyr path."""
    if _is_esp_idf_case(case_dir):
        return _run_compile_esp_idf(case_dir, generated_code, timeout)

    if _is_stm32_case(case_dir):
        return _run_compile_stm32(case_dir, generated_code, timeout)

    build_mode = _get_build_mode()

    # Cases without CMakeLists.txt are not compilable (kconfig, device-tree, etc.)
    if not (case_dir / "CMakeLists.txt").is_file():
        logger.info(
            "No CMakeLists.txt in %s, skipping compile gate (pass)",
            case_dir.name,
        )
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=True,
            details=[
                CheckDetail(
                    check_name="build_env",
                    passed=True,
                    expected="CMakeLists.txt present",
                    actual="skipped (not a compilable case)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    if build_mode == "skip":
        logger.info("Build disabled, skipping compile gate (pass)")
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=True,
            details=[
                CheckDetail(
                    check_name="build_env",
                    passed=True,
                    expected="EMBEDEVAL_ENABLE_BUILD set",
                    actual="skipped (build not enabled)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    if build_mode == "docker":
        return _run_compile_docker(case_dir, generated_code, timeout, build_dir)

    return _run_compile_local(case_dir, generated_code, timeout, build_dir)


def _prepare_build_dir(case_dir: Path, generated_code: str) -> Path:
    """Prepare a temporary build directory with case files + generated code.

    Copies CMakeLists.txt, prj.conf, and any overlay files from the case
    directory, then writes generated_code to src/main.c. Returns the tmpdir path.
    The caller is responsible for cleanup (use as context manager or explicit delete).
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="embedeval_build_"))

    # Copy build system files
    for name in ("CMakeLists.txt", "prj.conf"):
        src = case_dir / name
        if src.is_file():
            shutil.copy2(src, tmpdir / name)

    # Copy overlay files (*.overlay, *.conf, boards/)
    for pattern in ("*.overlay", "*.conf"):
        for f in case_dir.glob(pattern):
            if f.name not in ("prj.conf",):  # already copied
                shutil.copy2(f, tmpdir / f.name)
    boards_dir = case_dir / "boards"
    if boards_dir.is_dir():
        shutil.copytree(boards_dir, tmpdir / "boards")

    # Write generated code
    src_dir = tmpdir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "main.c").write_text(generated_code, encoding="utf-8")

    return tmpdir


def _run_compile_docker(
    case_dir: Path, generated_code: str, timeout: float,
    build_dir: Path | None = None,
) -> LayerResult:
    """Run west build inside Docker container.

    Uses shared build_dir from evaluate() if provided, otherwise creates
    a temporary one (legacy path for direct calls).
    """
    board = _get_build_board(case_dir)
    own_build_dir = build_dir is None
    if own_build_dir:
        build_dir = _prepare_build_dir(case_dir, generated_code)

    try:
        start = time.monotonic()
        cmd = [
            "docker", "run", "--rm",
            "--entrypoint", "",
            "-v", f"{build_dir}:/workspace",
            "-w", "/workspace",
            _get_docker_image(),
            "west", "build", "-b", board, "/workspace",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - start
        passed = result.returncode == 0

        error_output = ""
        if not passed:
            error_output = _extract_build_errors(
                result.stdout or "", result.stderr or ""
            )

        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=passed,
            details=[
                CheckDetail(
                    check_name="west_build_docker",
                    passed=passed,
                    expected="exit code 0",
                    actual=f"exit code {result.returncode}",
                    check_type="compile",
                )
            ],
            error=error_output[:4000] if not passed else None,
            duration_seconds=elapsed,
        )
    except subprocess.TimeoutExpired:
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=False,
            details=[],
            error=f"Docker build timed out after {timeout}s",
            duration_seconds=timeout,
        )
    finally:
        if own_build_dir:
            shutil.rmtree(build_dir, ignore_errors=True)


def _run_compile_local(
    case_dir: Path, generated_code: str, timeout: float,
    build_dir: Path | None = None,
) -> LayerResult:
    """Run west build locally (requires ZEPHYR_BASE)."""
    board = _get_build_board(case_dir)
    own_build_dir = build_dir is None
    if own_build_dir:
        build_dir = _prepare_build_dir(case_dir, generated_code)

    try:
        start = time.monotonic()
        result = subprocess.run(
            ["west", "build", "-b", board, str(build_dir)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(build_dir),
        )
        elapsed = time.monotonic() - start
        passed = result.returncode == 0
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=passed,
            details=[
                CheckDetail(
                    check_name="west_build",
                    passed=passed,
                    expected="exit code 0",
                    actual=f"exit code {result.returncode}",
                    check_type="compile",
                )
            ],
            error=(
                _extract_build_errors(
                    result.stdout or "", result.stderr or ""
                )[:4000]
                if not passed
                else None
            ),
            duration_seconds=elapsed,
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
    finally:
        if own_build_dir:
            shutil.rmtree(build_dir, ignore_errors=True)


def _run_runtime(
    case_dir: Path, generated_code: str, timeout: float,
    build_dir: Path | None = None,
) -> LayerResult:
    """Layer 2: Runtime execution.

    For Docker mode: runs `west build -t run` inside Docker using the shared
    build_dir (which already has L1 build artifacts).
    For local mode: runs `west build -t run` on the host.

    Only native_sim board target supports runtime execution. HW targets
    (nrf52840dk, etc.) are skipped since they need physical hardware.
    """
    if not (case_dir / "CMakeLists.txt").is_file():
        logger.info("No CMakeLists.txt, skipping runtime execution (pass)")
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=True,
            details=[
                CheckDetail(
                    check_name="build_env",
                    passed=True,
                    expected="CMakeLists.txt present",
                    actual="skipped (not a compilable case)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    if not _build_env_available():
        logger.info("Build not available, skipping runtime execution (pass)")
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=True,
            details=[
                CheckDetail(
                    check_name="build_env",
                    passed=True,
                    expected="build environment available",
                    actual="skipped (build not enabled)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    # Only native_sim can be executed without hardware
    board = _get_build_board(case_dir)
    if board != "native_sim":
        logger.info("Board %s requires hardware, skipping runtime (pass)", board)
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=True,
            details=[
                CheckDetail(
                    check_name="runtime_skip",
                    passed=True,
                    expected="runtime execution",
                    actual=f"skipped (board {board} requires hardware)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    build_mode = _get_build_mode()

    if build_dir is None:
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=True,
            details=[
                CheckDetail(
                    check_name="runtime_skip",
                    passed=True,
                    expected="runtime execution",
                    actual="skipped (no build artifacts from L1)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    if build_mode == "docker":
        cmd = [
            "docker", "run", "--rm",
            "--entrypoint", "",
            "-v", f"{build_dir}:/workspace",
            "-w", "/workspace",
            _get_docker_image(),
            "west", "build", "-t", "run",
        ]
        cwd = None
    else:
        cmd = ["west", "build", "-t", "run"]
        cwd = str(build_dir)

    # Embedded firmware runs forever (while(1) loops). We run for a short
    # window, capture whatever output appears, then kill the process.
    # Success = process started + expected output keywords found.
    rt_timeout = RUNTIME_TIMEOUT
    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=rt_timeout,
            cwd=cwd,
        )
        # Process exited on its own — check exit code
        elapsed = time.monotonic() - start
        stdout = result.stdout + result.stderr
        exited_ok = result.returncode == 0
    except subprocess.TimeoutExpired as exc:
        # Expected: firmware runs forever, we killed it after rt_timeout
        elapsed = time.monotonic() - start
        stdout = (exc.stdout or b"").decode(errors="replace") + \
                 (exc.stderr or b"").decode(errors="replace")
        exited_ok = True  # timeout is normal for embedded firmware

    details: list[CheckDetail] = [
        CheckDetail(
            check_name="runtime_started",
            passed=exited_ok,
            expected="process started successfully",
            actual=f"ran for {elapsed:.1f}s",
            check_type="runtime",
        )
    ]

    # Validate output against expected_output.txt
    expected_file = case_dir / "checks" / "expected_output.txt"
    if expected_file.exists() and exited_ok:
        expected_keywords = [
            kw.strip()
            for kw in expected_file.read_text(encoding="utf-8").strip().splitlines()
            if kw.strip()
        ]
        missing = [kw for kw in expected_keywords if kw not in stdout]
        output_passed = len(missing) == 0
        details.append(
            CheckDetail(
                check_name="output_validation",
                passed=output_passed,
                expected=f"Keywords: {expected_keywords}",
                actual="all found" if output_passed else f"Missing: {missing}",
                check_type="runtime",
            )
        )
        passed = exited_ok and output_passed
    else:
        # No expected_output.txt — pass if process started OK
        passed = exited_ok

    return LayerResult(
        layer=2,
        name="runtime_execution",
        passed=passed,
        details=details,
        error=stdout[-4000:] if not passed else None,
        duration_seconds=elapsed,
    )


def _run_behavioral(case_dir: Path, generated_code: str) -> LayerResult:
    """Layer 3: Behavioral assertion checks from case checks/behavior.py."""
    checks_module = _load_check_module(case_dir, "behavior")
    if checks_module is None:
        return LayerResult(
            layer=3,
            name="static_heuristic",
            passed=True,
            details=[],
            error=None,
            duration_seconds=0.0,
        )

    return _execute_check_module(
        checks_module, generated_code, layer=3, name="static_heuristic"
    )


def _run_mutant_checks(case_dir: Path, generated_code: str) -> LayerResult:
    """Layer 4: Mutation meta-verification.

    Loads negatives.py NEGATIVES data, applies each must_fail mutation to
    the generated code, and verifies that L0/L3 checks detect the seeded bug.
    This tests benchmark check quality, not LLM quality — L4 failures do not
    affect the overall case pass/fail determination.
    """
    start = time.monotonic()
    negatives = _load_negatives(case_dir)
    if negatives is None:
        return LayerResult(
            layer=4,
            name="test_quality_proof",
            passed=True,
            details=[],
            error=None,
            duration_seconds=0.0,
        )

    details: list[CheckDetail] = []
    for neg in negatives:
        if "must_fail" not in neg:
            continue

        name = neg.get("name", "unknown")
        try:
            mutated_code = neg["mutation"](generated_code)
        except Exception as exc:
            logger.debug("Mutation '%s' raised: %s", name, exc)
            details.append(CheckDetail(
                check_name=f"mutation_{name}",
                passed=True,
                expected="mutation applied",
                actual=f"skipped (mutation error: {exc})",
                check_type="mutation",
            ))
            continue

        if mutated_code == generated_code:
            details.append(CheckDetail(
                check_name=f"mutation_{name}",
                passed=True,
                expected="mutation applied",
                actual="skipped (code unchanged by mutation)",
                check_type="mutation",
            ))
            continue

        # Run L0 + L3 checks on the mutated code
        all_check_details: list[CheckDetail] = []
        static_result = _run_static_checks(case_dir, mutated_code)
        all_check_details.extend(static_result.details)
        behavior_result = _run_behavioral(case_dir, mutated_code)
        all_check_details.extend(behavior_result.details)

        # Verify that must_fail checks actually fail on mutated code
        all_caught = True
        missed: list[str] = []
        for check_name in neg["must_fail"]:
            matching = [d for d in all_check_details if d.check_name == check_name]
            if not matching or any(d.passed for d in matching):
                all_caught = False
                missed.append(check_name)

        details.append(CheckDetail(
            check_name=f"mutation_{name}",
            passed=all_caught,
            expected=f"checks {neg['must_fail']} detect mutation",
            actual="caught" if all_caught else f"missed: {missed}",
            check_type="mutation",
        ))

    elapsed = time.monotonic() - start
    all_passed = all(d.passed for d in details) if details else True
    return LayerResult(
        layer=4,
        name="test_quality_proof",
        passed=all_passed,
        details=details,
        error=None,
        duration_seconds=elapsed,
    )


def _load_negatives(case_dir: Path) -> list[dict[str, Any]] | None:
    """Load NEGATIVES mutation data from checks/negatives.py."""
    module = _load_check_module(case_dir, "negatives")
    if module is None:
        return None
    negatives: list[dict[str, Any]] | None = getattr(module, "NEGATIVES", None)
    if not negatives:
        return None
    return negatives


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


def _get_build_mode() -> str:
    """Return the build mode: 'docker', 'local', or 'skip'.

    EMBEDEVAL_ENABLE_BUILD values:
    - 'docker': Run west build inside Docker container (embedeval-zephyr image)
    - '1' or 'local': Run west build locally (requires ZEPHYR_BASE)
    - unset or other: Skip compilation (auto-pass)
    """
    val = os.environ.get("EMBEDEVAL_ENABLE_BUILD", "").lower()
    if val == "docker":
        return "docker"
    if val in ("1", "local"):
        return "local"
    return "skip"


def _build_env_available() -> bool:
    """Check if Zephyr build environment is ready for compilation."""
    return _get_build_mode() != "skip"


def _get_docker_image() -> str:
    """Return Docker image name for Zephyr compilation."""
    return os.environ.get("EMBEDEVAL_DOCKER_IMAGE", "embedeval-zephyr:latest")


def _get_build_board(case_dir: Path) -> str:
    """Read build_board from metadata.yaml, default to native_sim."""
    metadata_path = case_dir / "metadata.yaml"
    if metadata_path.is_file():
        for line in metadata_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("build_board:"):
                board = line.split(":", 1)[1].strip()
                if board:
                    return board
    return "native_sim"


def _esp_idf_env_available() -> bool:
    """Check if ESP-IDF build environment is available."""
    return (
        os.environ.get("IDF_PATH") is not None
        and _get_build_mode() != "skip"
    )


def _is_esp_idf_case(case_dir: Path) -> bool:
    """Return True if this case targets ESP-IDF rather than Zephyr.

    Detection strategy (first match wins):
    1. metadata.yaml contains ``platform: esp_idf``
    2. case directory contains an ``sdkconfig.defaults`` file
    """
    # Check metadata.yaml for explicit platform declaration
    metadata_path = case_dir / "metadata.yaml"
    if metadata_path.is_file():
        content = metadata_path.read_text(encoding="utf-8")
        if "platform: esp_idf" in content:
            return True

    # Fall back to presence of sdkconfig.defaults (ESP-IDF project marker)
    return (case_dir / "sdkconfig.defaults").is_file()


def _run_compile_esp_idf(
    case_dir: Path, generated_code: str, timeout: float
) -> LayerResult:
    """Layer 1: ESP-IDF compilation via idf.py build."""
    if not _esp_idf_env_available():
        logger.info("ESP-IDF not available, skipping compile gate (pass)")
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=True,
            details=[
                CheckDetail(
                    check_name="esp_idf_available",
                    passed=True,
                    expected="IDF_PATH set",
                    actual="skipped (ESP-IDF not available)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    src_file = case_dir / "main" / "main.c"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text(generated_code, encoding="utf-8")

    try:
        result = subprocess.run(
            ["idf.py", "build"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(case_dir),
        )
        passed = result.returncode == 0
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=passed,
            details=[
                CheckDetail(
                    check_name="idf_build",
                    passed=passed,
                    expected="exit code 0",
                    actual=f"exit code {result.returncode}",
                    check_type="compile",
                )
            ],
            error=result.stderr if not passed else None,
            duration_seconds=0.0,
        )
    except subprocess.TimeoutExpired:
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=False,
            details=[],
            error=f"ESP-IDF build timed out after {timeout}s",
            duration_seconds=timeout,
        )


def _is_stm32_case(case_dir: Path) -> bool:
    """Return True if this case targets STM32 HAL."""
    metadata_path = case_dir / "metadata.yaml"
    if metadata_path.is_file():
        content = metadata_path.read_text(encoding="utf-8")
        if "platform: stm32_hal" in content:
            return True
    return False


def _stm32_env_available() -> bool:
    """Check if STM32 build environment is available."""
    return (
        os.environ.get("STM32_HAL_PATH") is not None
        and _get_build_mode() != "skip"
    )


def _run_compile_stm32(
    case_dir: Path, generated_code: str, timeout: float
) -> LayerResult:
    """Layer 1: STM32 HAL compilation via arm-none-eabi-gcc."""
    if not _stm32_env_available():
        logger.info("STM32 toolchain not available, skipping compile gate (pass)")
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=True,
            details=[
                CheckDetail(
                    check_name="stm32_available",
                    passed=True,
                    expected="STM32_HAL_PATH set",
                    actual="skipped (STM32 toolchain not available)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    hal_path = os.environ["STM32_HAL_PATH"]

    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = Path(tmpdir) / "main.c"
        src_file.write_text(generated_code, encoding="utf-8")

        cmd = [
            "arm-none-eabi-gcc",
            "-c",
            "-mcpu=cortex-m4",
            "-mthumb",
            "-DSTM32F407xx",
            "-DUSE_HAL_DRIVER",
            f"-I{hal_path}/CMSIS/Include",
            f"-I{hal_path}/CMSIS/Device/ST/STM32F4xx/Include",
            f"-I{hal_path}/HAL_Driver/Inc",
            "-Wall",
            "-o", "/dev/null",
            str(src_file),
        ]

        try:
            start = time.monotonic()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
            )
            elapsed = time.monotonic() - start
            passed = result.returncode == 0
            return LayerResult(
                layer=1,
                name="compile_gate",
                passed=passed,
                details=[
                    CheckDetail(
                        check_name="stm32_gcc",
                        passed=passed,
                        expected="exit code 0",
                        actual=f"exit code {result.returncode}",
                        check_type="compile",
                    )
                ],
                error=result.stderr if not passed else None,
                duration_seconds=elapsed,
            )
        except subprocess.TimeoutExpired:
            return LayerResult(
                layer=1,
                name="compile_gate",
                passed=False,
                details=[],
                error=f"STM32 build timed out after {timeout}s",
                duration_seconds=timeout,
            )
