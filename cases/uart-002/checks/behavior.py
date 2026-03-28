"""Behavioral checks for UART async API with DMA application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate UART async behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: UART_RX_RDY event handled in callback
    has_rx_rdy = "UART_RX_RDY" in generated_code
    details.append(
        CheckDetail(
            check_name="uart_rx_rdy_handled",
            passed=has_rx_rdy,
            expected="UART_RX_RDY event handled in callback",
            actual="present" if has_rx_rdy else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: RX buffer defined with positive size
    import re
    buf_match = re.search(r"uint8_t\s+\w+\[(\d+)\]", generated_code)
    buf_size_ok = bool(buf_match and int(buf_match.group(1)) > 0)
    details.append(
        CheckDetail(
            check_name="rx_buffer_nonzero",
            passed=buf_size_ok,
            expected="RX buffer declared with positive size",
            actual="present" if buf_size_ok else "missing or zero-sized",
            check_type="constraint",
        )
    )

    # Check 3: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called before UART operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 4: callback registered before uart_rx_enable
    cb_pos = generated_code.find("uart_callback_set")
    rx_pos = generated_code.find("uart_rx_enable")
    order_ok = cb_pos != -1 and rx_pos != -1 and cb_pos < rx_pos
    details.append(
        CheckDetail(
            check_name="callback_before_rx_enable",
            passed=order_ok,
            expected="uart_callback_set called before uart_rx_enable",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 5: Cross-platform — no Linux/POSIX serial APIs
    has_posix = any(
        p in generated_code for p in ["open(", "read(", "write(", "ioctl(", "termios"]
    )
    details.append(
        CheckDetail(
            check_name="no_posix_serial_apis",
            passed=not has_posix,
            expected="No POSIX serial APIs (wrong platform)",
            actual="POSIX API found" if has_posix else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Ends with k_sleep(K_FOREVER) — not a busy loop
    has_forever_sleep = "K_FOREVER" in generated_code
    details.append(
        CheckDetail(
            check_name="sleeps_forever_not_busy_loop",
            passed=has_forever_sleep,
            expected="k_sleep(K_FOREVER) used instead of busy-wait loop",
            actual="present" if has_forever_sleep else "missing",
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
