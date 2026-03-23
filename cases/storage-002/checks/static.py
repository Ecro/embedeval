"""Static analysis checks for Settings subsystem load/save."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Settings subsystem code structure."""
    details: list[CheckDetail] = []

    # Check 1: Settings header included
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

    # Check 2: settings_subsys_init called
    has_init = "settings_subsys_init" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_subsys_init_called",
            passed=has_init,
            expected="settings_subsys_init() called",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: settings_save_one called
    has_save = "settings_save_one" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_save_one_called",
            passed=has_save,
            expected="settings_save_one() called",
            actual="present" if has_save else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: settings_load called
    has_load = "settings_load" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_load_called",
            passed=has_load,
            expected="settings_load() called",
            actual="present" if has_load else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: settings key uses namespace/key path format
    has_key_path = "/" in generated_code and (
        '"app/' in generated_code or "settings_save_one" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="settings_key_path_format",
            passed=has_key_path,
            expected="Settings key uses namespace/key path (e.g. 'app/mykey')",
            actual="present" if has_key_path else "missing",
            check_type="exact_match",
        )
    )

    return details
