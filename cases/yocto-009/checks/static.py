"""Static analysis checks for Yocto machine configuration."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto machine .conf structure."""
    details: list[CheckDetail] = []

    has_machine_features = "MACHINE_FEATURES" in generated_code
    details.append(
        CheckDetail(
            check_name="machine_features_defined",
            passed=has_machine_features,
            expected="MACHINE_FEATURES defined",
            actual="present" if has_machine_features else "missing",
            check_type="exact_match",
        )
    )

    has_kernel_dt = "KERNEL_DEVICETREE" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_devicetree_defined",
            passed=has_kernel_dt,
            expected="KERNEL_DEVICETREE defined",
            actual="present" if has_kernel_dt else "missing",
            check_type="exact_match",
        )
    )

    has_serial = "SERIAL_CONSOLES" in generated_code
    details.append(
        CheckDetail(
            check_name="serial_consoles_defined",
            passed=has_serial,
            expected="SERIAL_CONSOLES defined",
            actual="present" if has_serial else "missing",
            check_type="exact_match",
        )
    )

    has_kernel_image = "KERNEL_IMAGETYPE" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_imagetype_defined",
            passed=has_kernel_image,
            expected="KERNEL_IMAGETYPE defined",
            actual="present" if has_kernel_image else "missing",
            check_type="exact_match",
        )
    )

    return details
