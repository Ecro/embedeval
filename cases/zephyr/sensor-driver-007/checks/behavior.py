"""Behavioral checks for sensor FIFO batch read."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor FIFO batch read behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Watermark checked BEFORE burst read
    # (LLM failure: reading a fixed number of samples without checking watermark)
    watermark_pos = find_in_code(generated_code, "watermark")
    if watermark_pos == -1:
        watermark_pos = generated_code.lower().find("watermark")
    burst_pos = find_in_code(generated_code, "burst_read")
    if burst_pos == -1:
        burst_pos = find_in_code(generated_code, "sensor_sample_fetch")
    details.append(
        CheckDetail(
            check_name="watermark_before_burst_read",
            passed=watermark_pos != -1 and burst_pos != -1 and watermark_pos < burst_pos,
            expected="Watermark read BEFORE burst/batch read loop",
            actual="correct" if (watermark_pos != -1 and burst_pos != -1 and watermark_pos < burst_pos)
                   else "missing watermark check or read without checking watermark first",
            check_type="constraint",
        )
    )

    # Check 2: Buffer declared with FIFO_MAX_DEPTH capacity (not undersized)
    # (LLM failure: declaring buffer smaller than FIFO depth, e.g., samples[8] for 32-deep FIFO)
    has_fifo_max_in_buffer = (
        scoped_contains(generated_code, 'FIFO_MAX_DEPTH', scope='code_only')
        and scoped_contains(generated_code, 'sensor_sample', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="buffer_sized_for_max_fifo",
            passed=has_fifo_max_in_buffer,
            expected="Sample buffer declared with FIFO_MAX_DEPTH capacity",
            actual="correct" if has_fifo_max_in_buffer
                   else "missing — buffer may be too small for full FIFO depth",
            check_type="constraint",
        )
    )

    # Check 3: Burst read count matches watermark count (not fixed)
    # (LLM failure: always reading FIFO_MAX_DEPTH samples regardless of watermark)
    has_dynamic_count = (
        scoped_contains(generated_code, 'count', scope='code_only')
        and scoped_contains(generated_code, 'sensor_sample_fetch', scope='code_only')
        and "watermark" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="burst_count_from_watermark",
            passed=has_dynamic_count,
            expected="Burst read count driven by watermark value, not hardcoded",
            actual="correct" if has_dynamic_count
                   else "missing — reading fixed count, ignoring actual FIFO fill level",
            check_type="constraint",
        )
    )

    # Check 4: Buffer overflow guard (count > FIFO_MAX_DEPTH rejected)
    # (LLM failure: no guard, reading past buffer end if FIFO reports > max)
    has_overflow_guard = (
        (scoped_contains(generated_code, 'count > ', scope='code_only') or scoped_contains(generated_code, 'count >= ', scope='code_only'))
        and scoped_contains(generated_code, 'FIFO_MAX_DEPTH', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="overflow_guard_active",
            passed=has_overflow_guard,
            expected="Guard: count > FIFO_MAX_DEPTH rejected with error return",
            actual="present" if has_overflow_guard
                   else "missing — burst read can overflow the sample buffer!",
            check_type="constraint",
        )
    )

    # Check 5: device_is_ready checked before use
    has_device_ready = scoped_contains(generated_code, 'device_is_ready', scope='code_only')
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_device_ready,
            expected="device_is_ready() checked before using sensor",
            actual="present" if has_device_ready else "missing (no device readiness check)",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
