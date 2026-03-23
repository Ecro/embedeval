"""Behavioral checks for DMA with cache coherency."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA cache coherency behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Cache flush on source before DMA start
    flush_pos = generated_code.find("sys_cache_data_flush_range")
    start_pos = generated_code.find("dma_start(")
    flush_before_start = (
        flush_pos != -1
        and start_pos != -1
        and flush_pos < start_pos
    )
    details.append(
        CheckDetail(
            check_name="flush_before_dma_start",
            passed=flush_before_start,
            expected="sys_cache_data_flush_range() called before dma_start()",
            actual="correct order" if flush_before_start else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Cache invalidate on destination before DMA start (pre-invalidate)
    # Find the FIRST occurrence of invd_range; it should appear before dma_start
    invd_pos_first = generated_code.find("sys_cache_data_invd_range")
    pre_invd_ok = (
        invd_pos_first != -1
        and start_pos != -1
        and invd_pos_first < start_pos
    )
    details.append(
        CheckDetail(
            check_name="pre_invalidate_dst_before_dma",
            passed=pre_invd_ok,
            expected="sys_cache_data_invd_range() on dst before dma_start() to clear stale lines",
            actual="correct order" if pre_invd_ok else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 3: Cache invalidate on destination AFTER DMA completes (post-invalidate)
    # There should be a second invd_range call after the semaphore take
    sem_take_pos = generated_code.find("k_sem_take")
    invd_pos_second = generated_code.rfind("sys_cache_data_invd_range")
    post_invd_ok = (
        invd_pos_second != -1
        and sem_take_pos != -1
        and invd_pos_second > sem_take_pos
    )
    details.append(
        CheckDetail(
            check_name="post_invalidate_dst_after_dma",
            passed=post_invd_ok,
            expected="sys_cache_data_invd_range() on dst after DMA completion for CPU read",
            actual="correct order" if post_invd_ok else "missing or wrong order - CPU may read stale data",
            check_type="constraint",
        )
    )

    # Check 4: dma_config before dma_start
    config_pos = generated_code.find("dma_config(")
    order_ok = config_pos != -1 and start_pos != -1 and config_pos < start_pos
    details.append(
        CheckDetail(
            check_name="config_before_start",
            passed=order_ok,
            expected="dma_config() called before dma_start()",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 5: Buffer alignment specified for destination
    has_aligned = "__aligned" in generated_code
    details.append(
        CheckDetail(
            check_name="dst_buffer_cache_line_aligned",
            passed=has_aligned,
            expected="Destination buffer aligned to cache line size with __aligned()",
            actual="present" if has_aligned else "missing - unaligned buffer may cause partial cache line issues",
            check_type="constraint",
        )
    )

    # Check 6: Completion synchronization and verification
    has_sync = "k_sem_take" in generated_code
    has_verify = "memcmp" in generated_code or "DMA verify" in generated_code or "DMA OK" in generated_code
    details.append(
        CheckDetail(
            check_name="sync_and_verify",
            passed=has_sync and has_verify,
            expected="Completion semaphore wait and memcmp verification",
            actual=f"sync={has_sync}, verify={has_verify}",
            check_type="constraint",
        )
    )

    return details
