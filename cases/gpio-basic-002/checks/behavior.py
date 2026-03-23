"""Behavioral checks for UART echo application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate UART echo behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Device ready check before UART operations (AI failure: missing this)
    has_ready_check = any(
        p in generated_code
        for p in ["device_is_ready", "uart_is_ready"]
    )
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready_check,
            expected="device_is_ready() called before UART operations",
            actual="present" if has_ready_check else "missing",
            check_type="constraint",
        )
    )

    # Check 2: uart_poll_in return value checked (only echo on success)
    # AI failure pattern: calling uart_poll_out unconditionally without checking return
    poll_in_pos = generated_code.find("uart_poll_in")
    poll_out_pos = generated_code.find("uart_poll_out")
    # Check that poll_in result is used in a conditional (== 0, != -1, >= 0, etc.)
    has_conditional_echo = (
        poll_in_pos != -1
        and poll_out_pos != -1
        and any(
            p in generated_code
            for p in ["== 0", "!= -1", ">= 0", "if (uart_poll_in", "if(!uart_poll_in", "if (!uart_poll_in"]
        )
    )
    details.append(
        CheckDetail(
            check_name="poll_in_return_checked",
            passed=has_conditional_echo,
            expected="uart_poll_in return value checked before echoing",
            actual="checked" if has_conditional_echo else "unchecked or missing",
            check_type="constraint",
        )
    )

    # Check 3: Main loop present (while(1) or for(;;))
    has_loop = any(p in generated_code for p in ["while (1)", "while(1)", "for (;;)", "for(;;)"])
    details.append(
        CheckDetail(
            check_name="infinite_loop_present",
            passed=has_loop,
            expected="Infinite loop for continuous echo (while(1) or for(;;))",
            actual="present" if has_loop else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: No blocking sleep inside poll loop (AI failure: sleeping in tight poll loop
    # with a long delay defeats the purpose of poll-based echo)
    # Warn if k_msleep with large value appears — heuristic check
    has_long_sleep = "k_msleep(1000" in generated_code or "k_sleep(K_SECONDS" in generated_code
    details.append(
        CheckDetail(
            check_name="no_long_sleep_in_poll_loop",
            passed=not has_long_sleep,
            expected="No long blocking sleep inside poll loop",
            actual="long sleep found" if has_long_sleep else "no long sleep",
            check_type="constraint",
        )
    )

    # Check 5: No ISR callback used for simple poll implementation
    # (uart_irq_rx_enable is valid but the prompt asks for poll — penalise if both
    # poll API and IRQ are mixed, which is a common confusion pattern)
    has_poll_in = "uart_poll_in" in generated_code
    has_irq_rx = "uart_irq_rx_enable" in generated_code
    no_mixed_api = not (has_poll_in and has_irq_rx)
    details.append(
        CheckDetail(
            check_name="no_mixed_poll_and_irq_api",
            passed=no_mixed_api,
            expected="Uses poll API consistently, not mixed with IRQ API",
            actual="API consistent" if no_mixed_api else "mixed poll+IRQ API",
            check_type="constraint",
        )
    )

    # Check 6: Echo uses same byte read (not a hardcoded value)
    # Heuristic: uart_poll_out must appear after uart_poll_in in the same scope
    echo_order_ok = poll_in_pos != -1 and poll_out_pos != -1 and poll_in_pos < poll_out_pos
    details.append(
        CheckDetail(
            check_name="echo_order_correct",
            passed=echo_order_ok,
            expected="uart_poll_out called after uart_poll_in",
            actual="correct order" if echo_order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    return details
