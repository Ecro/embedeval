"""Behavioral checks for Yocto BitBake recipe."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BitBake recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: LIC_FILES_CHKSUM has md5 hash
    # (LLM failure: LIC_FILES_CHKSUM without md5= or sha256=)
    has_md5 = "md5=" in generated_code or "sha256=" in generated_code
    details.append(
        CheckDetail(
            check_name="lic_chksum_has_hash",
            passed=has_md5,
            expected="LIC_FILES_CHKSUM contains md5= or sha256=",
            actual="present" if has_md5 else "missing (will fail parse)",
            check_type="constraint",
        )
    )

    # Check 2: do_install uses ${D} prefix (staging dir)
    # (LLM failure: installing to absolute paths like /usr/bin)
    has_d_prefix = "${D}" in generated_code
    details.append(
        CheckDetail(
            check_name="install_uses_d_prefix",
            passed=has_d_prefix,
            expected="${D} used in do_install (staging directory)",
            actual="present" if has_d_prefix else "MISSING (wrong install path!)",
            check_type="constraint",
        )
    )

    # Check 3: Uses ${bindir} not hardcoded /usr/bin
    # (LLM failure: hardcoding /usr/bin instead of Yocto variable)
    has_bindir = "${bindir}" in generated_code
    has_hardcoded = "/usr/bin" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_bindir_variable",
            passed=has_bindir and not has_hardcoded,
            expected="${bindir} used (not hardcoded /usr/bin)",
            actual=f"bindir={has_bindir}, hardcoded={has_hardcoded}",
            check_type="constraint",
        )
    )

    # Check 4: do_compile uses ${CC} (cross-compiler)
    # (LLM failure: using 'gcc' directly instead of Yocto CC variable)
    has_cc_var = "${CC}" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_cc_variable",
            passed=has_cc_var,
            expected="${CC} used for cross-compilation",
            actual="present" if has_cc_var else "missing (native gcc?)",
            check_type="constraint",
        )
    )

    # Check 5: install -d to create directory before installing files
    has_install_d = "install -d" in generated_code
    details.append(
        CheckDetail(
            check_name="install_creates_dir",
            passed=has_install_d,
            expected="install -d to create directory before file install",
            actual="present" if has_install_d else "missing",
            check_type="constraint",
        )
    )

    # Check 6: SRC_URI has valid scheme
    has_valid_uri = any(
        s in generated_code
        for s in ["file://", "git://", "https://", "http://"]
    )
    details.append(
        CheckDetail(
            check_name="src_uri_valid_scheme",
            passed=has_valid_uri,
            expected="SRC_URI has valid scheme (file://, git://, etc.)",
            actual="present" if has_valid_uri else "missing or invalid",
            check_type="constraint",
        )
    )

    # Check 7: SPDX license format — no non-SPDX names
    # (LLM failure: "GPLv2" instead of "GPL-2.0-only", "LGPLv2.1" instead of "LGPL-2.1-only")
    non_spdx_patterns = [
        r'\bGPLv2\b', r'\bGPLv3\b', r'\bLGPLv2\b', r'\bLGPLv2\.1\b',
        r'\bLGPLv3\b', r'"GPL-2\.0"[^-]', r'"GPL-3\.0"[^-]',
    ]
    has_non_spdx = any(re.search(p, generated_code) for p in non_spdx_patterns)
    details.append(
        CheckDetail(
            check_name="spdx_license_format",
            passed=not has_non_spdx,
            expected="SPDX license identifiers used (e.g. GPL-2.0-only, not GPLv2)",
            actual="correct SPDX format" if not has_non_spdx else "NON-SPDX license name found (use GPL-2.0-only not GPLv2)",
            check_type="constraint",
        )
    )

    # Check 8: Override syntax uses ':' not '_' (Yocto 4.0+ / Honister+ requirement)
    # (LLM failure: using deprecated RDEPENDS_${PN} or SYSTEMD_SERVICE_${PN})
    deprecated_override = re.search(
        r'\b(RDEPENDS|SYSTEMD_SERVICE|SYSTEMD_AUTO_ENABLE|FILES|PACKAGES|KERNEL_MODULE_AUTOLOAD)_\$\{PN\}',
        generated_code,
    )
    details.append(
        CheckDetail(
            check_name="colon_override_syntax",
            passed=deprecated_override is None,
            expected="Override syntax uses ':' operator (e.g. RDEPENDS:${PN}, not RDEPENDS_${PN})",
            actual="correct" if deprecated_override is None else f"DEPRECATED '_' override syntax: {deprecated_override.group(0)}",
            check_type="constraint",
        )
    )

    # Check 9: No hardcoded /usr/lib path (use ${libdir})
    # (LLM failure: installing to /usr/lib instead of ${D}${libdir})
    has_hardcoded_lib = bool(re.search(r'(?<!\$\{D\})/usr/lib\b', generated_code))
    details.append(
        CheckDetail(
            check_name="no_hardcoded_libdir",
            passed=not has_hardcoded_lib,
            expected="${libdir} used (not hardcoded /usr/lib)",
            actual="correct" if not has_hardcoded_lib else "hardcoded /usr/lib found (use ${libdir})",
            check_type="constraint",
        )
    )

    # Check 10: SRC_URI git:// entries have SRCREV
    # (LLM failure: git:// without SRCREV — BitBake fetches HEAD unpredictably)
    has_git = "git://" in generated_code
    has_srcrev = "SRCREV" in generated_code
    srcrev_ok = (not has_git) or has_srcrev
    details.append(
        CheckDetail(
            check_name="git_src_uri_has_srcrev",
            passed=srcrev_ok,
            expected="SRCREV defined when SRC_URI uses git://",
            actual="ok" if srcrev_ok else "MISSING SRCREV for git:// (unpredictable builds!)",
            check_type="constraint",
        )
    )

    return details
