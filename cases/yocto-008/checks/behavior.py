"""Behavioral checks for Yocto multi-license recipe."""

import re

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

    # Check 3: No wrong SPDX like "GPLv2" or bare "GPL-2.0" (must be "GPL-2.0-only")
    # (LLM failure: using non-SPDX names)
    has_gplv2 = "GPLv2" in generated_code
    has_gpl20 = bool(re.search(r'"GPL-2\.0"[^-]', generated_code)) or generated_code.endswith('"GPL-2.0"')
    details.append(
        CheckDetail(
            check_name="correct_gpl_spdx_format",
            passed=not has_gplv2 and not has_gpl20,
            expected="Use GPL-2.0-only (SPDX), not GPLv2 or bare GPL-2.0",
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

    # Check 7: Override syntax uses ':' not '_' (Yocto 4.0+ requirement)
    deprecated_override = re.search(
        r'\b(RDEPENDS|FILES|PACKAGES|SYSTEMD_SERVICE)_\$\{PN\}',
        generated_code,
    )
    details.append(
        CheckDetail(
            check_name="colon_override_syntax",
            passed=deprecated_override is None,
            expected="Override syntax uses ':' (e.g. RDEPENDS:${PN})",
            actual="correct" if deprecated_override is None else f"DEPRECATED '_' override: {deprecated_override.group(0)}",
            check_type="constraint",
        )
    )

    # Check 8: No hardcoded /usr/lib or /usr/bin paths
    has_hardcoded_lib = bool(re.search(r'(?<!\$\{D\})/usr/lib\b', generated_code))
    has_hardcoded_bin = "/usr/bin" in generated_code
    details.append(
        CheckDetail(
            check_name="no_hardcoded_paths",
            passed=not has_hardcoded_lib and not has_hardcoded_bin,
            expected="No hardcoded /usr/lib or /usr/bin (use ${libdir}, ${bindir})",
            actual="correct" if not has_hardcoded_lib and not has_hardcoded_bin else "hardcoded paths found",
            check_type="constraint",
        )
    )

    # Check 9: install -d before install -m in do_install
    install_d_pos = generated_code.find("install -d")
    install_m_pos = generated_code.find("install -m")
    install_order_ok = install_d_pos != -1 and (install_m_pos == -1 or install_d_pos < install_m_pos)
    details.append(
        CheckDetail(
            check_name="install_d_before_install_m",
            passed=install_order_ok,
            expected="install -d called before install -m (directory must exist first)",
            actual="correct" if install_order_ok else "WRONG ORDER or missing install -d",
            check_type="constraint",
        )
    )

    # Check 10: 'inherit' used for class, not 'require'
    # (LLM failure: "require cmake" instead of "inherit cmake")
    has_require_class = bool(re.search(r'^require\s+(cmake|module|systemd|ptest|core-image)\b', generated_code, re.MULTILINE))
    details.append(
        CheckDetail(
            check_name="inherit_not_require_for_class",
            passed=not has_require_class,
            expected="'inherit' used for BitBake classes (not 'require')",
            actual="correct" if not has_require_class else "WRONG: 'require' used for a class (use 'inherit')",
            check_type="constraint",
        )
    )

    # Check 11: LICENSE count matches LIC_FILES_CHKSUM file:// count
    # LLM failure: declares dual-license but provides only one checksum entry, or vice versa
    license_line = re.search(r'LICENSE\s*=\s*"([^"]+)"', generated_code)
    license_count = len(license_line.group(1).split(" & ")) if license_line else 0
    lic_chksum_line = re.search(r'LIC_FILES_CHKSUM\s*=\s*"([^"]*)"', generated_code, re.DOTALL)
    file_count = lic_chksum_line.group(1).count("file://") if lic_chksum_line else 0
    counts_match = license_count > 0 and license_count == file_count
    details.append(
        CheckDetail(
            check_name="license_count_matches_checksum_count",
            passed=counts_match,
            expected="Number of licenses in LICENSE matches number of file:// entries in LIC_FILES_CHKSUM",
            actual=f"LICENSE has {license_count} license(s), LIC_FILES_CHKSUM has {file_count} file:// entry/entries",
            check_type="constraint",
        )
    )

    return details
