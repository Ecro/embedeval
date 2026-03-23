"""Behavioral checks for Yocto BitBake recipe."""

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

    return details
