"""Behavioral checks for Yocto custom image recipe."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto image recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: IMAGE_INSTALL uses += not = (avoid overriding base packages)
    # (LLM failure: IMAGE_INSTALL = "..." strips all base packages)
    has_append = (
        "IMAGE_INSTALL +=" in generated_code
        or "IMAGE_INSTALL:append" in generated_code
        or "IMAGE_INSTALL_append" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="image_install_uses_append",
            passed=has_append,
            expected="IMAGE_INSTALL uses += or :append (not = which overrides all)",
            actual="present" if has_append else "WRONG: IMAGE_INSTALL = overrides base packages",
            check_type="constraint",
        )
    )

    # Check 2: inherit core-image or image (not inherit package or other wrong class)
    has_core_image = "inherit core-image" in generated_code or "inherit image" in generated_code
    details.append(
        CheckDetail(
            check_name="inherits_correct_image_class",
            passed=has_core_image,
            expected="inherit core-image or inherit image",
            actual="present" if has_core_image else "MISSING or wrong class",
            check_type="constraint",
        )
    )

    # Check 3: No do_compile function (image recipes don't compile anything)
    has_do_compile = "do_compile" in generated_code
    details.append(
        CheckDetail(
            check_name="no_do_compile_in_image_recipe",
            passed=not has_do_compile,
            expected="No do_compile() in image recipe",
            actual="clean" if not has_do_compile else "WRONG: image recipes do not have do_compile",
            check_type="constraint",
        )
    )

    # Check 4: No do_install function (image recipes don't install like packages)
    has_do_install = "do_install" in generated_code
    details.append(
        CheckDetail(
            check_name="no_do_install_in_image_recipe",
            passed=not has_do_install,
            expected="No do_install() in image recipe",
            actual="clean" if not has_do_install else "WRONG: image recipes do not have do_install",
            check_type="constraint",
        )
    )

    # Check 5: At least one meaningful package listed
    has_packages = (
        "busybox" in generated_code
        or "packagegroup" in generated_code
        or "openssh" in generated_code
        or "bash" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="packages_listed",
            passed=has_packages,
            expected="At least one package listed in IMAGE_INSTALL",
            actual="present" if has_packages else "missing (empty image?)",
            check_type="constraint",
        )
    )

    # Check 6: SPDX license format (if LICENSE is set)
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
            expected="SPDX license identifier if set (GPL-2.0-only, not GPLv2)",
            actual="correct SPDX" if not has_non_spdx else "NON-SPDX license name found",
            check_type="constraint",
        )
    )

    # Check 7: Override syntax uses ':' not '_' (Yocto 4.0+ requirement)
    # (LLM failure: IMAGE_INSTALL_append instead of IMAGE_INSTALL:append)
    deprecated_override = re.search(
        r'\b(IMAGE_INSTALL|IMAGE_FEATURES|RDEPENDS|FILES|PACKAGES)_(?:append|prepend|\$\{PN\})',
        generated_code,
    )
    details.append(
        CheckDetail(
            check_name="colon_override_syntax",
            passed=deprecated_override is None,
            expected="Override syntax uses ':' (e.g. IMAGE_INSTALL:append, not IMAGE_INSTALL_append)",
            actual="correct" if deprecated_override is None else f"DEPRECATED '_' override: {deprecated_override.group(0)}",
            check_type="constraint",
        )
    )

    # Check 8: 'inherit' used for class, not 'require' or 'include'
    # (LLM failure: "require core-image" instead of "inherit core-image")
    has_require_class = bool(re.search(r'^require\s+(core-image|image)\b', generated_code, re.MULTILINE))
    details.append(
        CheckDetail(
            check_name="inherit_not_require_for_class",
            passed=not has_require_class,
            expected="'inherit core-image' not 'require core-image'",
            actual="correct" if not has_require_class else "WRONG: 'require' used instead of 'inherit'",
            check_type="constraint",
        )
    )

    # Check 9: No hardcoded absolute paths in image recipe (should use package names)
    has_hardcoded_path = bool(re.search(r'/usr/(bin|lib|sbin)\b', generated_code))
    details.append(
        CheckDetail(
            check_name="no_hardcoded_paths_in_image",
            passed=not has_hardcoded_path,
            expected="No hardcoded /usr/* paths in image recipe (use package names)",
            actual="correct" if not has_hardcoded_path else "hardcoded path found in image recipe",
            check_type="constraint",
        )
    )

    # Check 10: IMAGE_ROOTFS_SIZE uses ?= (weak assignment) or += (not hard =)
    # (LLM failure: IMAGE_ROOTFS_SIZE = ... overrides any board-specific value)
    has_rootfs_size = "IMAGE_ROOTFS_SIZE" in generated_code
    rootfs_uses_weak = (
        not has_rootfs_size
        or "IMAGE_ROOTFS_SIZE ?=" in generated_code
        or "IMAGE_ROOTFS_SIZE +=" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="rootfs_size_uses_weak_assignment",
            passed=rootfs_uses_weak,
            expected="IMAGE_ROOTFS_SIZE uses ?= (weak) not = (hard override)",
            actual="correct" if rootfs_uses_weak else "WRONG: hard = overrides board-specific size",
            check_type="constraint",
        )
    )

    return details
