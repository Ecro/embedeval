"""Behavioral checks for Yocto out-of-tree kernel module recipe."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate kernel module BitBake recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: inherit module present
    # (LLM failure: writing custom do_compile with make commands instead of inherit module)
    has_inherit_module = "inherit module" in generated_code
    details.append(
        CheckDetail(
            check_name="inherits_module_class",
            passed=has_inherit_module,
            expected="inherit module present (handles KERNEL_SRC and kbuild automatically)",
            actual="present" if has_inherit_module else "MISSING (module won't build against kernel!)",
            check_type="constraint",
        )
    )

    # Check 2: KERNEL_MODULE_AUTOLOAD set (module loads at boot)
    # (LLM failure: module installed but not added to autoload list)
    has_autoload = "KERNEL_MODULE_AUTOLOAD" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_module_autoload_set",
            passed=has_autoload,
            expected="KERNEL_MODULE_AUTOLOAD set so module loads at boot",
            actual="present" if has_autoload else "missing (module not auto-loaded)",
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

    # Check 4: GPL license used (kernel modules must be GPL)
    # (LLM failure: MIT or BSD license for a kernel module — taints kernel)
    has_gpl = "GPL" in generated_code
    details.append(
        CheckDetail(
            check_name="gpl_license_used",
            passed=has_gpl,
            expected="GPL license (required for kernel modules to avoid taint)",
            actual="present" if has_gpl else "MISSING GPL (kernel taint warning!)",
            check_type="constraint",
        )
    )

    # Check 5: SRC_URI includes a Makefile or .c source file
    # (LLM failure: recipe with no source files referenced)
    has_makefile = "Makefile" in generated_code or ".c" in generated_code
    details.append(
        CheckDetail(
            check_name="source_files_in_src_uri",
            passed=has_makefile,
            expected="SRC_URI includes Makefile and/or .c source",
            actual="present" if has_makefile else "missing (nothing to build!)",
            check_type="constraint",
        )
    )

    # Check 6: No custom do_compile (module class handles it)
    # (LLM failure: writing do_compile that bypasses kbuild integration)
    has_custom_compile = "do_compile()" in generated_code
    details.append(
        CheckDetail(
            check_name="no_custom_do_compile",
            passed=not has_custom_compile,
            expected="No custom do_compile() — module class handles kbuild",
            actual="absent (correct)" if not has_custom_compile else "PRESENT (overrides module class!)",
            check_type="constraint",
        )
    )

    return details
