"""Static analysis checks for zero-copy DMA double buffer swap."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA double buffer code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: DMA header included
    has_dma_h = "zephyr/drivers/dma.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_header_included",
            passed=has_dma_h,
            expected="zephyr/drivers/dma.h included",
            actual="present" if has_dma_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Two separate buffers declared (buf_a and buf_b or similar)
    has_buf_a = "buf_a" in generated_code or "buffer_a" in generated_code or "ping" in generated_code
    has_buf_b = "buf_b" in generated_code or "buffer_b" in generated_code or "pong" in generated_code
    has_two_bufs = has_buf_a and has_buf_b
    details.append(
        CheckDetail(
            check_name="two_separate_dma_buffers",
            passed=has_two_bufs,
            expected="Two separate DMA buffers (buf_a and buf_b) declared",
            actual=f"buf_a={has_buf_a}, buf_b={has_buf_b}",
            check_type="exact_match",
        )
    )

    # Check 3: atomic variable used for buffer index
    has_atomic = "atomic_t" in generated_code or "atomic_set" in generated_code or "atomic_get" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_buffer_index",
            passed=has_atomic,
            expected="atomic_t or atomic operations used for buffer index swap",
            actual="present" if has_atomic else "missing — non-atomic swap may cause race condition",
            check_type="exact_match",
        )
    )

    # Check 4: dma_reload called
    has_dma_reload = "dma_reload" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_reload_called",
            passed=has_dma_reload,
            expected="dma_reload() called to reload DMA with next buffer",
            actual="present" if has_dma_reload else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: dma_config and dma_start present
    has_dma_api = "dma_config" in generated_code and "dma_start" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_config_and_start_present",
            passed=has_dma_api,
            expected="dma_config() and dma_start() called",
            actual="present" if has_dma_api else "missing one or both DMA calls",
            check_type="exact_match",
        )
    )

    return details
