"""Behavioral checks for Settings Key-Value Load with Default Fallback."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate settings load with default fallback behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: settings_subsys_init before settings_load (correct ordering)
    init_pos = generated_code.find("settings_subsys_init")
    load_pos = generated_code.find("settings_load")
    init_before_load = init_pos != -1 and load_pos != -1 and init_pos < load_pos
    details.append(
        CheckDetail(
            check_name="init_before_load",
            passed=init_before_load,
            expected="settings_subsys_init() before settings_load()",
            actual="correct order" if init_before_load else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Default fallback path present (if/else after load)
    # Look for conditional default assignment after settings_load
    import re
    has_default_branch = bool(
        re.search(r'if\s*\(\s*!?\s*\w*loaded\w*\s*\)', generated_code)
        or re.search(r'if\s*\(\s*!?\s*\w*found\w*\s*\)', generated_code)
        or re.search(r'setting_loaded\s*==\s*false|!setting_loaded', generated_code)
        or (re.search(r'else\s*\{', generated_code) and "DEFAULT" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="default_fallback_branch",
            passed=has_default_branch,
            expected="Explicit default fallback branch when setting not found",
            actual="present" if has_default_branch else "missing (no default on first boot!)",
            check_type="constraint",
        )
    )

    # Check 3: Both loaded and default paths print the value
    has_loaded_print = "loaded" in generated_code and ("printk" in generated_code or "printf" in generated_code)
    has_default_print = "default" in generated_code and ("printk" in generated_code or "printf" in generated_code)
    details.append(
        CheckDetail(
            check_name="both_paths_print_value",
            passed=has_loaded_print and has_default_print,
            expected="Both 'loaded' and 'default' paths print the setting value",
            actual=f"loaded_path={has_loaded_print} default_path={has_default_print}",
            check_type="constraint",
        )
    )

    # Check 4: Does not crash on empty storage (safe default handling)
    # Proxy check: no unchecked direct dereference pattern that would crash on first boot
    # The key indicator is having the default value assigned unconditionally at init or in else branch
    has_safe_default = bool(
        re.search(r'=\s*DEFAULT_VALUE', generated_code)
        or re.search(r'=\s*\d+\s*;.*//.*default', generated_code, re.IGNORECASE)
        or "DEFAULT" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="safe_on_empty_storage",
            passed=has_safe_default,
            expected="Default value assigned so first boot with empty storage is safe",
            actual="safe default present" if has_safe_default else "may crash on empty storage",
            check_type="constraint",
        )
    )

    # Check 5: h_set or settings_read_cb used in handler to store value
    has_read_cb = "read_cb" in generated_code or "settings_read_cb" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_read_cb_used",
            passed=has_read_cb,
            expected="settings_read_cb used in h_set handler to read value from storage",
            actual="present" if has_read_cb else "missing (value may not be stored from callback)",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
