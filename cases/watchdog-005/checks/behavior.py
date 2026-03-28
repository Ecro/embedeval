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

    # Check 7: Health/alive flag must NOT be a plain int without volatile/atomic
    # LLM failure: `static int health = 0` allows compiler to cache the value across threads
    # Simplified: check if volatile or atomic_t appears on the flag declaration line
    flag_patterns = [
        r'volatile\s+\w+\s+\w*(?:health|alive|running|ok)\w*',
        r'atomic_t\s+\w*(?:health|alive|running|ok)\w*',
    ]
    has_safe_qualifier = any(re.search(p, generated_code) for p in flag_patterns)
    # Also accept atomic_set / atomic_get usage on the flag
    flag_var_match = re.search(
        r"\b(\w*(?:health|alive|flag|running)\w*)\s*[=;]", generated_code
    )
    flag_is_safe = has_safe_qualifier
    if not flag_is_safe and flag_var_match:
        flag_name = flag_var_match.group(1)
        # Accept atomic_set / atomic_get usage
        has_atomic_ops = bool(
            re.search(rf"atomic_(?:set|get|cas)\s*\(\s*&?\s*{re.escape(flag_name)}", generated_code)
        )
        # Check if volatile appears on the same line as the flag declaration
        decl_line_match = re.search(
            rf"volatile[^\n]*{re.escape(flag_name)}|{re.escape(flag_name)}[^\n]*volatile",
            generated_code,
        )
        flag_is_safe = has_atomic_ops or (decl_line_match is not None)
    details.append(
        CheckDetail(
            check_name="health_flag_not_plain_int",
            passed=flag_is_safe,
            expected="Health/alive flag declared volatile or atomic_t (not plain int)",
            actual="safe (volatile/atomic)" if flag_is_safe else "plain int - compiler may cache value",
            check_type="constraint",
        )
    )

    # Check 8: Feed loop interval must be less than WDT timeout to ensure timely feeding
    # LLM failure: sleep interval >= wdt timeout means watchdog fires before being fed
    wdt_timeout_match = re.search(
        r"\.window\s*\.\s*max\s*=\s*(\d+)|window\.max\s*=\s*(\d+)",
        generated_code,
    )
    feed_interval_match = re.search(
        r"k_sleep\s*\(\s*K_MSEC\s*\(\s*(\d+)\s*\)\s*\)|"
        r"k_sleep\s*\(\s*K_SECONDS\s*\(\s*(\d+)\s*\)\s*\)",
        generated_code,
    )
    timing_margin_ok = True  # default pass if values cannot be extracted
    if wdt_timeout_match and feed_interval_match:
        wdt_ms = int(wdt_timeout_match.group(1) or wdt_timeout_match.group(2))
        if feed_interval_match.group(1):
            feed_ms = int(feed_interval_match.group(1))
        else:
            feed_ms = int(feed_interval_match.group(2)) * 1000
        timing_margin_ok = feed_ms < wdt_ms
    details.append(
        CheckDetail(
            check_name="feed_interval_less_than_wdt_timeout",
            passed=timing_margin_ok,
            expected="Feed loop sleep interval < WDT timeout (must feed before timeout fires)",
            actual=(
                f"feed={feed_ms}ms < wdt={wdt_ms}ms: ok"
                if (wdt_timeout_match and feed_interval_match and timing_margin_ok)
                else (
                    f"feed={feed_ms}ms >= wdt={wdt_ms}ms: TOO SLOW"
                    if (wdt_timeout_match and feed_interval_match)
                    else "could not extract timing values"
                )
            ),
            check_type="constraint",
        )
    )

    return details
