"""Static checks for dma-011: scatter-gather linked block descriptors."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    has_dma_h = "drivers/dma.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_header_included",
            passed=has_dma_h,
            expected="zephyr/drivers/dma.h included",
            actual="present" if has_dma_h else "missing",
            check_type="exact_match",
        )
    )

    # Count block_config declarations — need at least 3
    block_cfg_count = len(
        re.findall(
            r"struct\s+dma_block_config\s+\w+",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="three_block_configs",
            passed=block_cfg_count >= 3,
            expected=">=3 dma_block_config structs (one per scatter entry)",
            actual=f"found {block_cfg_count}",
            check_type="constraint",
        )
    )

    # Linked list via next_block assignments
    next_block_links = len(re.findall(r"\.next_block\s*=\s*&\w+", generated_code))
    details.append(
        CheckDetail(
            check_name="blocks_linked",
            passed=next_block_links >= 2,
            expected=">=2 next_block links (chain of 3 descriptors)",
            actual=f"{next_block_links} link assignment(s)",
            check_type="constraint",
        )
    )

    # Exactly one dma_start call — single scatter-gather request
    start_count = len(re.findall(r"\bdma_start\s*\(", generated_code))
    details.append(
        CheckDetail(
            check_name="single_dma_start",
            passed=start_count == 1,
            expected="Exactly one dma_start() call (not three separate transfers)",
            actual=f"{start_count} dma_start call(s)",
            check_type="constraint",
        )
    )

    # block_count in dma_config should be 3
    has_block_count_3 = bool(
        re.search(
            r"\.block_count\s*=\s*3",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="block_count_three",
            passed=has_block_count_3,
            expected=".block_count = 3 in dma_config",
            actual="present" if has_block_count_3 else "missing or wrong value",
            check_type="constraint",
        )
    )

    # head_block points to first descriptor
    has_head_block = bool(re.search(r"\.head_block\s*=\s*&\w+", generated_code))
    details.append(
        CheckDetail(
            check_name="head_block_set",
            passed=has_head_block,
            expected=".head_block = &first_block in dma_config",
            actual="present" if has_head_block else "missing",
            check_type="constraint",
        )
    )

    return details
