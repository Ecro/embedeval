"""Static analysis checks for Yocto multi-license recipe."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto multi-license recipe structure."""
    details: list[CheckDetail] = []

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

    has_ampersand = " & " in generated_code
    details.append(
        CheckDetail(
            check_name="license_uses_ampersand_separator",
            passed=has_ampersand,
            expected="LICENSE uses & separator between licenses",
            actual="present" if has_ampersand else "missing (use & not comma)",
            check_type="exact_match",
        )
    )

    has_spdx_mit = '"MIT"' in generated_code or "= \"MIT" in generated_code or "MIT &" in generated_code or "& MIT" in generated_code
    details.append(
        CheckDetail(
            check_name="spdx_mit_identifier",
            passed=has_spdx_mit,
            expected="MIT SPDX identifier used",
            actual="present" if has_spdx_mit else "missing",
            check_type="exact_match",
        )
    )

    has_spdx_gpl = "GPL-2.0-only" in generated_code
    details.append(
        CheckDetail(
            check_name="spdx_gpl_identifier",
            passed=has_spdx_gpl,
            expected="GPL-2.0-only SPDX identifier used (not GPLv2 or GPL-2.0)",
            actual="present" if has_spdx_gpl else "missing or wrong format",
            check_type="exact_match",
        )
    )

    return details
