"""Behavioral checks for Zephyr stack size optimization Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Kconfig fragment behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: MAIN_STACK_SIZE value is at least 256 (not dangerously small)
    # (LLM failure: setting 128 or smaller — guaranteed stack overflow)
    main_stack_ok = False
    for line in generated_code.splitlines():
        if "CONFIG_MAIN_STACK_SIZE" in line and "=" in line:
            try:
                val = int(line.split("=")[-1].strip())
                main_stack_ok = val >= 256
            except ValueError:
                pass
    details.append(
        CheckDetail(
            check_name="main_stack_size_reasonable",
            passed=main_stack_ok,
            expected="CONFIG_MAIN_STACK_SIZE >= 256 (avoid stack overflow)",
            actual="ok" if main_stack_ok else "too small or missing (stack overflow risk)",
            check_type="constraint",
        )
    )

    # Check 2: ISR_STACK_SIZE value is at least 256
    # (LLM failure: setting ISR stack to tiny value = crash in any interrupt)
    isr_stack_ok = False
    for line in generated_code.splitlines():
        if "CONFIG_ISR_STACK_SIZE" in line and "=" in line:
            try:
                val = int(line.split("=")[-1].strip())
                isr_stack_ok = val >= 256
            except ValueError:
                pass
    details.append(
        CheckDetail(
            check_name="isr_stack_size_reasonable",
            passed=isr_stack_ok,
            expected="CONFIG_ISR_STACK_SIZE >= 256 (avoid ISR stack overflow)",
            actual="ok" if isr_stack_ok else "too small or missing",
            check_type="constraint",
        )
    )

    # Check 3: CONFIG_MINIMAL_LIBC=y (enabled, not just mentioned)
    has_minimal_libc_enabled = "CONFIG_MINIMAL_LIBC=y" in generated_code
    details.append(
        CheckDetail(
            check_name="minimal_libc_enabled_value",
            passed=has_minimal_libc_enabled,
            expected="CONFIG_MINIMAL_LIBC=y (not just defined, must be =y)",
            actual="enabled" if has_minimal_libc_enabled else "missing or not =y",
            check_type="constraint",
        )
    )

    # Check 4: NEWLIB_LIBC not enabled (conflicts with MINIMAL_LIBC)
    # (LLM failure: enabling both causes linker errors)
    has_newlib_enabled = "CONFIG_NEWLIB_LIBC=y" in generated_code
    details.append(
        CheckDetail(
            check_name="newlib_not_conflicting",
            passed=not has_newlib_enabled,
            expected="CONFIG_NEWLIB_LIBC=y absent (conflicts with MINIMAL_LIBC)",
            actual="absent (ok)" if not has_newlib_enabled else "PRESENT (conflict with MINIMAL_LIBC!)",
            check_type="constraint",
        )
    )

    # Check 5: HEAP_MEM_POOL_SIZE present and set to 0 (heap disabled)
    heap_disabled = "CONFIG_HEAP_MEM_POOL_SIZE=0" in generated_code
    details.append(
        CheckDetail(
            check_name="heap_disabled",
            passed=heap_disabled,
            expected="CONFIG_HEAP_MEM_POOL_SIZE=0 to disable system heap",
            actual="disabled" if heap_disabled else "missing or non-zero",
            check_type="constraint",
        )
    )

    return details
