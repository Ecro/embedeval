"""Static analysis checks for watchdog pre-timeout ISR callback application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog pre-timeout callback code structure."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/watchdog.h
    has_wdt_h = "zephyr/drivers/watchdog.h" in generated_code
    details.append(
        CheckDetail(
            check_name="watchdog_header_included",
            passed=has_wdt_h,
            expected="zephyr/drivers/watchdog.h included",
            actual="present" if has_wdt_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Includes zephyr/kernel.h
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Callback function defined with correct signature
    import re
    has_callback_fn = bool(
        re.search(
            r"(void|static void)\s+\w+\s*\(\s*const struct device\s*\*\s*\w*,\s*int\s+\w+\s*\)",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="callback_correct_signature",
            passed=has_callback_fn,
            expected="Callback with signature (const struct device*, int channel_id) defined",
            actual="present" if has_callback_fn else "missing or wrong signature",
            check_type="constraint",
        )
    )

    # Check 4: Callback registered in wdt_timeout_cfg (.callback field set)
    has_callback_set = ".callback" in generated_code and "NULL" not in re.sub(
        r"\.callback\s*=\s*NULL", "", generated_code
    )
    # More robust: check callback field is assigned to a non-NULL function
    has_non_null_callback = bool(re.search(r"\.callback\s*=\s*(?!NULL)\w+", generated_code))
    details.append(
        CheckDetail(
            check_name="callback_registered_non_null",
            passed=has_non_null_callback,
            expected=".callback field set to a function (not NULL)",
            actual="present" if has_non_null_callback else "missing or NULL",
            check_type="constraint",
        )
    )

    # Check 5: wdt_install_timeout and wdt_setup called
    has_install = "wdt_install_timeout" in generated_code
    has_setup = "wdt_setup" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_install_and_setup",
            passed=has_install and has_setup,
            expected="wdt_install_timeout() and wdt_setup() both called",
            actual=f"install={has_install}, setup={has_setup}",
            check_type="exact_match",
        )
    )

    # Check 6: WDT_FLAG_RESET_SOC used
    has_reset_flag = "WDT_FLAG_RESET_SOC" in generated_code
    details.append(
        CheckDetail(
            check_name="reset_soc_flag",
            passed=has_reset_flag,
            expected="WDT_FLAG_RESET_SOC used",
            actual="present" if has_reset_flag else "missing",
            check_type="exact_match",
        )
    )

    return details
