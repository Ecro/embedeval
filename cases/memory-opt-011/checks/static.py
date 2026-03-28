"""Static analysis checks for RAM budget constraint."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate RAM-constrained buffer code structure."""
    details: list[CheckDetail] = []

    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    has_main = "void main(" in generated_code or "int main(" in generated_code
    details.append(
        CheckDetail(
            check_name="main_function_present",
            passed=has_main,
            expected="main() function defined",
            actual="present" if has_main else "missing",
            check_type="exact_match",
        )
    )

    defines = re.findall(r'#define\s+\w+.*\d+', generated_code)
    details.append(
        CheckDetail(
            check_name="buffer_sizes_defined",
            passed=len(defines) >= 2,
            expected="At least 2 #define for buffer sizes",
            actual=f"{len(defines)} #define found",
            check_type="constraint",
        )
    )

    return details
