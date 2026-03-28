"""Behavioral checks for DMA peripheral-to-memory transfer."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA peripheral-to-memory behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: PERIPHERAL_TO_MEMORY direction set (not MEMORY_TO_MEMORY)
    has_p2m = "PERIPHERAL_TO_MEMORY" in generated_code
    has_m2m_wrong = (
        "MEMORY_TO_MEMORY" in generated_code
        and "PERIPHERAL_TO_MEMORY" not in generated_code
    )
    details.append(
        CheckDetail(
            check_name="correct_dma_direction",
            passed=has_p2m and not has_m2m_wrong,
            expected="PERIPHERAL_TO_MEMORY direction, not MEMORY_TO_MEMORY",
            actual="correct" if (has_p2m and not has_m2m_wrong) else "wrong direction or missing",
            check_type="constraint",
        )
    )

    # Check 2: Source address adjustment is NO_CHANGE (peripheral register is fixed)
    has_no_change = bool(re.search(
        r'source_addr_adj\s*=\s*DMA_ADDR_ADJ_NO_CHANGE', generated_code
    )) or "DMA_ADDR_ADJ_NO_CHANGE" in generated_code
    details.append(
        CheckDetail(
            check_name="source_addr_fixed",
            passed=has_no_change,
            expected="source_addr_adj = DMA_ADDR_ADJ_NO_CHANGE for fixed peripheral",
            actual="present" if has_no_change else "missing - peripheral may be incremented",
            check_type="constraint",
        )
    )

    # Check 3: Destination address increments into memory buffer
    has_increment = bool(re.search(
        r'dest_addr_adj\s*=\s*DMA_ADDR_ADJ_INCREMENT', generated_code
    )) or "DMA_ADDR_ADJ_INCREMENT" in generated_code
    details.append(
        CheckDetail(
            check_name="dest_addr_increments",
            passed=has_increment,
            expected="dest_addr_adj = DMA_ADDR_ADJ_INCREMENT for memory buffer",
            actual="present" if has_increment else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Completion synchronization present
    has_sync = any(
        p in generated_code
        for p in ["k_sem_take", "k_sem_give", "dma_callback", "k_poll", "k_event"]
    )
    details.append(
        CheckDetail(
            check_name="completion_synchronization",
            passed=has_sync,
            expected="DMA completion synchronization mechanism present",
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

    # Check 6: device_is_ready() called
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
