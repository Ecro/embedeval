"""Behavioral checks for linker section placement for DMA buffers."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate linker section placement behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: section attribute present (GCC standard)
    has_section = (
        '__attribute__((section(' in generated_code
        or 'Z_GENERIC_SECTION(' in generated_code
        or '__attribute__ ((section(' in generated_code
    )
    details.append(
        CheckDetail(
            check_name="gcc_section_attribute_used",
            passed=has_section,
            expected='GCC __attribute__((section(...))) or Z_GENERIC_SECTION used',
            actual="present" if has_section else "MISSING (buffer not in named section)",
            check_type="constraint",
        )
    )

    # Check 2: Buffer is in a named section (not default .bss)
    has_named = ".dma_buf" in generated_code or ".noinit" in generated_code or ".nocache" in generated_code
    details.append(
        CheckDetail(
            check_name="buffer_in_named_section",
            passed=has_named,
            expected="Buffer placed in named section (.dma_buf, .noinit, .nocache, etc.)",
            actual="present" if has_named else "MISSING (buffer stays in default .bss)",
            check_type="constraint",
        )
    )

    # Check 3: No __attribute__((at(...))) — Keil/MDK-ARM specific, not GCC
    # (LLM hallucination: using Keil AT() attribute in GCC code)
    has_at_attr = "__attribute__((at(" in generated_code or "__attribute__ ((at(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_keil_at_attribute",
            passed=not has_at_attr,
            expected="No __attribute__((at(address))) — Keil-specific, not GCC",
            actual="clean" if not has_at_attr else "HALLUCINATION: __attribute__((at())) is Keil/MDK only!",
            check_type="constraint",
        )
    )

    # Check 4: No hardcoded volatile pointer to fixed address
    # e.g., volatile uint8_t *ptr = (volatile uint8_t *)0x20000000;
    import re
    has_fixed_addr = bool(re.search(r'\(\s*volatile\s+\w+\s*\*\s*\)\s*0x[0-9a-fA-F]+', generated_code))
    details.append(
        CheckDetail(
            check_name="no_hardcoded_memory_address",
            passed=not has_fixed_addr,
            expected="No hardcoded memory address cast (not portable)",
            actual="clean" if not has_fixed_addr else "hardcoded address found (use section attribute instead)",
            check_type="constraint",
        )
    )

    # Check 5: aligned() or __aligned() for cache alignment (DMA best practice)
    has_aligned = (
        "aligned(" in generated_code
        or "__aligned(" in generated_code
        or "ALIGN" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="alignment_specified",
            passed=has_aligned,
            expected="Buffer alignment specified (aligned() for DMA cache coherency)",
            actual="present" if has_aligned else "missing (DMA buffers should be cache-line aligned)",
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
