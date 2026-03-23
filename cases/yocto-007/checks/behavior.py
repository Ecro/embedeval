"""Behavioral checks for Yocto custom image recipe."""

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

    return details
