"""Behavioral checks for Linux workqueue driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate workqueue driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: INIT_WORK before schedule_work
    # (LLM failure: calling schedule_work on uninitialized work = kernel crash)
    has_init = "INIT_WORK" in generated_code
    has_schedule = "schedule_work" in generated_code
    details.append(
        CheckDetail(
            check_name="init_work_before_schedule",
            passed=has_init and has_schedule,
            expected="INIT_WORK() called before schedule_work()",
            actual=f"INIT_WORK={has_init}, schedule_work={has_schedule}",
            check_type="constraint",
        )
    )

    # Check 2: cancel_work_sync in exit (ensures work not running on unload)
    # (LLM failure: forgetting cancel = use-after-free when module unloads)
    has_cancel = "cancel_work_sync" in generated_code
    details.append(
        CheckDetail(
            check_name="cancel_work_sync_in_exit",
            passed=has_cancel,
            expected="cancel_work_sync() called in module_exit for safe shutdown",
            actual="present" if has_cancel else "MISSING (use-after-free risk on unload!)",
            check_type="constraint",
        )
    )

    # Check 3: No k_work_submit — Zephyr RTOS API, wrong platform
    # (Cross-platform LLM hallucination)
    has_zephyr_api = "k_work_submit" in generated_code
    details.append(
        CheckDetail(
            check_name="no_zephyr_k_work_submit",
            passed=not has_zephyr_api,
            expected="No k_work_submit() (Zephyr RTOS API, not Linux)",
            actual="clean" if not has_zephyr_api else "WRONG PLATFORM: k_work_submit is Zephyr, use schedule_work()",
            check_type="constraint",
        )
    )

    # Check 4: Work handler uses process context (should not use spin_lock_irq)
    # The work handler runs in process context and can sleep
    has_work_handler = "work_struct *work" in generated_code or "work_struct *" in generated_code
    details.append(
        CheckDetail(
            check_name="work_handler_process_context",
            passed=has_work_handler,
            expected="Work handler takes struct work_struct* parameter",
            actual="present" if has_work_handler else "missing",
            check_type="constraint",
        )
    )

    # Check 5: MODULE_LICENSE defined
    has_license = "MODULE_LICENSE" in generated_code
    details.append(
        CheckDetail(
            check_name="module_license_defined",
            passed=has_license,
            expected="MODULE_LICENSE defined",
            actual="present" if has_license else "missing",
            check_type="constraint",
        )
    )

    # Check 6: module_init and module_exit both present
    has_init_macro = "module_init" in generated_code
    has_exit_macro = "module_exit" in generated_code
    details.append(
        CheckDetail(
            check_name="init_exit_macros",
            passed=has_init_macro and has_exit_macro,
            expected="module_init() and module_exit() macros used",
            actual=f"init={has_init_macro}, exit={has_exit_macro}",
            check_type="constraint",
        )
    )

    return details
