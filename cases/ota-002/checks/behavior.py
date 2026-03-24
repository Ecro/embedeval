"""Behavioral checks for MCUboot swap type check."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate swap type check behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: All four swap type cases covered in a switch/if chain
    # (LLM failure: missing REVERT or PERM, only handling NONE and TEST)
    all_four = all(
        t in generated_code
        for t in [
            "BOOT_SWAP_TYPE_NONE",
            "BOOT_SWAP_TYPE_TEST",
            "BOOT_SWAP_TYPE_PERM",
            "BOOT_SWAP_TYPE_REVERT",
        ]
    )
    details.append(
        CheckDetail(
            check_name="all_swap_types_covered",
            passed=all_four,
            expected="All four swap types handled: NONE, TEST, PERM, REVERT",
            actual="all covered" if all_four else "incomplete coverage",
            check_type="constraint",
        )
    )

    # Check 2: Uses switch or if-else (not just printing a number)
    has_branch = "switch" in generated_code or (
        "if" in generated_code and "BOOT_SWAP_TYPE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="conditional_dispatch",
            passed=has_branch,
            expected="switch or if-else used to dispatch on swap type",
            actual="present" if has_branch else "missing (no branching logic)",
            check_type="constraint",
        )
    )

    # Check 3: Prints human-readable string, not just the integer value
    # (LLM failure: printk("Swap type: %d\n", swap_type))
    has_string_output = any(
        s in generated_code
        for s in ['"Swap type: NONE"', '"Swap type: TEST"', '"Swap type: PERM"', '"Swap type: REVERT"',
                  'Swap type: NONE', 'Swap type: TEST', 'Swap type: PERM', 'Swap type: REVERT']
    )
    details.append(
        CheckDetail(
            check_name="human_readable_output",
            passed=has_string_output,
            expected="Human-readable swap type string printed",
            actual="present" if has_string_output else "only numeric output (not human-readable)",
            check_type="constraint",
        )
    )

    # Check 4: mcuboot_swap_type() result is stored or directly used in switch
    # (LLM failure: calling swap_type multiple times)
    swap_call_count = generated_code.count("mcuboot_swap_type()")
    details.append(
        CheckDetail(
            check_name="swap_type_called_once",
            passed=swap_call_count >= 1,
            expected="mcuboot_swap_type() called at least once",
            actual=f"called {swap_call_count} time(s)",
            check_type="constraint",
        )
    )

    # Check 5: Completion message printed
    has_complete = "complete" in generated_code.lower() or "done" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="completion_message",
            passed=has_complete,
            expected="Completion message printed after swap type check",
            actual="present" if has_complete else "missing",
            check_type="constraint",
        )
    )

    # Check 6: default case handled in switch (or else clause for unrecognized type)
    # (LLM failure: no default case — unrecognized swap types silently ignored)
    has_default = "default" in generated_code or "UNKNOWN" in generated_code or "unknown" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="default_case_handled",
            passed=has_default,
            expected="default/unknown case handled in switch statement",
            actual="present" if has_default else "missing (unrecognized swap types not handled)",
            check_type="constraint",
        )
    )

    # Check 7: mcuboot_swap_type() return value stored before use
    # (LLM failure: calling mcuboot_swap_type() multiple times in switch arms)
    stored_before_use = (
        "swap_type" in generated_code
        and "mcuboot_swap_type()" in generated_code
        and generated_code.count("mcuboot_swap_type()") == 1
    )
    details.append(
        CheckDetail(
            check_name="swap_type_result_stored",
            passed=stored_before_use,
            expected="mcuboot_swap_type() called exactly once and result stored",
            actual="correct" if stored_before_use else "called multiple times or result not stored",
            check_type="constraint",
        )
    )

    return details
