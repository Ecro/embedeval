"""Behavioral checks for Yocto ptest recipe."""

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

    return details
