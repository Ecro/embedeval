"""Static analysis checks for Linux sysfs attribute driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sysfs attribute driver code structure."""
    details: list[CheckDetail] = []

    has_module_h = "linux/module.h" in generated_code
    details.append(
        CheckDetail(
            check_name="module_header",
            passed=has_module_h,
            expected="linux/module.h included",
            actual="present" if has_module_h else "missing",
            check_type="exact_match",
        )
    )

    has_sysfs_h = "linux/sysfs.h" in generated_code
    details.append(
        CheckDetail(
            check_name="sysfs_header",
            passed=has_sysfs_h,
            expected="linux/sysfs.h included",
            actual="present" if has_sysfs_h else "missing",
            check_type="exact_match",
        )
    )

    has_license = "MODULE_LICENSE" in generated_code
    details.append(
        CheckDetail(
            check_name="module_license",
            passed=has_license,
            expected="MODULE_LICENSE defined",
            actual="present" if has_license else "missing",
            check_type="exact_match",
        )
    )

    has_device_attr_rw = "DEVICE_ATTR_RW" in generated_code
    details.append(
        CheckDetail(
            check_name="device_attr_rw_macro",
            passed=has_device_attr_rw,
            expected="DEVICE_ATTR_RW() macro used",
            actual="present" if has_device_attr_rw else "missing",
            check_type="exact_match",
        )
    )

    has_show = "_show" in generated_code
    details.append(
        CheckDetail(
            check_name="show_function",
            passed=has_show,
            expected="show function defined (name ending in _show)",
            actual="present" if has_show else "missing",
            check_type="exact_match",
        )
    )

    has_store = "_store" in generated_code
    details.append(
        CheckDetail(
            check_name="store_function",
            passed=has_store,
            expected="store function defined (name ending in _store)",
            actual="present" if has_store else "missing",
            check_type="exact_match",
        )
    )

    has_attr_group = "attribute_group" in generated_code
    details.append(
        CheckDetail(
            check_name="attribute_group_defined",
            passed=has_attr_group,
            expected="struct attribute_group defined",
            actual="present" if has_attr_group else "missing",
            check_type="exact_match",
        )
    )

    has_create_group = "sysfs_create_group" in generated_code
    details.append(
        CheckDetail(
            check_name="sysfs_create_group_called",
            passed=has_create_group,
            expected="sysfs_create_group() called in probe",
            actual="present" if has_create_group else "missing",
            check_type="exact_match",
        )
    )

    return details
