"""Static analysis checks for ISR-deferred k_work processing."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_work ISR safety constraints."""
    details: list[CheckDetail] = []

    # Check 1: struct k_work declared
    has_kwork = "struct k_work" in generated_code
    details.append(
        CheckDetail(
            check_name="k_work_declared",
            passed=has_kwork,
            expected="struct k_work declared",
            actual="present" if has_kwork else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: k_work_init called (LLM failure: missing init, or called inside ISR)
    has_init = "k_work_init" in generated_code
    details.append(
        CheckDetail(
            check_name="k_work_init_called",
            passed=has_init,
            expected="k_work_init() called (in main, before ISR fires)",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: k_work_init NOT called inside isr_handler (must be before ISR fires)
    isr_block = re.search(
        r'(isr_handler|ISR|irq_handler)\s*\([^{]*\)\s*\{([^}]*)\}',
        generated_code, re.IGNORECASE | re.DOTALL
    )
    isr_has_init = False
    if isr_block:
        isr_has_init = "k_work_init" in isr_block.group(2)
    details.append(
        CheckDetail(
            check_name="k_work_init_not_in_isr",
            passed=not isr_has_init,
            expected="k_work_init() must NOT be called inside ISR",
            actual="violation found" if isr_has_init else "clean",
            check_type="constraint",
        )
    )

    # Check 4: k_work_submit called in ISR (triggers deferred processing)
    has_submit = "k_work_submit" in generated_code
    details.append(
        CheckDetail(
            check_name="k_work_submit_called",
            passed=has_submit,
            expected="k_work_submit() called",
            actual="present" if has_submit else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Work handler takes struct k_work * parameter (correct signature)
    has_correct_sig = bool(re.search(
        r'\w+\s*\(\s*struct\s+k_work\s*\*', generated_code
    ))
    details.append(
        CheckDetail(
            check_name="work_handler_correct_signature",
            passed=has_correct_sig,
            expected="Work handler takes (struct k_work *) parameter",
            actual="present" if has_correct_sig else "missing or wrong signature",
            check_type="constraint",
        )
    )

    # Check 6: k_work_init called BEFORE isr_handler invocation in main
    # Use regex to find a *call* to isr_handler (preceded by ; { or newline, not 'void')
    # This avoids matching the function definition line.
    init_pos = generated_code.find("k_work_init")
    isr_calls = list(re.finditer(r'(?<![a-zA-Z_])isr_handler\s*\(', generated_code))
    # Filter out the definition: a call is not preceded by a return type keyword on the same line
    isr_call_positions = []
    for m in isr_calls:
        line_start = generated_code.rfind('\n', 0, m.start()) + 1
        line = generated_code[line_start:m.start()]
        if not re.search(r'\b(void|static|inline)\b', line):
            isr_call_positions.append(m.start())
    first_isr_call = isr_call_positions[0] if isr_call_positions else -1
    details.append(
        CheckDetail(
            check_name="init_before_isr_call",
            passed=init_pos != -1 and first_isr_call != -1 and init_pos < first_isr_call,
            expected="k_work_init() before first isr_handler() call in main",
            actual="correct" if (init_pos != -1 and first_isr_call != -1 and init_pos < first_isr_call) else "wrong order or missing",
            check_type="constraint",
        )
    )

    return details
