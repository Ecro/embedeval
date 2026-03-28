"""Behavioral checks for Settings subsystem load/save."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Settings subsystem behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: settings_subsys_init before save/load (correct ordering)
    init_pos = generated_code.find("settings_subsys_init")
    save_pos = generated_code.find("settings_save_one")
    load_pos = generated_code.find("settings_load")
    init_first = (
        init_pos != -1
        and save_pos != -1
        and load_pos != -1
        and init_pos < save_pos
        and init_pos < load_pos
    )
    details.append(
        CheckDetail(
            check_name="init_before_save_load",
            passed=init_first,
            expected="settings_subsys_init() before settings_save_one/settings_load",
            actual="correct order" if init_first else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: settings_register before settings_load
    register_pos = generated_code.find("settings_register")
    register_before_load = (
        register_pos != -1 and load_pos != -1 and register_pos < load_pos
    )
    details.append(
        CheckDetail(
            check_name="register_before_load",
            passed=register_before_load,
            expected="settings_register() before settings_load()",
            actual="correct order" if register_before_load else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: save before load (write-then-verify pattern)
    save_before_load = (
        save_pos != -1 and load_pos != -1 and save_pos < load_pos
    )
    details.append(
        CheckDetail(
            check_name="save_before_load",
            passed=save_before_load,
            expected="settings_save_one() before settings_load() (verify pattern)",
            actual="correct" if save_before_load else "wrong order",
            check_type="constraint",
        )
    )

    # Check 4: error handling present
    has_error = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling",
            passed=has_error,
            expected="Error checks on Settings API return values",
            actual="present" if has_error else "missing",
            check_type="constraint",
        )
    )

    # Check 5: handler struct defined (settings_handler)
    has_handler = "settings_handler" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_handler_defined",
            passed=has_handler,
            expected="struct settings_handler defined for load callback",
            actual="present" if has_handler else "missing",
            check_type="exact_match",
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
