"""Behavioral checks for Yocto recipe with DEPENDS and RDEPENDS."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate dependency BitBake recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: RDEPENDS uses :${PN} suffix (new Yocto override syntax)
    # (LLM failure: writing RDEPENDS = "..." without :${PN} — silently ignored)
    has_rdepends_pn = "RDEPENDS:${PN}" in generated_code
    details.append(
        CheckDetail(
            check_name="rdepends_has_pn_suffix",
            passed=has_rdepends_pn,
            expected="RDEPENDS:${PN} with package name override suffix",
            actual="present" if has_rdepends_pn else "MISSING :${PN} (RDEPENDS ignored!)",
            check_type="constraint",
        )
    )

    # Check 2: DEPENDS is separate from RDEPENDS (not confused)
    # (LLM failure: putting runtime deps in DEPENDS and vice versa)
    has_depends = "DEPENDS" in generated_code
    has_rdepends = "RDEPENDS" in generated_code
    details.append(
        CheckDetail(
            check_name="both_depends_and_rdepends_present",
            passed=has_depends and has_rdepends,
            expected="Both DEPENDS (build-time) and RDEPENDS (runtime) defined",
            actual=f"DEPENDS={has_depends}, RDEPENDS={has_rdepends}",
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

    # Check 4: do_compile uses ${CC} for cross-compilation
    # (LLM failure: hardcoding gcc instead of ${CC})
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

    # Check 5: do_install uses ${D} prefix
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

    # Check 6: Uses ${bindir} not hardcoded /usr/bin
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

    return details
