"""Layer L1 (compile) and L2 (runtime) execution.

subprocess and the build-mode/env helpers are reached through the facade
package (``_ev``) so test patches of ``embedeval.evaluator.subprocess`` /
``embedeval.evaluator._get_build_mode`` etc. take effect at call time.
"""

import logging
import os
import shutil
import tempfile
import time
from pathlib import Path

from embedeval import evaluator as _ev
from embedeval.evaluator.support import (
    _extract_build_errors,
    _get_build_board,
    _get_docker_image,
    _is_esp_idf_case,
    _is_l1_skipped,
    _is_l2_skipped,
    _is_nxp_case,
    _is_stm32_case,
    _nxp_env_available,
    _stm32_env_available,
)
from embedeval.models import CheckDetail, LayerResult

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300.0
# Embedded firmware runs forever (while(1) + k_sleep). L2 captures output
# for a short window, then kills the process and validates what was printed.
RUNTIME_TIMEOUT = 10.0


def _run_compile_gate(
    case_dir: Path,
    generated_code: str,
    timeout: float,
    build_dir: Path | None = None,
) -> LayerResult:
    """Layer 1: Compile gate — dispatches to ESP-IDF, STM32, or Zephyr path."""
    if _is_esp_idf_case(case_dir):
        return _run_compile_esp_idf(case_dir, generated_code, timeout)

    if _is_nxp_case(case_dir):
        return _run_compile_nxp(case_dir, generated_code, timeout)

    if _is_stm32_case(case_dir):
        return _run_compile_stm32(case_dir, generated_code, timeout)

    build_mode = _ev._get_build_mode()

    # Cases with l1_skip: reference solution doesn't compile for target board
    if _is_l1_skipped(case_dir):
        logger.info(
            "l1_skip set in %s, skipping compile gate (pass)",
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
                    expected="l1_skip not set",
                    actual=(
                        "skipped (l1_skip: reference does not compile for target board)"
                    ),
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

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
    case_dir: Path,
    generated_code: str,
    timeout: float,
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
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "",
            "-v",
            f"{build_dir}:/workspace",
            "-w",
            "/workspace",
            _get_docker_image(),
            "west",
            "build",
            "-b",
            board,
            "/workspace",
        ]
        result = _ev.subprocess.run(
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
    except _ev.subprocess.TimeoutExpired:
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
            assert build_dir is not None
            shutil.rmtree(build_dir, ignore_errors=True)


def _run_compile_local(
    case_dir: Path,
    generated_code: str,
    timeout: float,
    build_dir: Path | None = None,
) -> LayerResult:
    """Run west build locally (requires ZEPHYR_BASE)."""
    board = _get_build_board(case_dir)
    own_build_dir = build_dir is None
    if own_build_dir:
        build_dir = _prepare_build_dir(case_dir, generated_code)

    try:
        start = time.monotonic()
        result = _ev.subprocess.run(
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
                _extract_build_errors(result.stdout or "", result.stderr or "")[:4000]
                if not passed
                else None
            ),
            duration_seconds=elapsed,
        )
    except _ev.subprocess.TimeoutExpired:
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
            assert build_dir is not None
            shutil.rmtree(build_dir, ignore_errors=True)




