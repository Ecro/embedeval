"""Behavioral checks for Yocto multi-license recipe."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto multi-license recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: & separator used (NOT comma)
    # (LLM failure: "MIT, GPL-2.0-only" — comma is wrong in BitBake)
    has_comma_sep = '"MIT,' in generated_code or 'MIT, GPL' in generated_code
    details.append(
        CheckDetail(
            check_name="no_comma_license_separator",
            passed=not has_comma_sep,
            expected="LICENSE uses & not comma separator",
            actual="clean" if not has_comma_sep else "WRONG: comma separator in LICENSE (use &)",
            check_type="constraint",
        )
    )

    # Check 2: Two separate md5/sha256 entries in LIC_FILES_CHKSUM
    # (LLM failure: only one checksum entry for dual-licensed package)
    md5_count = generated_code.count("md5=") + generated_code.count("sha256=")
    details.append(
        CheckDetail(
            check_name="two_checksum_entries",
            passed=md5_count >= 2,
            expected="LIC_FILES_CHKSUM has checksums for both license files",
            actual=f"found {md5_count} checksum(s) (need at least 2)",
            check_type="constraint",
        )
    )

    # Check 3: No wrong SPDX like "GPLv2" or "GPL-2.0" (must be "GPL-2.0-only")
    # (LLM failure: using non-SPDX names)
    has_gplv2 = "GPLv2" in generated_code
    has_gpl20 = '"GPL-2.0"' in generated_code
    details.append(
        CheckDetail(
            check_name="correct_gpl_spdx_format",
            passed=not has_gplv2 and not has_gpl20,
            expected="Use GPL-2.0-only (SPDX), not GPLv2 or GPL-2.0",
            actual="correct" if not has_gplv2 and not has_gpl20 else "WRONG SPDX: use GPL-2.0-only",
            check_type="constraint",
        )
    )

    # Check 4: LIC_FILES_CHKSUM has file:// entries
    has_file_lic = "file://" in generated_code and "LIC_FILES_CHKSUM" in generated_code
    details.append(
        CheckDetail(
            check_name="lic_chksum_has_file_entries",
            passed=has_file_lic,
            expected="LIC_FILES_CHKSUM points to file:// license files",
            actual="present" if has_file_lic else "missing",
            check_type="constraint",
        )
    )

    # Check 5: ${D}${bindir} in do_install
    has_d_bindir = "${D}${bindir}" in generated_code
    details.append(
        CheckDetail(
            check_name="d_bindir_in_install",
            passed=has_d_bindir,
            expected="${D}${bindir} used in do_install",
            actual="present" if has_d_bindir else "missing",
            check_type="constraint",
        )
    )

    # Check 6: ${CC} used for cross-compilation
    has_cc = "${CC}" in generated_code
    details.append(
        CheckDetail(
            check_name="cc_variable_used",
            passed=has_cc,
            expected="${CC} used for cross-compilation",
            actual="present" if has_cc else "missing",
            check_type="constraint",
        )
    )

    return details
