"""Static analysis checks for Yocto custom image recipe."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto image recipe structure."""
    details: list[CheckDetail] = []

    has_inherit = "inherit core-image" in generated_code or "inherit image" in generated_code
    details.append(
        CheckDetail(
            check_name="inherits_core_image",
            passed=has_inherit,
            expected="inherit core-image or inherit image",
            actual="present" if has_inherit else "missing (image recipe must inherit core-image)",
            check_type="exact_match",
        )
    )

    has_image_install = "IMAGE_INSTALL" in generated_code
    details.append(
        CheckDetail(
            check_name="image_install_defined",
            passed=has_image_install,
            expected="IMAGE_INSTALL defined with packages",
            actual="present" if has_image_install else "missing",
            check_type="exact_match",
        )
    )

    has_image_features = "IMAGE_FEATURES" in generated_code
    details.append(
        CheckDetail(
            check_name="image_features_defined",
            passed=has_image_features,
            expected="IMAGE_FEATURES defined",
            actual="present" if has_image_features else "missing",
            check_type="exact_match",
        )
    )

    has_summary = "SUMMARY" in generated_code
    details.append(
        CheckDetail(
            check_name="summary_defined",
            passed=has_summary,
            expected="SUMMARY defined",
            actual="present" if has_summary else "missing",
            check_type="exact_match",
        )
    )

    return details
