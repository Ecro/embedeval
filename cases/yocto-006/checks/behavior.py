"""Behavioral checks for Yocto recipe with patch application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto patch recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: No manual git apply or patch in do_compile
    # (LLM hallucination: Yocto handles patches automatically via SRC_URI)
    has_git_apply = "git apply" in generated_code
    has_patch_cmd = (
        "patch -p" in generated_code
        or "patch -i" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="no_manual_patch_in_do_compile",
            passed=not has_git_apply and not has_patch_cmd,
            expected="No manual git apply or patch command in do_compile (Yocto auto-applies)",
            actual="clean" if not has_git_apply and not has_patch_cmd else "HALLUCINATION: manual patch in recipe (Yocto handles this automatically)",
            check_type="constraint",
        )
    )

    # Check 2: patch file listed with file:// scheme in SRC_URI
    has_file_patch = "file://" in generated_code and ".patch" in generated_code
    details.append(
        CheckDetail(
            check_name="patch_uses_file_scheme",
            passed=has_file_patch,
            expected="Patch file uses file:// scheme in SRC_URI",
            actual="present" if has_file_patch else "missing or wrong scheme",
            check_type="constraint",
        )
    )

    # Check 3: FILESEXTRAPATHS uses prepend (correct BitBake syntax)
    has_prepend = "FILESEXTRAPATHS:prepend" in generated_code or "FILESEXTRAPATHS_prepend" in generated_code
    details.append(
        CheckDetail(
            check_name="filesextrapaths_prepend_syntax",
            passed=has_prepend,
            expected="FILESEXTRAPATHS uses :prepend operator",
            actual="present" if has_prepend else "missing or wrong syntax",
            check_type="constraint",
        )
    )

    # Check 4: ${D}${bindir} used in do_install (not hardcoded path)
    has_d_bindir = "${D}${bindir}" in generated_code
    details.append(
        CheckDetail(
            check_name="d_bindir_in_install",
            passed=has_d_bindir,
            expected="${D}${bindir} used in do_install",
            actual="present" if has_d_bindir else "missing (hardcoded path?)",
            check_type="constraint",
        )
    )

    # Check 5: ${CC} used for cross-compilation
    has_cc = "${CC}" in generated_code
    details.append(
        CheckDetail(
            check_name="cc_variable_used",
            passed=has_cc,
            expected="${CC} used for cross-compilation",
            actual="present" if has_cc else "missing (native gcc?)",
            check_type="constraint",
        )
    )

    # Check 6: LIC_FILES_CHKSUM has md5 or sha256
    has_hash = "md5=" in generated_code or "sha256=" in generated_code
    details.append(
        CheckDetail(
            check_name="lic_chksum_has_hash",
            passed=has_hash,
            expected="LIC_FILES_CHKSUM contains md5= or sha256= hash",
            actual="present" if has_hash else "missing hash",
            check_type="constraint",
        )
    )

    return details
