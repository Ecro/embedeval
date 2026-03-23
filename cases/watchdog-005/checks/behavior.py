"""Behavioral checks for watchdog with thread health monitoring application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog thread health monitoring behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: install_timeout before setup (correct ordering)
    install_pos = generated_code.find("wdt_install_timeout")
    setup_pos = generated_code.find("wdt_setup")
    order_ok = install_pos != -1 and setup_pos != -1 and install_pos < setup_pos
    details.append(
        CheckDetail(
            check_name="install_before_setup",
            passed=order_ok,
            expected="wdt_install_timeout() called before wdt_setup()",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Worker flag declared volatile (AI failure: non-volatile cross-thread flag)
    # Matches: volatile int worker_alive, volatile bool alive, volatile uint8_t health_flag, etc.
    has_volatile_flag = bool(
        re.search(r"volatile\s+\w+\s+\w*(?:alive|health|flag|ready)\w*", generated_code)
        or (
            "volatile" in generated_code
            and re.search(r"\b(?:worker_alive|alive|health_flag)\b", generated_code)
        )
    )
    details.append(
        CheckDetail(
            check_name="worker_flag_volatile",
            passed=has_volatile_flag,
            expected="Health flag declared volatile for cross-thread visibility",
            actual="volatile" if has_volatile_flag else "not volatile - compiler may cache",
            check_type="constraint",
        )
    )

    # Check 3: wdt_feed is conditional on health flag (not unconditional)
    # AI failure: always calling wdt_feed regardless of worker state
    # Look for wdt_feed inside an if-block that checks the health flag
    feed_is_conditional = bool(
        re.search(
            r"if\s*\([^)]*(?:alive|health|flag|worker)[^)]*\)[^{]*\{[^}]*wdt_feed",
            generated_code,
            re.DOTALL,
        )
        or re.search(
            r"if\s*\([^)]*(?:alive|health|flag|worker)[^)]*\).*?wdt_feed",
            generated_code,
            re.DOTALL,
        )
    )
    details.append(
        CheckDetail(
            check_name="wdt_feed_is_conditional",
            passed=feed_is_conditional,
            expected="wdt_feed() only called when worker health flag is set",
            actual="conditional" if feed_is_conditional else "unconditional - defeats purpose",
            check_type="constraint",
        )
    )

    # Check 4: Worker flag reset after checking (prevents stale value)
    # AI failure: checking flag but never resetting it (always appears alive)
    flag_reset = bool(
        re.search(
            r"(?:worker_alive|alive|health_flag)\s*=\s*0",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="flag_reset_after_check",
            passed=flag_reset,
            expected="Health flag reset to 0 after checking (so worker must set again)",
            actual="reset" if flag_reset else "not reset - worker always appears alive",
            check_type="constraint",
        )
    )

    # Check 5: Worker thread sets flag in a loop (periodically signals liveness)
    has_flag_set_in_loop = bool(
        re.search(
            r"(?:worker_alive|alive|health_flag)\s*=\s*1",
            generated_code,
        )
        and re.search(
            r"while\s*\(\s*1\s*\)|while\s*\(\s*true\s*\)|for\s*\(\s*;\s*;\s*\)",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="worker_sets_flag_in_loop",
            passed=has_flag_set_in_loop,
            expected="Worker thread sets health flag to 1 inside a loop",
            actual="present" if has_flag_set_in_loop else "missing",
            check_type="constraint",
        )
    )

    # Check 6: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() check before WDT operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    return details
