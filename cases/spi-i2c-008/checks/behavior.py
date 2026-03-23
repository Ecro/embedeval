"""Behavioral checks for I2C target (slave) mode implementation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C target mode behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: write_requested callback implemented
    has_write_requested = "write_requested" in generated_code
    details.append(
        CheckDetail(
            check_name="write_requested_callback",
            passed=has_write_requested,
            expected="write_requested callback implemented",
            actual="present" if has_write_requested else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: read_requested callback implemented
    has_read_requested = "read_requested" in generated_code
    details.append(
        CheckDetail(
            check_name="read_requested_callback",
            passed=has_read_requested,
            expected="read_requested callback implemented",
            actual="present" if has_read_requested else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: write_received callback implemented
    has_write_received = "write_received" in generated_code
    details.append(
        CheckDetail(
            check_name="write_received_callback",
            passed=has_write_received,
            expected="write_received callback implemented",
            actual="present" if has_write_received else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: read_processed callback implemented
    has_read_processed = "read_processed" in generated_code
    details.append(
        CheckDetail(
            check_name="read_processed_callback",
            passed=has_read_processed,
            expected="read_processed callback implemented",
            actual="present" if has_read_processed else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: All 4 callbacks present (composite check)
    all_four_callbacks = (
        has_write_requested
        and has_read_requested
        and has_write_received
        and has_read_processed
    )
    details.append(
        CheckDetail(
            check_name="all_four_callbacks_implemented",
            passed=all_four_callbacks,
            expected="All 4 i2c_target_callbacks implemented",
            actual="all present" if all_four_callbacks else "one or more callbacks missing",
            check_type="constraint",
        )
    )

    # Check 6: Target registered with valid address (0x55 or any 7-bit address)
    has_address = "0x55" in generated_code or "TARGET_ADDR" in generated_code or ".address" in generated_code
    details.append(
        CheckDetail(
            check_name="target_address_set",
            passed=has_address,
            expected="Target address configured in i2c_target_config",
            actual="present" if has_address else "missing",
            check_type="constraint",
        )
    )

    return details
