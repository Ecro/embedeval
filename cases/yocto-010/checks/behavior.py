"""Behavioral checks for Yocto ptest recipe."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto ptest recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: No "make test" in do_install_ptest
    # (LLM hallucination: ptest doesn't use make test in install)
    has_make_test = "make test" in generated_code
    details.append(
        CheckDetail(
            check_name="no_make_test_in_install_ptest",
            passed=not has_make_test,
            expected="No 'make test' in do_install_ptest (ptest uses run-ptest script)",
            actual="clean" if not has_make_test else "HALLUCINATION: 'make test' in do_install_ptest (wrong!)",
            check_type="constraint",
        )
    )

    # Check 2: run-ptest script installed or referenced
    has_run_ptest = "run-ptest" in generated_code
    details.append(
        CheckDetail(
            check_name="run_ptest_script_installed",
            passed=has_run_ptest,
            expected="run-ptest script installed in do_install_ptest",
            actual="present" if has_run_ptest else "missing (run-ptest script needed for ptest framework)",
            check_type="constraint",
        )
    )

    # Check 3: ${D}${PTEST_PATH} used in do_install_ptest
    has_d_ptest = "${D}${PTEST_PATH}" in generated_code
    details.append(
        CheckDetail(
            check_name="d_ptest_path_in_install",
            passed=has_d_ptest,
            expected="${D}${PTEST_PATH} used in do_install_ptest",
            actual="present" if has_d_ptest else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Both do_compile_ptest and do_install_ptest defined
    has_compile = "do_compile_ptest" in generated_code
    has_install = "do_install_ptest" in generated_code
    details.append(
        CheckDetail(
            check_name="both_ptest_functions_defined",
            passed=has_compile and has_install,
            expected="Both do_compile_ptest() and do_install_ptest() defined",
            actual=f"compile_ptest={has_compile}, install_ptest={has_install}",
            check_type="constraint",
        )
    )

    # Check 5: LIC_FILES_CHKSUM has a hash
    has_hash = "md5=" in generated_code or "sha256=" in generated_code
    details.append(
        CheckDetail(
            check_name="lic_chksum_has_hash",
            passed=has_hash,
            expected="LIC_FILES_CHKSUM has md5= or sha256= hash",
            actual="present" if has_hash else "missing",
            check_type="constraint",
        )
    )

    # Check 6: ${CC} used in ptest compile
    has_cc = "${CC}" in generated_code
    details.append(
        CheckDetail(
            check_name="cc_used_for_test_compile",
            passed=has_cc,
            expected="${CC} used for test compilation",
            actual="present" if has_cc else "missing",
            check_type="constraint",
        )
    )

    # Check 7: SPDX license format — no non-SPDX names
    non_spdx_patterns = [
        r'\bGPLv2\b', r'\bGPLv3\b', r'\bLGPLv2\b', r'\bLGPLv2\.1\b',
        r'\bLGPLv3\b', r'"GPL-2\.0"[^-]', r'"GPL-3\.0"[^-]',
    ]
    has_non_spdx = any(re.search(p, generated_code) for p in non_spdx_patterns)
    details.append(
        CheckDetail(
            check_name="spdx_license_format",
            passed=not has_non_spdx,
            expected="SPDX license identifier (GPL-2.0-only, not GPLv2)",
            actual="correct SPDX" if not has_non_spdx else "NON-SPDX license name found",
            check_type="constraint",
        )
    )

    # Check 8: Override syntax uses ':' not '_' (Yocto 4.0+ requirement)
    # (LLM failure: RDEPENDS_${PN}-ptest instead of RDEPENDS:${PN}-ptest)
    deprecated_override = re.search(
        r'\b(RDEPENDS|FILES|PACKAGES)_\$\{PN\}',
        generated_code,
    )
    details.append(
        CheckDetail(
            check_name="colon_override_syntax",
            passed=deprecated_override is None,
            expected="Override syntax uses ':' (e.g. RDEPENDS:${PN}-ptest)",
            actual="correct" if deprecated_override is None else f"DEPRECATED '_' override: {deprecated_override.group(0)}",
            check_type="constraint",
        )
    )

    # Check 9: No hardcoded /usr/lib or /usr/bin paths
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

    # Check 10: 'inherit ptest' present (required for ptest framework integration)
    # (LLM failure: defining do_install_ptest without inheriting ptest class)
    has_inherit_ptest = "inherit ptest" in generated_code
    details.append(
        CheckDetail(
            check_name="inherits_ptest_class",
            passed=has_inherit_ptest,
            expected="'inherit ptest' present (required for ptest framework)",
            actual="present" if has_inherit_ptest else "MISSING (ptest framework not active!)",
            check_type="constraint",
        )
    )

    return details
