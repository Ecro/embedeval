"""Static analysis checks for Settings Key-Value Load with Default Fallback."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate settings load with default fallback code structure."""
    details: list[CheckDetail] = []

    # Check 1: settings.h included
    has_settings_h = "zephyr/settings/settings.h" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_header_included",
            passed=has_settings_h,
            expected="zephyr/settings/settings.h included",
            actual="present" if has_settings_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Default value defined
    import re
    has_default = bool(
        re.search(r'#define\s+DEFAULT\w*\s+\d+', generated_code)
        or re.search(r'default_\w*\s*=\s*\d+', generated_code)
        or re.search(r'= DEFAULT', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="default_value_defined",
            passed=has_default,
            expected="Default value defined (e.g. #define DEFAULT_VALUE 42)",
            actual="present" if has_default else "missing (no default — crashes on first boot!)",
            check_type="constraint",
        )
    )

    # Check 3: settings_load called
    has_settings_load = "settings_load" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_load_called",
            passed=has_settings_load,
            expected="settings_load() called to load stored settings",
            actual="present" if has_settings_load else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: settings_subsys_init called before load
    has_subsys_init = "settings_subsys_init" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_subsys_init_called",
            passed=has_subsys_init,
            expected="settings_subsys_init() called before settings_load()",
            actual="present" if has_subsys_init else "missing (subsystem not initialized)",
            check_type="exact_match",
        )
    )

    # Check 5: Handler registered (settings_register or SETTINGS_STATIC_HANDLER_DEFINE)
    has_handler = (
        "settings_register" in generated_code
        or "SETTINGS_STATIC_HANDLER_DEFINE" in generated_code
        or "struct settings_handler" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="settings_handler_registered",
            passed=has_handler,
            expected="Settings handler registered (settings_register or SETTINGS_STATIC_HANDLER_DEFINE)",
            actual="present" if has_handler else "missing (no handler to receive loaded values)",
            check_type="constraint",
        )
    )

    # Check 6: Return value of settings_load checked
    load_ret_checked = bool(
        re.search(r'(ret|rc|err)\s*=\s*settings_load', generated_code)
        or re.search(r'if\s*\(\s*settings_load', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="settings_load_return_checked",
            passed=load_ret_checked,
            expected="Return value of settings_load() checked",
            actual="checked" if load_ret_checked else "return value ignored",
            check_type="constraint",
        )
    )

    return details
