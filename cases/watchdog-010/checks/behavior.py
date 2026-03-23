"""Behavioral checks for task watchdog main thread monitoring application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate task watchdog behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: task_wdt_init before task_wdt_add (correct ordering)
    init_pos = generated_code.find("task_wdt_init")
    add_pos = generated_code.find("task_wdt_add")
    order_ok = init_pos != -1 and add_pos != -1 and init_pos < add_pos
    details.append(
        CheckDetail(
            check_name="init_before_add",
            passed=order_ok,
            expected="task_wdt_init called before task_wdt_add",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: task_wdt_add before task_wdt_feed
    feed_pos = generated_code.find("task_wdt_feed")
    add_before_feed = add_pos != -1 and feed_pos != -1 and add_pos < feed_pos
    details.append(
        CheckDetail(
            check_name="add_before_feed",
            passed=add_before_feed,
            expected="task_wdt_add called before task_wdt_feed",
            actual="correct order" if add_before_feed else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: feed period (sleep) < channel period (task_wdt_add period_ms)
    # Heuristic: find period_ms in task_wdt_add and sleep duration
    import re
    add_match = re.search(r"task_wdt_add\s*\(\s*(\d+)", generated_code)
    sleep_s_match = re.search(r"K_SECONDS\s*\(\s*(\d+)\s*\)", generated_code)
    sleep_ms_match = re.search(r"K_MSEC\s*\(\s*(\d+)\s*\)", generated_code)

    period_ms = int(add_match.group(1)) if add_match else 0
    sleep_ms = 0
    if sleep_s_match:
        sleep_ms = int(sleep_s_match.group(1)) * 1000
    elif sleep_ms_match:
        sleep_ms = int(sleep_ms_match.group(1))

    feed_period_ok = period_ms > 0 and sleep_ms > 0 and sleep_ms < period_ms
    details.append(
        CheckDetail(
            check_name="feed_period_less_than_wdt_period",
            passed=feed_period_ok,
            expected="Feed sleep < task_wdt_add period_ms (feed before timeout)",
            actual=f"sleep={sleep_ms}ms, period={period_ms}ms",
            check_type="constraint",
        )
    )

    # Check 4: task_wdt_feed called inside the loop
    loop_pos = max(generated_code.find("while"), generated_code.find("for ("))
    feed_in_loop = feed_pos != -1 and loop_pos != -1 and feed_pos > loop_pos
    details.append(
        CheckDetail(
            check_name="feed_in_loop",
            passed=feed_in_loop,
            expected="task_wdt_feed called inside the main loop",
            actual="inside loop" if feed_in_loop else "outside loop or missing",
            check_type="constraint",
        )
    )

    # Check 5: Error handling for task_wdt_add return value
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling_present",
            passed=has_error_check,
            expected="Return value of task_wdt_add() checked for error",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: printk used for heartbeat
    has_printk = "printk" in generated_code
    details.append(
        CheckDetail(
            check_name="heartbeat_printed",
            passed=has_printk,
            expected="printk() used for heartbeat messages",
            actual="present" if has_printk else "missing",
            check_type="exact_match",
        )
    )

    return details
