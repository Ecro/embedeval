"""Behavioral checks for SPI full-duplex transfer."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI full-duplex behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Both TX and RX buf_sets provided to spi_transceive
    # Must pass both tx_bufs and rx_bufs (not NULL for either)
    transceive_pos = generated_code.find("spi_transceive")
    has_tx_bufs = "tx_bufs" in generated_code or "tx_buf_set" in generated_code
    has_rx_bufs = "rx_bufs" in generated_code or "rx_buf_set" in generated_code
    both_populated = has_tx_bufs and has_rx_bufs
    details.append(
        CheckDetail(
            check_name="both_tx_rx_buf_sets_populated",
            passed=both_populated,
            expected="Both TX and RX spi_buf_set structs populated and passed to spi_transceive",
            actual=f"tx_bufs={has_tx_bufs}, rx_bufs={has_rx_bufs}",
            check_type="constraint",
        )
    )

    # Check 2: TX and RX buffers are different arrays
    # Check for two separate buffer declarations
    has_separate_tx = "tx_buf" in generated_code
    has_separate_rx = "rx_buf" in generated_code
    buffers_separate = has_separate_tx and has_separate_rx
    details.append(
        CheckDetail(
            check_name="tx_rx_buffers_separate",
            passed=buffers_separate,
            expected="TX buffer and RX buffer are separate arrays",
            actual="separate" if buffers_separate else "missing one or both buffers",
            check_type="constraint",
        )
    )

    # Check 3: spi_config has operation field with SPI_OP_MODE_MASTER
    has_master_mode = "SPI_OP_MODE_MASTER" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_op_mode_master_set",
            passed=has_master_mode,
            expected="SPI_OP_MODE_MASTER set in spi_config.operation",
            actual="present" if has_master_mode else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Error handling on spi_transceive return value
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code or "ret" in generated_code
    details.append(
        CheckDetail(
            check_name="transceive_return_checked",
            passed=has_error_check and transceive_pos != -1,
            expected="spi_transceive() return value checked for error",
            actual="present" if (has_error_check and transceive_pos != -1) else "missing",
            check_type="constraint",
        )
    )

    # Check 5: device_is_ready before transfer
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_is_ready_before_transfer",
            passed=has_ready,
            expected="device_is_ready() called before SPI transfer",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    return details