def _run_runtime(
    case_dir: Path,
    generated_code: str,
    timeout: float,
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

    if _is_l1_skipped(case_dir):
        logger.info("l1_skip set, skipping runtime execution (pass)")
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=True,
            details=[
                CheckDetail(
                    check_name="build_env",
                    passed=True,
                    expected="l1_skip not set",
                    actual="skipped (l1_skip: reference does not compile)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    if _is_l2_skipped(case_dir):
        logger.info("l2_skip set, skipping runtime execution (pass)")
        return LayerResult(
            layer=2,
            name="runtime_execution",
            passed=True,
            details=[
                CheckDetail(
                    check_name="runtime_skip",
                    passed=True,
                    expected="l2_skip not set",
                    actual="skipped (l2_skip: peripheral unavailable on native_sim)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    if not _ev._build_env_available():
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

    build_mode = _ev._get_build_mode()

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
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "",
            "-v",
            f"{build_dir}:/workspace",
            "-w",
            "/workspace",
            _get_docker_image(),
            "west",
            "build",
            "-t",
            "run",
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
        result = _ev.subprocess.run(
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
    except _ev.subprocess.TimeoutExpired as exc:
        # Expected: firmware runs forever, we killed it after rt_timeout
        elapsed = time.monotonic() - start
        stdout = (exc.stdout or b"").decode(errors="replace") + (
            exc.stderr or b""
        ).decode(errors="replace")
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




def _run_compile_esp_idf(
    case_dir: Path, generated_code: str, timeout: float
) -> LayerResult:
    """Layer 1: ESP-IDF compilation via idf.py build."""
    if not _ev._esp_idf_env_available():
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
        result = _ev.subprocess.run(
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
    except _ev.subprocess.TimeoutExpired:
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=False,
            details=[],
            error=f"ESP-IDF build timed out after {timeout}s",
            duration_seconds=timeout,
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
            "-o",
            "/dev/null",
            str(src_file),
        ]

        try:
            start = time.monotonic()
            result = _ev.subprocess.run(
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
        except _ev.subprocess.TimeoutExpired:
            return LayerResult(
                layer=1,
                name="compile_gate",
                passed=False,
                details=[],
                error=f"STM32 build timed out after {timeout}s",
                duration_seconds=timeout,
            )


# Per-family compile settings for NXP MCUXpresso bare-metal cases.
# Include dirs are relative to NXP_SDK_PATH (root holding the cloned SDK repos).
# Family is selected by case-id prefix, not metadata: both families share
# platform: nxp_bare_metal, so only the id distinguishes MCXC144 from RT1170.
# Non-obvious paths (do not "simplify"):
#   - MCXC fsl_clock.h lives under MCXC444/drivers (MCXC144 reuses the 444 clock driver)
#   - RT GPIO is the i.MX "igpio" variant, not the Kinetis "gpio" driver
#   - RT eDMA is the legacy "edma" driver, not "edma4"
_NXP_MCXC = {
    "mcpu": "cortex-m0plus",
    "cpu_define": "CPU_MCXC144VFM",
    "includes": [
        "mcx/MCXC/MCXC144",
        "mcx/MCXC/periph2",
        "mcx/MCXC/MCXC444/drivers",
        "mcuxsdk-core/drivers/common",
        "mcuxsdk-core/drivers/port",
        "mcuxsdk-core/drivers/gpio",
        "mcuxsdk-core/drivers/uart",
        "mcuxsdk-core/drivers/pit",
        "mcuxsdk-core/drivers/i2c",
        "mcuxsdk-core/drivers/spi",
        "mcuxsdk-core/drivers/flash",
        "mcuxsdk-core/drivers/cop",
        "cmsis/CMSIS/Core/Include",
    ],
}

_NXP_RT = {
    "mcpu": "cortex-m7",
    "cpu_define": "CPU_MIMXRT1176DVMAA_cm7",
    "includes": [
        "rt/RT1170/MIMXRT1176",
        "rt/RT1170/periph",
        "rt/RT1170/MIMXRT1176/drivers",
        "mcuxsdk-core/drivers/common",
        "mcuxsdk-core/drivers/igpio",
        "mcuxsdk-core/drivers/lpi2c",
        "mcuxsdk-core/drivers/lpspi",
        "mcuxsdk-core/drivers/lpuart",
        "mcuxsdk-core/drivers/gpt",
        "mcuxsdk-core/drivers/sai",
        "mcuxsdk-core/drivers/rtwdog",
        "mcuxsdk-core/drivers/edma",
        "cmsis/CMSIS/Core/Include",
    ],
}


def _nxp_family_settings(case_dir: Path) -> dict:
    """Select MCXC144 or RT1170 compile settings from the case-id prefix."""
    case_id = case_dir.name
    if case_id.startswith("nxp-mcxc-"):
        return _NXP_MCXC
    # nxp-rt-* and nxp-rt1170-* both target the RT1170 Cortex-M7
    return _NXP_RT


def _run_compile_nxp(
    case_dir: Path, generated_code: str, timeout: float
) -> LayerResult:
    """Layer 1: NXP MCUXpresso compilation via arm-none-eabi-gcc."""
    if not _nxp_env_available():
        logger.info("NXP toolchain not available, skipping compile gate (pass)")
        return LayerResult(
            layer=1,
            name="compile_gate",
            passed=True,
            details=[
                CheckDetail(
                    check_name="nxp_available",
                    passed=True,
                    expected="NXP_SDK_PATH set",
                    actual="skipped (NXP toolchain not available)",
                    check_type="environment",
                )
            ],
            error=None,
            duration_seconds=0.0,
        )

    sdk_path = os.environ["NXP_SDK_PATH"]
    settings = _nxp_family_settings(case_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = Path(tmpdir) / "main.c"
        src_file.write_text(generated_code, encoding="utf-8")

        cmd = [
            "arm-none-eabi-gcc",
            "-c",
            f"-mcpu={settings['mcpu']}",
            "-mthumb",
            f"-D{settings['cpu_define']}",
        ]
        for rel in settings["includes"]:
            cmd.append(f"-I{sdk_path}/{rel}")
        cmd += ["-Wall", "-o", "/dev/null", str(src_file)]

        try:
            start = time.monotonic()
            result = _ev.subprocess.run(
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
                        check_name="nxp_gcc",
                        passed=passed,
                        expected="exit code 0",
                        actual=f"exit code {result.returncode}",
                        check_type="compile",
                    )
                ],
                error=result.stderr if not passed else None,
                duration_seconds=elapsed,
            )
        except _ev.subprocess.TimeoutExpired:
            return LayerResult(
                layer=1,
                name="compile_gate",
                passed=False,
                details=[],
                error=f"NXP build timed out after {timeout}s",
                duration_seconds=timeout,
            )
