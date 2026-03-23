"""Behavioral checks for PWM LED Device Tree overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PWM LED overlay behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Correct compatible string for pwm-leds (AI failure: uses "gpio-leds" or wrong string)
    has_pwm_leds = 'compatible = "pwm-leds"' in generated_code
    details.append(
        CheckDetail(
            check_name="pwm_leds_compatible",
            passed=has_pwm_leds,
            expected='compatible = "pwm-leds"',
            actual="present" if has_pwm_leds else "missing or wrong compatible string",
            check_type="exact_match",
        )
    )

    # Check 2: pwms property references pwm0 (AI failure: omits pwms or uses wrong controller)
    has_pwm0_ref = "&pwm0" in generated_code
    details.append(
        CheckDetail(
            check_name="pwm0_controller_referenced",
            passed=has_pwm0_ref,
            expected="&pwm0 phandle reference in pwms property",
            actual="present" if has_pwm0_ref else "missing or wrong PWM controller reference",
            check_type="exact_match",
        )
    )

    # Check 3: Channel 0 specified in pwms cell (AI failure: uses channel 1 or omits channel)
    # Valid forms: <&pwm0 0 ...>
    has_channel_0 = "pwm0 0 " in generated_code or "pwm0 0>" in generated_code
    details.append(
        CheckDetail(
            check_name="pwm_channel_0",
            passed=has_channel_0,
            expected="Channel 0 specified in pwms cell (e.g. <&pwm0 0 ...>)",
            actual="present" if has_channel_0 else "missing or wrong channel number",
            check_type="exact_match",
        )
    )

    # Check 4: Period value 20000000 ns present (AI failure: omits period or uses wrong unit)
    has_period = "20000000" in generated_code
    details.append(
        CheckDetail(
            check_name="period_20ms",
            passed=has_period,
            expected="Period of 20000000 ns (20ms) in pwms cell",
            actual="present" if has_period else "missing or wrong period value",
            check_type="exact_match",
        )
    )

    # Check 5: label = "green-led" (AI failure: omits label or uses wrong string)
    has_green_led_label = 'label = "green-led"' in generated_code
    details.append(
        CheckDetail(
            check_name="green_led_label",
            passed=has_green_led_label,
            expected='label = "green-led"',
            actual="present" if has_green_led_label else "missing or wrong label",
            check_type="exact_match",
        )
    )

    # Check 6: pwms property uses angle-bracket cell syntax
    has_pwms_cell = "pwms = <" in generated_code
    details.append(
        CheckDetail(
            check_name="pwms_cell_syntax",
            passed=has_pwms_cell,
            expected="pwms = <...> cell syntax",
            actual="present" if has_pwms_cell else "missing or wrong pwms syntax",
            check_type="exact_match",
        )
    )

    return details
