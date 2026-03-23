"""Behavioral checks for Yocto CMake recipe."""

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

    return details
