"""Behavioral checks for DMA circular buffer."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA circular buffer behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: dma_reload() called inside the callback
    # Heuristic: dma_reload appears in the same function scope as the callback signature
    callback_pos = find_in_code(generated_code, "dma_callback")
    reload_pos = find_in_code(generated_code, "dma_reload")
    reload_in_callback = (
        callback_pos != -1
        and reload_pos != -1
        and reload_pos > callback_pos
    )
    details.append(
        CheckDetail(
            check_name="reload_in_callback",
            passed=reload_in_callback,
            expected="dma_reload() called from within DMA callback",
            actual="correct" if reload_in_callback else "missing or outside callback",
            check_type="constraint",
        )
    )

    # Check 2: cyclic flag set to 1
    has_cyclic_one = (
        scoped_contains(generated_code, 'cyclic = 1', scope='code_only')
        or scoped_contains(generated_code, 'cyclic=1', scope='code_only')
        or scoped_contains(generated_code, '.cyclic = 1', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="cyclic_enabled",
            passed=has_cyclic_one,
            expected="cyclic = 1 set in dma_block_config",
            actual="present" if has_cyclic_one else "missing or zero",
            check_type="constraint",
        )
    )

    # Check 3: Ping-pong or alternating buffer used (two destination buffers)
    has_two_bufs = (
        (scoped_contains(generated_code, 'buf_a', scope='code_only') and scoped_contains(generated_code, 'buf_b', scope='code_only'))
        or (scoped_contains(generated_code, 'ping', scope='code_only') and scoped_contains(generated_code, 'pong', scope='code_only'))
        or generated_code.count("dst_buf") >= 2
        or (scoped_contains(generated_code, 'buf[0]', scope='code_only') and scoped_contains(generated_code, 'buf[1]', scope='code_only'))
    )
    details.append(
        CheckDetail(
            check_name="ping_pong_buffers",
            passed=has_two_bufs,
            expected="Two alternating destination buffers (ping-pong) for circular DMA",
            actual="present" if has_two_bufs else "missing - single buffer risks overflow",
            check_type="constraint",
        )
    )

    # Check 4: dma_stop() called to terminate
    has_stop = scoped_contains(generated_code, 'dma_stop', scope='code_only')
    details.append(
        CheckDetail(
            check_name="dma_stop_called",
            passed=has_stop,
            expected="dma_stop() called to terminate circular DMA",
            actual="present" if has_stop else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Error handling on dma_config / dma_start
    has_error_check = scoped_contains(generated_code, '< 0', scope='code_only') or scoped_contains(generated_code, '!= 0', scope='code_only')
    details.append(
        CheckDetail(
            check_name="dma_error_handling",
            passed=has_error_check,
            expected="Error checking on DMA API return values",
            actual="present" if has_error_check else "missing",
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
