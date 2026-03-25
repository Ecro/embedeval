"""Behavioral checks for STM32 HAL DMA memory-to-memory transfer application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL DMA M2M behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: DMA clock enabled before HAL_DMA_Init
    clk_pos = -1
    for token in ["__HAL_RCC_DMA2_CLK_ENABLE", "__HAL_RCC_DMA"]:
        pos = generated_code.find(token)
        if pos != -1:
            clk_pos = pos if clk_pos == -1 else min(clk_pos, pos)
    dma_init_pos = generated_code.find("HAL_DMA_Init")
    clock_before_init = clk_pos != -1 and dma_init_pos != -1 and clk_pos < dma_init_pos
    details.append(
        CheckDetail(
            check_name="dma_clock_before_init",
            passed=clock_before_init,
            expected="DMA2 clock enabled before HAL_DMA_Init",
            actual="correct order" if clock_before_init else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Source pointer increment enabled (M2M needs both src and dst to increment)
    # LLM failure: copies only one byte repeatedly because PINC disabled
    has_pinc_enable = "DMA_PINC_ENABLE" in generated_code
    details.append(
        CheckDetail(
            check_name="src_pointer_increment_enabled",
            passed=has_pinc_enable,
            expected="DMA_PINC_ENABLE set (source address must increment for M2M)",
            actual="present" if has_pinc_enable else "missing — source pointer static",
            check_type="constraint",
        )
    )

    # Check 3: Destination pointer increment enabled
    has_minc_enable = "DMA_MINC_ENABLE" in generated_code
    details.append(
        CheckDetail(
            check_name="dst_pointer_increment_enabled",
            passed=has_minc_enable,
            expected="DMA_MINC_ENABLE set (destination address must increment)",
            actual="present" if has_minc_enable else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Transfer complete callback registered or overridden
    has_cplt_callback = any(
        p in generated_code
        for p in [
            "HAL_DMA_XferCpltCallback",
            "HAL_DMA_RegisterCallback",
            "XferCpltCallback",
        ]
    )
    details.append(
        CheckDetail(
            check_name="transfer_complete_callback_registered",
            passed=has_cplt_callback,
            expected="DMA transfer complete callback registered or overridden",
            actual="present" if has_cplt_callback else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Data verification after transfer (memcmp or byte loop)
    has_verification = any(
        p in generated_code
        for p in ["memcmp", "verification", "verify", "compare"]
    )
    details.append(
        CheckDetail(
            check_name="data_verified_after_transfer",
            passed=has_verification,
            expected="Data verified after DMA transfer (memcmp or equivalent)",
            actual="present" if has_verification else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Buffers declared global or static (not on stack — DMA needs stable address)
    has_static_src = any(
        p in generated_code
        for p in ["static uint8_t src", "uint8_t src_buf", "static uint8_t source"]
    )
    has_static_dst = any(
        p in generated_code
        for p in ["static uint8_t dst", "uint8_t dst_buf", "static uint8_t dest"]
    )
    details.append(
        CheckDetail(
            check_name="dma_buffers_not_on_stack",
            passed=has_static_src and has_static_dst,
            expected="Source and destination buffers global or static (not stack)",
            actual=f"src={'ok' if has_static_src else 'stack?'} dst={'ok' if has_static_dst else 'stack?'}",
            check_type="constraint",
        )
    )

    return details
