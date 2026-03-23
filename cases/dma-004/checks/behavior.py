"""Behavioral checks for DMA scatter-gather multi-block transfer."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA scatter-gather behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Last block's next_block is NULL
    has_null_termination = (
        "next_block = NULL" in generated_code
        or ".next_block = NULL" in generated_code
        or "next_block = 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="null_termination_on_last_block",
            passed=has_null_termination,
            expected="Last dma_block_config has next_block = NULL",
            actual="present" if has_null_termination else "missing - chain not terminated",
            check_type="constraint",
        )
    )

    # Check 2: block_count matches number of blocks (3 in reference)
    # Detect numeric literal or constant equal to number of block descriptors
    block_struct_count = generated_code.count("dma_block_config")
    # block_struct_count includes the struct keyword usage; at least 3 struct definitions + 1 typedef = 4+
    has_matching_count = (
        "block_count" in generated_code
        and (
            "block_count = 3" in generated_code
            or "block_count=3" in generated_code
            or ".block_count = 3" in generated_code
            or "NUM_BLOCKS" in generated_code
        )
    )
    details.append(
        CheckDetail(
            check_name="block_count_matches_descriptors",
            passed=has_matching_count,
            expected="block_count set to match number of chained descriptors (3)",
            actual="correct" if has_matching_count else "missing or mismatched",
            check_type="constraint",
        )
    )

    # Check 3: Destination segments non-overlapping (offsets differ by block_size)
    # Heuristic: destination addresses contain stride increments (BLOCK_SIZE, 16, 32, etc.)
    has_stride = (
        "BLOCK_SIZE" in generated_code
        or "+ 16" in generated_code
        or "+16" in generated_code
        or "* 2" in generated_code
        or "32" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="non_overlapping_destinations",
            passed=has_stride,
            expected="Destination addresses offset by block size (non-overlapping)",
            actual="likely correct" if has_stride else "possible overlap",
            check_type="constraint",
        )
    )

    # Check 4: Completion synchronization present
    has_sync = any(
        p in generated_code
        for p in ["k_sem_take", "k_sem_give", "dma_callback", "k_poll"]
    )
    details.append(
        CheckDetail(
            check_name="completion_synchronization",
            passed=has_sync,
            expected="DMA completion synchronization present",
            actual="present" if has_sync else "missing",
            check_type="constraint",
        )
    )

    # Check 5: dma_config before dma_start
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

    # Check 6: Verification of destination content after transfer
    has_verify = (
        "memcmp" in generated_code
        or ("==" in generated_code and ("0xAA" in generated_code or "0xBB" in generated_code))
        or "verify" in generated_code.lower()
        or "OK" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="destination_verified",
            passed=has_verify,
            expected="Destination buffer content verified after scatter-gather",
            actual="present" if has_verify else "missing",
            check_type="constraint",
        )
    )

    return details
