"""Behavioral checks for task watchdog application."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate task watchdog behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: task_wdt_init called before task_wdt_add (correct ordering)
    # AI failure: calling task_wdt_add before task_wdt_init
    init_pos = generated_code.find("task_wdt_init")
    add_pos = generated_code.find("task_wdt_add")
    init_before_add = init_pos != -1 and add_pos != -1 and init_pos < add_pos
    details.append(
        CheckDetail(
            check_name="init_before_add",
            passed=init_before_add,
            expected="task_wdt_init() called before task_wdt_add()",
            actual="correct order" if init_before_add else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: task_wdt_feed called from within the worker thread function
    # AI failure: feeding from main thread instead of the monitored thread
    # Heuristic: find the thread entry function and check if task_wdt_feed is inside it
    thread_fn_match = re.search(
        r"void\s+(\w+)\s*\(\s*void\s*\*[^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.DOTALL,
    )
    feed_in_thread = False
    if thread_fn_match:
        thread_body = thread_fn_match.group(2)
        feed_in_thread = "task_wdt_feed" in thread_body
    # Fallback: if thread body couldn't be extracted, check that task_wdt_feed
    # appears near a thread definition and NOT only inside main()
    if not feed_in_thread and not thread_fn_match:
        has_feed = "task_wdt_feed" in generated_code
        # Check it's associated with a thread, not just in main
        has_thread_def = bool(re.search(
            r"K_THREAD_DEFINE|k_thread_create", generated_code
        ))
        # Ensure feed is NOT only in main()
        main_match = re.search(
            r"\bmain\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
            generated_code,
            re.DOTALL,
        )
        feed_only_in_main = False
        if main_match and has_feed:
            feed_only_in_main = (
                "task_wdt_feed" in main_match.group(1)
                and generated_code.count("task_wdt_feed") == main_match.group(1).count("task_wdt_feed")
            )
        feed_in_thread = has_feed and has_thread_def and not feed_only_in_main
    details.append(
        CheckDetail(
            check_name="feed_from_worker_thread",
            passed=feed_in_thread,
            expected="task_wdt_feed() called from within the worker thread",
            actual="present in thread" if feed_in_thread else "missing or in wrong context",
            check_type="constraint",
        )
    )

    # Check 3: task_wdt_add return value checked or stored (channel ID used in feed)
    # AI failure: ignoring return value, then feeding channel -1 or 0 blindly
    add_result_stored = bool(
        re.search(r"(?:int\s+)?\w+\s*=\s*task_wdt_add\s*\(", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="channel_id_stored",
            passed=add_result_stored,
            expected="task_wdt_add() return value stored as channel ID",
            actual="stored" if add_result_stored else "return value ignored",
            check_type="constraint",
        )
    )

    # Check 4: Worker thread loops (not a one-shot function)
    has_loop_in_thread = bool(
        re.search(r"while\s*\(\s*1\s*\)|while\s*\(\s*true\s*\)|for\s*\(\s*;\s*;\s*\)", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="worker_thread_loops",
            passed=has_loop_in_thread,
            expected="Worker thread runs in an infinite loop",
            actual="present" if has_loop_in_thread else "missing - thread may exit",
            check_type="constraint",
        )
    )

    # Check 5: k_sleep present in worker loop (not busy-wait)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="worker_sleeps_between_feeds",
            passed=has_sleep,
            expected="k_sleep() used in worker loop between WDT feeds",
            actual="present" if has_sleep else "missing - may busy-wait",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
