"""Behavioral checks for DMA circular buffer."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA circular buffer behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: dma_reload() called inside the callback
    # Heuristic: dma_reload appears in the same function scope as the callback signature
    callback_pos = generated_code.find("dma_callback")
    reload_pos = generated_code.find("dma_reload")
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
        "cyclic = 1" in generated_code
        or "cyclic=1" in generated_code
        or ".cyclic = 1" in generated_code
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
        ("buf_a" in generated_code and "buf_b" in generated_code)
        or ("ping" in generated_code and "pong" in generated_code)
        or generated_code.count("dst_buf") >= 2
        or ("buf[0]" in generated_code and "buf[1]" in generated_code)
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
    has_stop = "dma_stop" in generated_code
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
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_error_handling",
            passed=has_error_check,
            expected="Error checking on DMA API return values",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    return details
