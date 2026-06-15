"""Shared helpers: case metadata, build mode/env detection, error extraction.

_get_build_mode, _build_env_available and _esp_idf_env_available are patched
in tests as embedeval.evaluator.<name>; callers in build.py/pipeline.py reach
them through the facade package so those patches take effect.
"""

import logging
import os
from pathlib import Path

from embedeval.models import CaseMetadata

logger = logging.getLogger(__name__)


def _extract_build_errors(stdout: str, stderr: str) -> str:
    """Extract meaningful error lines from build output.

    Build logs can be very long. Instead of blindly truncating the tail,
    extract lines containing 'error:' or 'fatal error:' which carry the
    actual compiler diagnostics, then append the tail for context.
    """
    combined = stdout + "\n" + stderr
    lines = combined.splitlines()

    error_lines = [
        line
        for line in lines
        if any(
            marker in line.lower()
            for marker in (
                "error:",
                "fatal error:",
                "undefined reference",
                "no such file",
                "undeclared",
                "linker command failed",
            )
        )
    ]

    if error_lines:
        # Error lines first (most valuable), then tail for context
        error_section = "\n".join(error_lines[:30])
        tail_section = "\n".join(lines[-10:])
        return f"{error_section}\n\n--- build tail ---\n{tail_section}"

    # No recognizable error lines — fall back to tail
    return "\n".join(lines[-40:])




def _load_case_meta(case_dir: Path) -> CaseMetadata | None:
    """Load and cache CaseMetadata for a case directory.

    Uses the canonical Pydantic model from runner.load_case_metadata()
    so metadata parsing is consistent across all components.
    """
    from embedeval.runner import load_case_metadata

    return load_case_metadata(case_dir)


def _is_l1_skipped(case_dir: Path) -> bool:
    """Check if case has l1_skip flag (reference doesn't compile for target board).

    Cases marked l1_skip: true in metadata.yaml have reference solutions that
    cannot compile for their declared build_board. L1/L2 are skipped (auto-pass)
    so only L0 and L3 checks are evaluated.
    """
    meta = _load_case_meta(case_dir)
    return meta.l1_skip if meta is not None else False


def _is_l2_skipped(case_dir: Path) -> bool:
    """Check if case has l2_skip flag (peripheral unavailable on native_sim).

    Cases marked l2_skip: true in metadata.yaml target peripherals that
    cannot function on native_sim at runtime (e.g., BLE controller, network
    sockets). L2 is skipped (auto-pass) so only L0, L1, and L3 are evaluated.
    """
    meta = _load_case_meta(case_dir)
    return meta.l2_skip if meta is not None else False


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
    meta = _load_case_meta(case_dir)
    if meta is not None and meta.build_board:
        return meta.build_board
    return "native_sim"


def _esp_idf_env_available() -> bool:
    """Check if ESP-IDF build environment is available."""
    return os.environ.get("IDF_PATH") is not None and _get_build_mode() != "skip"




def _is_esp_idf_case(case_dir: Path) -> bool:
    """Return True if this case targets ESP-IDF rather than Zephyr.

    Detection strategy (first match wins):
    1. metadata.yaml ``platform: esp_idf``
    2. case directory contains an ``sdkconfig.defaults`` file
    """
    from embedeval.models import EvalPlatform

    meta = _load_case_meta(case_dir)
    if meta is not None and meta.platform == EvalPlatform.ESP_IDF:
        return True
    # Fall back to presence of sdkconfig.defaults (ESP-IDF project marker)
    return (case_dir / "sdkconfig.defaults").is_file()




def _is_stm32_case(case_dir: Path) -> bool:
    """Return True if this case targets STM32 HAL."""
    from embedeval.models import EvalPlatform

    meta = _load_case_meta(case_dir)
    return meta is not None and meta.platform == EvalPlatform.STM32_HAL


def _stm32_env_available() -> bool:
    """Check if STM32 build environment is available."""
    return os.environ.get("STM32_HAL_PATH") is not None and _get_build_mode() != "skip"


def _is_nxp_case(case_dir: Path) -> bool:
    """Return True if this case targets NXP MCUXpresso bare-metal."""
    from embedeval.models import EvalPlatform

    meta = _load_case_meta(case_dir)
    return meta is not None and meta.platform == EvalPlatform.NXP_BARE_METAL


def _nxp_env_available() -> bool:
    """Check if NXP build environment is available."""
    return os.environ.get("NXP_SDK_PATH") is not None and _get_build_mode() != "skip"


