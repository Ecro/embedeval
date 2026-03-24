"""Behavioral checks for Linux IIO ADC driver skeleton."""

import re

from embedeval.check_utils import (
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate IIO driver behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: read_raw returns IIO_VAL_INT (not 0 or 1)
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

    # Check 7: Error path handles allocation failure (-ENOMEM)
    # LLM failure: calling devm_iio_device_alloc, not checking NULL, proceeding to crash
    error_blocks = extract_error_blocks(generated_code)
    has_enomem_check = (
        "ENOMEM" in generated_code
        or "!indio_dev" in generated_code
        or bool(re.search(r'if\s*\(\s*!\s*\w+\s*\)', generated_code))
    )
    details.append(
        CheckDetail(
            check_name="allocation_failure_handled",
            passed=has_enomem_check,
            expected="-ENOMEM returned when devm_iio_device_alloc fails",
            actual="present" if has_enomem_check else "allocation failure not handled",
            check_type="constraint",
        )
    )

    # Check 8: No Zephyr API contamination
    zephyr_apis = ["k_work_submit", "k_thread_create", "K_THREAD_DEFINE",
                   "k_mutex_lock", "k_sleep("]
    has_zephyr = any(api in generated_code for api in zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_zephyr_apis",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs in Linux IIO driver",
            actual="clean" if not has_zephyr else "WRONG PLATFORM: Zephyr APIs found",
            check_type="constraint",
        )
    )

    return details
