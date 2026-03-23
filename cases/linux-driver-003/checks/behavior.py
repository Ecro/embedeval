"""Behavioral checks for Linux IIO ADC driver skeleton."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate IIO driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: read_raw returns IIO_VAL_INT (not 0 or 1)
    # (LLM failure: returning 0 means "no value", sysfs read shows nothing)
    has_iio_val_int = "IIO_VAL_INT" in generated_code
    details.append(
        CheckDetail(
            check_name="read_raw_returns_iio_val_int",
            passed=has_iio_val_int,
            expected="read_raw returns IIO_VAL_INT for RAW channel reads",
            actual="present" if has_iio_val_int else "MISSING (sysfs shows empty!)",
            check_type="constraint",
        )
    )

    # Check 2: IIO_CHAN_INFO_RAW handled in read_raw switch/if
    # (LLM failure: read_raw ignores the mask argument entirely)
    has_raw_mask = "IIO_CHAN_INFO_RAW" in generated_code
    details.append(
        CheckDetail(
            check_name="iio_chan_info_raw_handled",
            passed=has_raw_mask,
            expected="IIO_CHAN_INFO_RAW case handled in read_raw",
            actual="present" if has_raw_mask else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Uses devm_ prefixed alloc (not manual iio_device_alloc)
    # (LLM failure: using iio_device_alloc without iio_device_unregister in remove)
    has_devm_alloc = "devm_iio_device_alloc" in generated_code
    details.append(
        CheckDetail(
            check_name="devm_iio_device_alloc_used",
            passed=has_devm_alloc,
            expected="devm_iio_device_alloc() for automatic cleanup",
            actual="present" if has_devm_alloc else "missing (manual alloc needs matching free)",
            check_type="constraint",
        )
    )

    # Check 4: devm_iio_device_register or iio_device_register called
    # (LLM failure: allocates but never registers — device invisible to userspace)
    has_register = (
        "devm_iio_device_register" in generated_code
        or "iio_device_register" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="iio_device_registered",
            passed=has_register,
            expected="iio_device_register() or devm_iio_device_register() called",
            actual="present" if has_register else "MISSING (device not visible!)",
            check_type="constraint",
        )
    )

    # Check 5: indio_dev->info assigned (links read_raw to device)
    # (LLM failure: forgets to assign iio_info, read_raw never called)
    has_info_assign = "->info" in generated_code or ".info" in generated_code
    details.append(
        CheckDetail(
            check_name="iio_info_assigned",
            passed=has_info_assign,
            expected="indio_dev->info assigned to iio_info struct",
            actual="present" if has_info_assign else "MISSING (read_raw never called!)",
            check_type="constraint",
        )
    )

    # Check 6: num_channels set (otherwise IIO reports 0 channels)
    has_num_channels = "num_channels" in generated_code
    details.append(
        CheckDetail(
            check_name="num_channels_set",
            passed=has_num_channels,
            expected="indio_dev->num_channels set",
            actual="present" if has_num_channels else "missing (0 channels exported)",
            check_type="constraint",
        )
    )

    return details
