"""Static analysis checks for linker section placement."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate linker section placement code structure."""
    details: list[CheckDetail] = []

    has_section_attr = '__attribute__((section(' in generated_code or 'Z_GENERIC_SECTION(' in generated_code
    details.append(
        CheckDetail(
            check_name="section_attribute_used",
            passed=has_section_attr,
            expected='__attribute__((section(...))) or Z_GENERIC_SECTION() used',
            actual="present" if has_section_attr else "MISSING (no section placement attribute)",
            check_type="exact_match",
        )
    )

    has_named_section = ".dma_buf" in generated_code or ".noinit" in generated_code or ".nocache" in generated_code
    details.append(
        CheckDetail(
            check_name="named_section_referenced",
            passed=has_named_section,
            expected="Named section (.dma_buf, .noinit, etc.) referenced",
            actual="present" if has_named_section else "missing",
            check_type="exact_match",
        )
    )

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

    has_buffer = "uint8_t" in generated_code and "[" in generated_code
    details.append(
        CheckDetail(
            check_name="buffer_defined",
            passed=has_buffer,
            expected="uint8_t buffer array defined",
            actual="present" if has_buffer else "missing",
            check_type="exact_match",
        )
    )

    return details
