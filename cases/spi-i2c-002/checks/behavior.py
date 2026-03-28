"""Behavioral checks for SPI loopback test."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI loopback behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: device_is_ready() called before SPI operations
    has_ready = "device_is_ready" in generated_code
    transceive_pos = generated_code.find("spi_transceive")
    ready_pos = generated_code.find("device_is_ready")
    order_ok = (
        has_ready
        and ready_pos != -1
        and transceive_pos != -1
        and ready_pos < transceive_pos
    )
    details.append(
        CheckDetail(
            check_name="ready_check_before_spi",
            passed=order_ok,
            expected="device_is_ready() before spi_transceive()",
            actual="correct order" if order_ok else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Separate tx and rx buffers (LLM failure: same pointer for both)
    # Heuristic: at least two distinct buffer names containing "tx"/"send"/"out" and "rx"/"recv"/"in"
    tx_patterns = [r'\btx[_\w]*buf\b', r'\bsend[_\w]*buf\b', r'\bout[_\w]*buf\b', r'\btx_data\b', r'\bsend_data\b']
    rx_patterns = [r'\brx[_\w]*buf\b', r'\brecv[_\w]*buf\b', r'\bin[_\w]*buf\b', r'\brx_data\b', r'\brecv_data\b']
    has_tx_buf = any(re.search(p, generated_code) for p in tx_patterns)
    has_rx_buf = any(re.search(p, generated_code) for p in rx_patterns)
    details.append(
        CheckDetail(
            check_name="separate_tx_rx_buffers",
            passed=has_tx_buf and has_rx_buf,
            expected="Separate tx and rx buffers defined",
            actual=f"tx_buf={has_tx_buf}, rx_buf={has_rx_buf}",
            check_type="constraint",
        )
    )

    # Check 3: Error return value checked after spi_transceive
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_error_handling",
            passed=has_error_check,
            expected="Return value of spi_transceive() checked for errors",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Loopback comparison performed (memcmp or manual loop)
    has_compare = (
        "memcmp" in generated_code
        or "strcmp" in generated_code
        or (
            "tx_buf" in generated_code
            and "rx_buf" in generated_code
            and ("==" in generated_code or "!=" in generated_code)
        )
    )
    details.append(
        CheckDetail(
            check_name="loopback_comparison",
            passed=has_compare,
            expected="TX and RX buffers compared to verify loopback",
            actual="present" if has_compare else "missing",
            check_type="constraint",
        )
    )

    # Check 5: SPI frequency configured (not zero or missing)
    has_freq = bool(
        re.search(r"frequency\s*=\s*[1-9]\d+", generated_code)
        or "1000000" in generated_code
        or "KHZ" in generated_code
        or "MHZ" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="spi_frequency_configured",
            passed=has_freq,
            expected="SPI frequency set to non-zero value in spi_config",
            actual="present" if has_freq else "missing or zero",
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
