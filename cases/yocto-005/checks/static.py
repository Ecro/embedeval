"""Static analysis checks for Yocto out-of-tree kernel module recipe."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate kernel module BitBake recipe structure."""
    details: list[CheckDetail] = []

    has_summary = "SUMMARY" in generated_code
    details.append(
        CheckDetail(
            check_name="summary_defined",
            passed=has_summary,
            expected="SUMMARY variable defined",
            actual="present" if has_summary else "missing",
            check_type="exact_match",
        )
    )

    has_license = "LICENSE" in generated_code
    details.append(
        CheckDetail(
            check_name="license_defined",
            passed=has_license,
            expected="LICENSE variable defined",
            actual="present" if has_license else "missing",
            check_type="exact_match",
        )
    )

    has_inherit_module = "inherit module" in generated_code
    details.append(
        CheckDetail(
            check_name="inherit_module",
            passed=has_inherit_module,
            expected="inherit module present",
            actual="present" if has_inherit_module else "missing",
            check_type="exact_match",
        )
    )

    has_src_uri = "SRC_URI" in generated_code
    details.append(
        CheckDetail(
            check_name="src_uri_defined",
            passed=has_src_uri,
            expected="SRC_URI defined",
            actual="present" if has_src_uri else "missing",
            check_type="exact_match",
        )
    )

    has_autoload = "KERNEL_MODULE_AUTOLOAD" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_module_autoload",
            passed=has_autoload,
            expected="KERNEL_MODULE_AUTOLOAD set for boot loading",
            actual="present" if has_autoload else "missing",
            check_type="exact_match",
        )
    )

    has_lic_chksum = "LIC_FILES_CHKSUM" in generated_code
    details.append(
        CheckDetail(
            check_name="lic_files_chksum",
            passed=has_lic_chksum,
            expected="LIC_FILES_CHKSUM defined",
            actual="present" if has_lic_chksum else "missing",
            check_type="exact_match",
        )
    )

    return details
