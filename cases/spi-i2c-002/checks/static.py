"""Static analysis checks for SPI loopback test."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI loopback code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: SPI header included
    has_spi_h = "zephyr/drivers/spi.h" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_header_included",
            passed=has_spi_h,
            expected="zephyr/drivers/spi.h included",
            actual="present" if has_spi_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Device obtained via DT
    has_dev_get = (
        "DEVICE_DT_GET" in generated_code
        or "device_get_binding" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="device_binding",
            passed=has_dev_get,
            expected="DEVICE_DT_GET or device_get_binding used",
            actual="present" if has_dev_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: spi_transceive called
    has_transceive = "spi_transceive" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_transceive_called",
            passed=has_transceive,
            expected="spi_transceive() called",
            actual="present" if has_transceive else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: spi_buf_set structures used
    has_buf_set = "spi_buf_set" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_buf_set_used",
            passed=has_buf_set,
            expected="struct spi_buf_set defined",
            actual="present" if has_buf_set else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: spi_config struct used
    has_spi_cfg = "spi_config" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_config_used",
            passed=has_spi_cfg,
            expected="struct spi_config defined",
            actual="present" if has_spi_cfg else "missing",
            check_type="exact_match",
        )
    )

    return details
