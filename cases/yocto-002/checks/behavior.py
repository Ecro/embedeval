"""Behavioral checks for Yocto CMake recipe."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CMake BitBake recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: inherit cmake present (not manual cmake commands)
    # (LLM failure: writing do_compile() { cmake .. && make } instead of inherit cmake)
    has_inherit_cmake = "inherit cmake" in generated_code
    has_manual_cmake = "cmake .." in generated_code or "cmake ${S}" in generated_code
    details.append(
        CheckDetail(
            check_name="inherits_cmake_class",
            passed=has_inherit_cmake and not has_manual_cmake,
            expected="inherit cmake used (not manual cmake commands in do_compile)",
            actual="correct" if (has_inherit_cmake and not has_manual_cmake) else "wrong (manual cmake or missing inherit)",
            check_type="constraint",
        )
    )

    # Check 2: SRCREV set when using git:// (mandatory, build fails without it)
    # (LLM failure: uses git:// SRC_URI without SRCREV)
    has_git_src = "git://" in generated_code
    has_srcrev = "SRCREV" in generated_code
    srcrev_ok = (not has_git_src) or has_srcrev
    details.append(
        CheckDetail(
            check_name="srcrev_present_for_git",
            passed=srcrev_ok,
            expected="SRCREV defined when SRC_URI uses git://",
            actual="ok" if srcrev_ok else "MISSING SRCREV for git:// source (build error!)",
            check_type="constraint",
        )
    )

    # Check 3: LIC_FILES_CHKSUM has md5 or sha256 hash
    has_hash = "md5=" in generated_code or "sha256=" in generated_code
    details.append(
        CheckDetail(
            check_name="lic_chksum_has_hash",
            passed=has_hash,
            expected="LIC_FILES_CHKSUM contains md5= or sha256=",
            actual="present" if has_hash else "missing (will fail parse)",
            check_type="constraint",
        )
    )

    # Check 4: do_install uses ${D} prefix
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

    # Check 5: Uses ${bindir} not hardcoded /usr/bin
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

    # Check 6: S set to ${WORKDIR}/git for git sources
    has_s_workdir_git = "${WORKDIR}/git" in generated_code or "${WORKDIR}" in generated_code
    details.append(
        CheckDetail(
            check_name="s_variable_set",
            passed=has_s_workdir_git,
            expected="S set to ${WORKDIR}/git (or ${WORKDIR} for local sources)",
            actual="present" if has_s_workdir_git else "missing",
            check_type="constraint",
        )
    )

    # Check 7: SPDX license format — no non-SPDX names
    # (LLM failure: "GPLv2" instead of "GPL-2.0-only")
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
            actual="correct SPDX format" if not has_non_spdx else "NON-SPDX license name found",
            check_type="constraint",
        )
    )

    # Check 8: Override syntax uses ':' not '_' (Yocto 4.0+ requirement)
    # (LLM failure: using deprecated RDEPENDS_${PN})
    deprecated_override = re.search(
        r'\b(RDEPENDS|SYSTEMD_SERVICE|SYSTEMD_AUTO_ENABLE|FILES|PACKAGES)_\$\{PN\}',
        generated_code,
    )
    details.append(
        CheckDetail(
            check_name="colon_override_syntax",
            passed=deprecated_override is None,
            expected="Override syntax uses ':' operator (e.g. RDEPENDS:${PN})",
            actual="correct" if deprecated_override is None else f"DEPRECATED '_' override: {deprecated_override.group(0)}",
            check_type="constraint",
        )
    )

    # Check 9: No hardcoded /usr/lib (use ${libdir})
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

    # Check 10: install -d before install -m in do_install
    # (LLM failure: calling install -m without creating the directory first)
    install_d_pos = generated_code.find("install -d")
    install_m_pos = generated_code.find("install -m")
    install_order_ok = install_d_pos != -1 and (install_m_pos == -1 or install_d_pos < install_m_pos)
    details.append(
        CheckDetail(
            check_name="install_d_before_install_m",
            passed=install_order_ok,
            expected="install -d called before install -m (create dir before installing file)",
            actual="correct" if install_order_ok else "WRONG ORDER or missing install -d",
            check_type="constraint",
        )
    )

    return details
