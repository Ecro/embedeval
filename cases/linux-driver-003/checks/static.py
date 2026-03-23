"""Static analysis checks for Linux IIO ADC driver skeleton."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate IIO driver code structure."""
    details: list[CheckDetail] = []

    has_module_h = "linux/module.h" in generated_code
    details.append(
        CheckDetail(
            check_name="module_header",
            passed=has_module_h,
            expected="linux/module.h included",
            actual="present" if has_module_h else "missing",
            check_type="exact_match",
        )
    )

    has_iio_h = "linux/iio/iio.h" in generated_code
    details.append(
        CheckDetail(
            check_name="iio_header",
            passed=has_iio_h,
            expected="linux/iio/iio.h included",
            actual="present" if has_iio_h else "missing",
            check_type="exact_match",
        )
    )

    has_license = "MODULE_LICENSE" in generated_code
    details.append(
        CheckDetail(
            check_name="module_license",
            passed=has_license,
            expected="MODULE_LICENSE defined",
            actual="present" if has_license else "missing",
            check_type="exact_match",
        )
    )

    has_chan_spec = "iio_chan_spec" in generated_code
    details.append(
        CheckDetail(
            check_name="iio_chan_spec_defined",
            passed=has_chan_spec,
            expected="struct iio_chan_spec array defined",
            actual="present" if has_chan_spec else "missing",
            check_type="exact_match",
        )
    )

    has_iio_voltage = "IIO_VOLTAGE" in generated_code
    details.append(
        CheckDetail(
            check_name="iio_voltage_type",
            passed=has_iio_voltage,
            expected="IIO_VOLTAGE channel type set",
            actual="present" if has_iio_voltage else "missing",
            check_type="exact_match",
        )
    )

    has_read_raw = "read_raw" in generated_code
    details.append(
        CheckDetail(
            check_name="read_raw_callback",
            passed=has_read_raw,
            expected="read_raw callback defined in iio_info",
            actual="present" if has_read_raw else "missing",
            check_type="exact_match",
        )
    )

    has_iio_info = "iio_info" in generated_code
    details.append(
        CheckDetail(
            check_name="iio_info_struct",
            passed=has_iio_info,
            expected="struct iio_info defined",
            actual="present" if has_iio_info else "missing",
            check_type="exact_match",
        )
    )

    return details
