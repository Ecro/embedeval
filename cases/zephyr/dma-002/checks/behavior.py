"""Behavioral checks for DMA peripheral-to-memory transfer."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA peripheral-to-memory behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: PERIPHERAL_TO_MEMORY direction set (not MEMORY_TO_MEMORY)
    has_p2m = scoped_contains(generated_code, 'PERIPHERAL_TO_MEMORY', scope='code_only')
    has_m2m_wrong = (
        scoped_contains(generated_code, 'MEMORY_TO_MEMORY', scope='code_only')
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
    )) or scoped_contains(generated_code, 'DMA_ADDR_ADJ_NO_CHANGE', scope='code_only')
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
    )) or scoped_contains(generated_code, 'DMA_ADDR_ADJ_INCREMENT', scope='code_only')
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
    config_pos = find_in_code(generated_code, "dma_config(")
    start_pos = find_in_code(generated_code, "dma_start(")
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
    has_ready = scoped_contains(generated_code, 'device_is_ready', scope='code_only')
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() before DMA operations",
            actual="present" if has_ready else "missing",
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
