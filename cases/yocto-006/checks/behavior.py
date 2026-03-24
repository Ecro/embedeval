"""Behavioral checks for Yocto recipe with patch application."""

import re

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

    # Check 3: FILESEXTRAPATHS uses :prepend (correct BitBake syntax)
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
    deprecated_override = re.search(
        r'\b(RDEPENDS|FILESEXTRAPATHS|FILES|PACKAGES)_\$\{PN\}',
        generated_code,
    )
    details.append(
        CheckDetail(
            check_name="colon_override_syntax",
            passed=deprecated_override is None,
            expected="Override syntax uses ':' (e.g. FILESEXTRAPATHS:prepend)",
            actual="correct" if deprecated_override is None else f"DEPRECATED '_' override: {deprecated_override.group(0)}",
            check_type="constraint",
        )
    )

    # Check 9: FILESEXTRAPATHS uses := (immediate assignment) not just =
    # (LLM failure: "FILESEXTRAPATHS:prepend = ..." instead of ":= ..." — late binding causes wrong path)
    has_immediate_assign = "FILESEXTRAPATHS:prepend :=" in generated_code
    has_filesextrapaths = "FILESEXTRAPATHS" in generated_code
    filesextrapaths_ok = (not has_filesextrapaths) or has_immediate_assign
    details.append(
        CheckDetail(
            check_name="filesextrapaths_immediate_assignment",
            passed=filesextrapaths_ok,
            expected="FILESEXTRAPATHS:prepend uses ':= ' (immediate assignment)",
            actual="correct" if filesextrapaths_ok else "WRONG: use ':=' not '=' for FILESEXTRAPATHS:prepend",
            check_type="constraint",
        )
    )

    # Check 10: install -d before install -m in do_install
    # (LLM failure: calling install -m without creating directory first)
    install_d_pos = generated_code.find("install -d")
    install_m_pos = generated_code.find("install -m")
    install_order_ok = install_d_pos != -1 and (install_m_pos == -1 or install_d_pos < install_m_pos)
    details.append(
        CheckDetail(
            check_name="install_d_before_install_m",
            passed=install_order_ok,
            expected="install -d called before install -m (directory must exist)",
            actual="correct" if install_order_ok else "WRONG ORDER or missing install -d",
            check_type="constraint",
        )
    )

    return details
