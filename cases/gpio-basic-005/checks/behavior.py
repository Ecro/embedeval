"""Behavioral checks for multi-LED sequential blink application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-LED GPIO behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: All LED pins configured as output before the main loop
    # (AI failure: calling gpio_pin_set_dt on unconfigured pins)
    has_output_config = "GPIO_OUTPUT" in generated_code
    config_pos = generated_code.find("gpio_pin_configure")
    set_pos = generated_code.find("gpio_pin_set_dt")
    toggle_pos = generated_code.find("gpio_pin_toggle_dt")
    first_drive_pos = min(
        p for p in [set_pos, toggle_pos] if p != -1
    ) if any(p != -1 for p in [set_pos, toggle_pos]) else -1

    pins_configured_before_drive = (
        has_output_config
        and config_pos != -1
        and first_drive_pos != -1
        and config_pos < first_drive_pos
    )
    details.append(
        CheckDetail(
            check_name="pins_configured_as_output_before_drive",
            passed=pins_configured_before_drive,
            expected="gpio_pin_configure_dt with GPIO_OUTPUT called before any gpio_pin_set_dt",
            actual="correct order" if pins_configured_before_drive else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Device ready check for LEDs (AI failure: no gpio_is_ready_dt call)
    has_ready_check = any(
        p in generated_code
        for p in ["gpio_is_ready_dt", "device_is_ready"]
    )
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready_check,
            expected="gpio_is_ready_dt() or device_is_ready() called for each LED",
            actual="present" if has_ready_check else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Delay between LED activations (AI failure: no sleep causes all LEDs
    # to appear constantly on or pattern too fast to observe)
    has_sleep = any(p in generated_code for p in ["k_sleep", "k_msleep"])
    details.append(
        CheckDetail(
            check_name="delay_between_leds",
            passed=has_sleep,
            expected="k_sleep or k_msleep between LED activations",
            actual="present" if has_sleep else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Sequential pattern — LEDs turned on then off one at a time
    # Look for both set(1) and set(0) or toggle pattern
    has_on = any(p in generated_code for p in ["gpio_pin_set_dt", "gpio_pin_toggle_dt"])
    has_off_or_toggle = (
        "gpio_pin_set_dt" in generated_code
        and (", 0)" in generated_code or ",0)" in generated_code)
    ) or "gpio_pin_toggle_dt" in generated_code
    details.append(
        CheckDetail(
            check_name="leds_turned_on_and_off",
            passed=has_on and has_off_or_toggle,
            expected="Each LED turned on then off (or toggled) in sequence",
            actual="present" if (has_on and has_off_or_toggle) else "missing off step",
            check_type="exact_match",
        )
    )

    # Check 5: Infinite loop present for continuous cycling
    has_loop = any(p in generated_code for p in ["while (1)", "while(1)", "for (;;)", "for(;;)"])
    details.append(
        CheckDetail(
            check_name="infinite_loop_present",
            passed=has_loop,
            expected="Infinite outer loop for continuous LED chaser",
            actual="present" if has_loop else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: LED array or repeated operations for all 4 LEDs
    # (AI failure: only wiring up led0 and forgetting led1..led3)
    covers_multiple_leds = (
        generated_code.count("led") >= 4
        or "NUM_LEDS" in generated_code
        or "ARRAY_SIZE" in generated_code
        or all(f"led{i}" in generated_code for i in range(1, 4))
    )
    details.append(
        CheckDetail(
            check_name="all_leds_driven",
            passed=covers_multiple_leds,
            expected="All 4 LEDs driven in sequence (not just led0)",
            actual="all LEDs covered" if covers_multiple_leds else "incomplete — missing LEDs",
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
