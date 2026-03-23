"""Behavioral checks for wake timer from deep sleep."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate wakeup timer ordering and correctness."""
    details: list[CheckDetail] = []

    # Check 1: Timer started BEFORE pm_state_force
    # LLM failure: starting timer after requesting PM state (timer never fires before sleep)
    # Use regex to find the actual function call (not mentions in comments)
    timer_start_match = re.search(r"\bk_timer_start\s*\(", generated_code)
    pm_force_match = re.search(r"\bpm_state_force\s*\(", generated_code)
    timer_start_pos = timer_start_match.start() if timer_start_match else -1
    pm_force_pos = pm_force_match.start() if pm_force_match else -1
    timer_before_force = (
        timer_start_pos != -1 and pm_force_pos != -1 and timer_start_pos < pm_force_pos
    )
    details.append(
        CheckDetail(
            check_name="timer_started_before_pm_force",
            passed=timer_before_force,
            expected="k_timer_start() called BEFORE pm_state_force() (arm before sleep)",
            actual="correct order" if timer_before_force else "wrong order (timer after sleep!)",
            check_type="constraint",
        )
    )

    # Check 2: Timer initialized with k_timer_init
    has_timer_init = "k_timer_init" in generated_code
    details.append(
        CheckDetail(
            check_name="timer_initialized",
            passed=has_timer_init,
            expected="k_timer_init() called to initialize wakeup timer",
            actual="present" if has_timer_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Timer callback defined
    callback_match = re.search(
        r"void\s+\w*(?:wakeup|timer|cb|callback|wake)\w*\s*\(\s*struct\s+k_timer\s*\*",
        generated_code,
        re.IGNORECASE,
    )
    has_callback = callback_match is not None
    details.append(
        CheckDetail(
            check_name="timer_callback_defined",
            passed=has_callback,
            expected="Timer callback function defined",
            actual="present" if has_callback else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_timer_stop called after wakeup (cleanup)
    has_timer_stop = "k_timer_stop" in generated_code
    details.append(
        CheckDetail(
            check_name="timer_stopped_after_wakeup",
            passed=has_timer_stop,
            expected="k_timer_stop() called after wakeup to clean up",
            actual="present" if has_timer_stop else "missing",
            check_type="constraint",
        )
    )

    # Check 5: After-wakeup message printed
    has_wakeup_msg = bool(
        re.search(r"(return|wakeup|wake|resumed|awake)", generated_code, re.IGNORECASE)
    ) and "printk" in generated_code
    details.append(
        CheckDetail(
            check_name="wakeup_message_printed",
            passed=has_wakeup_msg,
            expected="Message printed after returning from deep sleep",
            actual="present" if has_wakeup_msg else "missing",
            check_type="constraint",
        )
    )

    return details
