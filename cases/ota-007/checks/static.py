"""Static analysis checks for OTA progress reporting."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA progress reporting code structure."""
    details: list[CheckDetail] = []

    has_dfu_target = "dfu/dfu_target.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_header",
            passed=has_dfu_target,
            expected="zephyr/dfu/dfu_target.h included",
            actual="present" if has_dfu_target else "missing",
            check_type="exact_match",
        )
    )

    has_total_size = (
        "TOTAL_IMAGE_SIZE" in generated_code
        or "total_size" in generated_code
        or "image_size" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="total_size_defined",
            passed=has_total_size,
            expected="Total image size constant/variable defined before download",
            actual="present" if has_total_size else "missing",
            check_type="exact_match",
        )
    )

    has_progress = (
        "report_progress" in generated_code
        or "progress" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="progress_reporting",
            passed=has_progress,
            expected="Progress reporting function or logic present",
            actual="present" if has_progress else "missing",
            check_type="exact_match",
        )
    )

    has_div_zero_guard = (
        "total == 0" in generated_code
        or "total_size == 0" in generated_code
        or "!= 0" in generated_code
        or "total > 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="division_by_zero_guard",
            passed=has_div_zero_guard,
            expected="Division-by-zero guard before percentage calculation",
            actual="present" if has_div_zero_guard else "missing (potential divide-by-zero)",
            check_type="exact_match",
        )
    )

    has_percentage_calc = (
        "* 100" in generated_code
        or "* 100U" in generated_code
        or "pct" in generated_code
        or "percent" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="percentage_calculation",
            passed=has_percentage_calc,
            expected="Percentage calculation present (received * 100 / total)",
            actual="present" if has_percentage_calc else "missing",
            check_type="exact_match",
        )
    )

    has_bytes_received = (
        "bytes_received" in generated_code
        or "received" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="bytes_received_counter",
            passed=has_bytes_received,
            expected="Bytes received counter tracked during download",
            actual="present" if has_bytes_received else "missing",
            check_type="exact_match",
        )
    )

    return details
