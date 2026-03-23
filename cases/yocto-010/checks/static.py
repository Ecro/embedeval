"""Static analysis checks for Yocto ptest recipe."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto ptest recipe structure."""
    details: list[CheckDetail] = []

    has_inherit_ptest = "inherit ptest" in generated_code
    details.append(
        CheckDetail(
            check_name="inherit_ptest",
            passed=has_inherit_ptest,
            expected="inherit ptest in recipe",
            actual="present" if has_inherit_ptest else "MISSING (must inherit ptest class)",
            check_type="exact_match",
        )
    )

    has_compile_ptest = "do_compile_ptest" in generated_code
    details.append(
        CheckDetail(
            check_name="do_compile_ptest_defined",
            passed=has_compile_ptest,
            expected="do_compile_ptest() function defined",
            actual="present" if has_compile_ptest else "missing",
            check_type="exact_match",
        )
    )

    has_install_ptest = "do_install_ptest" in generated_code
    details.append(
        CheckDetail(
            check_name="do_install_ptest_defined",
            passed=has_install_ptest,
            expected="do_install_ptest() function defined",
            actual="present" if has_install_ptest else "missing",
            check_type="exact_match",
        )
    )

    has_ptest_path = "PTEST_PATH" in generated_code
    details.append(
        CheckDetail(
            check_name="ptest_path_used",
            passed=has_ptest_path,
            expected="${PTEST_PATH} used in do_install_ptest",
            actual="present" if has_ptest_path else "missing",
            check_type="exact_match",
        )
    )

    has_lic_chksum = "LIC_FILES_CHKSUM" in generated_code
    details.append(
        CheckDetail(
            check_name="lic_files_chksum_defined",
            passed=has_lic_chksum,
            expected="LIC_FILES_CHKSUM defined",
            actual="present" if has_lic_chksum else "missing",
            check_type="exact_match",
        )
    )

    return details
