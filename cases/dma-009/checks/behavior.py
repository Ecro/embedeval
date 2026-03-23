"""Behavioral checks for DMA linked list multi-block with stop condition."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA linked list behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Three separate source buffers defined
    has_src0 = "src0" in generated_code or "src_0" in generated_code
    has_src1 = "src1" in generated_code or "src_1" in generated_code
    has_src2 = "src2" in generated_code or "src_2" in generated_code
    three_src_bufs = has_src0 and has_src1 and has_src2
    details.append(
        CheckDetail(
            check_name="three_source_buffers_defined",
            passed=three_src_bufs,
            expected="Three source buffers (src0, src1, src2) defined",
            actual=f"src0={has_src0}, src1={has_src1}, src2={has_src2}",
            check_type="constraint",
        )
    )

    # Check 2: Three separate destination buffers defined
    has_dst0 = "dst0" in generated_code or "dst_0" in generated_code
    has_dst1 = "dst1" in generated_code or "dst_1" in generated_code
    has_dst2 = "dst2" in generated_code or "dst_2" in generated_code
    three_dst_bufs = has_dst0 and has_dst1 and has_dst2
    details.append(
        CheckDetail(
            check_name="three_destination_buffers_defined",
            passed=three_dst_bufs,
            expected="Three destination buffers (dst0, dst1, dst2) defined",
            actual=f"dst0={has_dst0}, dst1={has_dst1}, dst2={has_dst2}",
            check_type="constraint",
        )
    )

    # Check 3: Last block terminates with NULL (not circular)
    last_block_null = bool(re.search(r"next_block\s*=\s*NULL", generated_code))
    details.append(
        CheckDetail(
            check_name="last_block_terminates_with_null",
            passed=last_block_null,
            expected="Last DMA block next_block = NULL (no circular wrap-around)",
            actual="correct" if last_block_null else "missing NULL terminator — may loop or corrupt",
            check_type="constraint",
        )
    )

    # Check 4: block_count matches actual blocks (= 3)
    has_block_count_3 = bool(re.search(r"block_count\s*=\s*3", generated_code))
    details.append(
        CheckDetail(
            check_name="block_count_matches_actual_blocks",
            passed=has_block_count_3,
            expected="block_count set to 3 matching actual number of blocks",
            actual="correct" if has_block_count_3 else "block_count mismatch",
            check_type="constraint",
        )
    )

    # Check 5: All three dst buffers verified after DMA
    verify_count = generated_code.count("memcmp")
    has_verification = verify_count >= 1 or "Multi-block DMA OK" in generated_code
    details.append(
        CheckDetail(
            check_name="all_blocks_verified",
            passed=has_verification,
            expected="All destination buffers verified after DMA completion",
            actual=f"memcmp calls={verify_count}" if verify_count else "no verification found",
            check_type="constraint",
        )
    )

    return details
