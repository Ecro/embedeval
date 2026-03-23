"""Static analysis checks for ADC single channel read application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ADC code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/adc.h
    has_adc_h = "zephyr/drivers/adc.h" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_header_included",
            passed=has_adc_h,
            expected="zephyr/drivers/adc.h included",
            actual="present" if has_adc_h else "missing",
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

    # Check 3: Uses ADC DT spec macro to get device
    has_dt_spec = any(
        p in generated_code
        for p in ["ADC_DT_SPEC_GET", "ADC_DT_SPEC_INST_GET"]
    )
    details.append(
        CheckDetail(
            check_name="uses_adc_dt_spec",
            passed=has_dt_spec,
            expected="ADC_DT_SPEC_GET macro used for devicetree binding",
            actual="present" if has_dt_spec else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Defines adc_sequence struct (AI failure: calling adc_read without sequence)
    has_adc_sequence = "adc_sequence" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_sequence_defined",
            passed=has_adc_sequence,
            expected="struct adc_sequence defined with buffer",
            actual="present" if has_adc_sequence else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Sample buffer declared (AI failure: no buffer allocated for sequence)
    has_buffer = any(
        p in generated_code
        for p in ["int16_t buf", "int16_t sample", "int16_t raw", "uint16_t buf", "uint16_t sample"]
    )
    details.append(
        CheckDetail(
            check_name="sample_buffer_declared",
            passed=has_buffer,
            expected="int16_t (or uint16_t) sample buffer declared",
            actual="present" if has_buffer else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No raw register access
    has_raw_register = any(
        p in generated_code for p in ["volatile uint32_t", "*(uint32_t*)", "MMIO"]
    )
    details.append(
        CheckDetail(
            check_name="no_raw_register_access",
            passed=not has_raw_register,
            expected="Uses ADC API, not raw register access",
            actual="raw register found" if has_raw_register else "API only",
            check_type="constraint",
        )
    )

    return details
