"""Behavioral checks for DMA memory-to-memory transfer."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Source and destination buffers are separate
    # (LLM failure: using same buffer for src and dst)
    has_src = any(
        p in generated_code for p in ["src_buf", "source_buf", "src_data"]
    )
    has_dst = any(
        p in generated_code for p in ["dst_buf", "dest_buf", "dst_data"]
    )
    details.append(
        CheckDetail(
            check_name="separate_src_dst_buffers",
            passed=has_src and has_dst,
            expected="Separate source and destination buffers",
            actual=f"src={has_src}, dst={has_dst}",
            check_type="constraint",
        )
    )

    # Check 2: MEMORY_TO_MEMORY direction set
    has_m2m = "MEMORY_TO_MEMORY" in generated_code
    details.append(
        CheckDetail(
            check_name="memory_to_memory_direction",
            passed=has_m2m,
            expected="channel_direction = MEMORY_TO_MEMORY",
            actual="present" if has_m2m else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: dma_config before dma_start (correct ordering)
    config_pos = generated_code.find("dma_config(")
    start_pos = generated_code.find("dma_start(")
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

    # Check 4: Completion synchronization (semaphore, callback, or polling)
    has_sync = any(
        p in generated_code
        for p in [
            "k_sem_take",
            "k_sem_give",
            "dma_callback",
            "k_poll",
            "k_event",
        ]
    )
    details.append(
        CheckDetail(
            check_name="completion_synchronization",
            passed=has_sync,
            expected="DMA completion synchronization mechanism",
            actual="present" if has_sync else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Block size > 0 (LLM failure: zero-size transfer)
    has_block_size = "block_size" in generated_code
    details.append(
        CheckDetail(
            check_name="block_size_set",
            passed=has_block_size,
            expected="block_size configured in block config",
            actual="present" if has_block_size else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Error handling for dma_config/dma_start
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_error_handling",
            passed=has_error_check,
            expected="Error checking for DMA API return values",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 7: Device ready check
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() before DMA operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    return details
