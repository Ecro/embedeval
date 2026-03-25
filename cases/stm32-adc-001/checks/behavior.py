"""Behavioral checks for STM32 HAL ADC + DMA continuous conversion application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL ADC+DMA behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: DMA initialized before ADC (DMA must exist before ADC links to it)
    dma_init_pos = generated_code.find("HAL_DMA_Init")
    adc_init_pos = generated_code.find("HAL_ADC_Init")
    # Also accept: DMA init function called before ADC init function in main
    dma_fn_pos = -1
    for token in ["MX_DMA_Init", "DMA_Init", "HAL_DMA_Init"]:
        pos = generated_code.find(token)
        if pos != -1:
            dma_fn_pos = pos if dma_fn_pos == -1 else min(dma_fn_pos, pos)

    adc_fn_pos = -1
    for token in ["MX_ADC1_Init", "ADC1_Init", "HAL_ADC_Init"]:
        pos = generated_code.find(token)
        if pos != -1:
            adc_fn_pos = pos if adc_fn_pos == -1 else min(adc_fn_pos, pos)

    dma_before_adc = dma_fn_pos != -1 and adc_fn_pos != -1 and dma_fn_pos < adc_fn_pos
    details.append(
        CheckDetail(
            check_name="dma_initialized_before_adc",
            passed=dma_before_adc,
            expected="DMA initialized before ADC (ADC links to DMA handle)",
            actual="correct order" if dma_before_adc else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Continuous conversion mode enabled
    has_continuous = "ContinuousConvMode" in generated_code and "ENABLE" in generated_code
    details.append(
        CheckDetail(
            check_name="continuous_conv_mode_enabled",
            passed=has_continuous,
            expected="ContinuousConvMode = ENABLE",
            actual="present" if has_continuous else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: DMA continuous requests enabled
    # (LLM failure: enables continuous mode but not DMAContinuousRequests → DMA stops after first buffer)
    has_dma_cont = "DMAContinuousRequests" in generated_code and "ENABLE" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_continuous_requests_enabled",
            passed=has_dma_cont,
            expected="DMAContinuousRequests = ENABLE (required for circular DMA)",
            actual="present" if has_dma_cont else "missing — DMA stops after first fill",
            check_type="constraint",
        )
    )

    # Check 4: Conversion complete callback defined
    has_conv_cplt = "HAL_ADC_ConvCpltCallback" in generated_code
    details.append(
        CheckDetail(
            check_name="conv_complete_callback_defined",
            passed=has_conv_cplt,
            expected="HAL_ADC_ConvCpltCallback override defined",
            actual="present" if has_conv_cplt else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Error callback defined
    has_error_cb = "HAL_ADC_ErrorCallback" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_error_callback_defined",
            passed=has_error_cb,
            expected="HAL_ADC_ErrorCallback override defined",
            actual="present" if has_error_cb else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: ADC result buffer declared globally or statically
    # (LLM failure: stack buffer — DMA writes to stack which may go out of scope)
    has_global_buf = any(
        p in generated_code
        for p in ["static uint32_t", "static uint16_t", "uint32_t adc_buf", "uint16_t adc_buf"]
    )
    details.append(
        CheckDetail(
            check_name="adc_buffer_global_or_static",
            passed=has_global_buf,
            expected="ADC DMA buffer declared global or static (not on stack)",
            actual="present" if has_global_buf else "possibly on stack — unsafe for DMA",
            check_type="constraint",
        )
    )

    return details
