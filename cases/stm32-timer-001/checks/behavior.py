"""Behavioral checks for STM32 HAL TIM3 PWM 1kHz 50% duty cycle application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL PWM behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Prescaler and ARR values are consistent for 1kHz
    # With 84MHz timer clock: PSC=83 → tick=1MHz, ARR=999 → 1kHz
    # With 168MHz timer clock: PSC=167 → tick=1MHz, ARR=999 → 1kHz
    # Accept multiple valid combinations — check ARR * (PSC+1) / timer_clk ≈ 1ms
    # Simplified: look for ARR in range 99..9999 and PSC set
    arr_match = re.search(r"\.Period\s*=\s*(\d+)", generated_code)
    psc_match = re.search(r"\.Prescaler\s*=\s*(\d+)", generated_code)
    freq_ok = False
    if arr_match and psc_match:
        arr = int(arr_match.group(1))
        psc = int(psc_match.group(1))
        # Timer clock typically 84MHz (APB1*2) or 168MHz (APB2*1)
        for timer_clk in [84_000_000, 168_000_000, 42_000_000]:
            freq = timer_clk / ((psc + 1) * (arr + 1))
            if 900 <= freq <= 1100:  # within 10% of 1kHz
                freq_ok = True
                break
    details.append(
        CheckDetail(
            check_name="prescaler_arr_gives_1khz",
            passed=freq_ok,
            expected="Prescaler and ARR combination yields ~1kHz PWM",
            actual=f"PSC={psc_match.group(1) if psc_match else 'missing'} ARR={arr_match.group(1) if arr_match else 'missing'}",
            check_type="constraint",
        )
    )

    # Check 2: Compare value (CCR/Pulse) is approximately 50% of ARR
    ccr_match = re.search(r"\.Pulse\s*=\s*(\d+)", generated_code)
    duty_ok = False
    if ccr_match and arr_match:
        ccr = int(ccr_match.group(1))
        arr = int(arr_match.group(1))
        duty = ccr / (arr + 1)
        duty_ok = 0.40 <= duty <= 0.60  # 50% ± 10%
    details.append(
        CheckDetail(
            check_name="duty_cycle_approximately_50pct",
            passed=duty_ok,
            expected="Pulse (CCR) ~= ARR/2 for 50% duty cycle",
            actual=f"CCR={ccr_match.group(1) if ccr_match else 'missing'} ARR={arr_match.group(1) if arr_match else 'missing'}",
            check_type="constraint",
        )
    )

    # Check 3: TIM_CHANNEL_1 used (requirement specifies Channel 1)
    has_ch1 = "TIM_CHANNEL_1" in generated_code
    details.append(
        CheckDetail(
            check_name="tim_channel_1_used",
            passed=has_ch1,
            expected="TIM_CHANNEL_1 used",
            actual="present" if has_ch1 else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: PWM mode configured (OCMode = PWM1 or PWM2)
    has_pwm_mode = any(
        p in generated_code
        for p in ["TIM_OCMODE_PWM1", "TIM_OCMODE_PWM2"]
    )
    details.append(
        CheckDetail(
            check_name="pwm_oc_mode_configured",
            passed=has_pwm_mode,
            expected="TIM_OCMODE_PWM1 or PWM2 configured",
            actual="present" if has_pwm_mode else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Timer clock enabled before HAL_TIM_PWM_Init
    clk_pos = -1
    for token in ["__HAL_RCC_TIM3_CLK_ENABLE", "__HAL_RCC_TIM"]:
        pos = generated_code.find(token)
        if pos != -1:
            clk_pos = pos if clk_pos == -1 else min(clk_pos, pos)
    pwm_init_pos = generated_code.find("HAL_TIM_PWM_Init")
    clock_before_init = clk_pos != -1 and pwm_init_pos != -1 and clk_pos < pwm_init_pos
    details.append(
        CheckDetail(
            check_name="timer_clock_before_init",
            passed=clock_before_init,
            expected="TIM3 clock enabled before HAL_TIM_PWM_Init",
            actual="correct order" if clock_before_init else "wrong order or missing",
            check_type="constraint",
        )
    )

    return details
