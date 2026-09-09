"""Behavioral checks for watchdog with NVS persistent reboot counter."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog + NVS behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: NVS read before watchdog setup (ordering)
    nvs_read_pos = -1
    for pattern in ["nvs_read", "settings_runtime_get", "settings_load"]:
        pos = find_in_code(generated_code, pattern)
        if pos != -1:
            nvs_read_pos = pos
            break

    wdt_setup_pos = find_in_code(generated_code, "wdt_setup")
    wdt_install_pos = find_in_code(generated_code, "wdt_install_timeout")
    wdt_pos = min(
        p for p in [wdt_setup_pos, wdt_install_pos] if p != -1
    ) if any(p != -1 for p in [wdt_setup_pos, wdt_install_pos]) else -1

    read_before_wdt = nvs_read_pos != -1 and wdt_pos != -1 and nvs_read_pos < wdt_pos
    details.append(
        CheckDetail(
            check_name="nvs_read_before_watchdog_setup",
            passed=read_before_wdt,
            expected="NVS read before watchdog setup (must know reboot count first)",
            actual="correct order" if read_before_wdt else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Counter threshold comparison (escalation logic)
    has_threshold = bool(
        re.search(
            r"(reboot|boot|counter|count)\s*[><=!]+\s*\d|"
            r"\d+\s*[><=!]+\s*(reboot|boot|counter|count)|"
            r"MAX_REBOOT|REBOOT_THRESHOLD|MAX_BOOT",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="counter_threshold_comparison",
            passed=has_threshold,
            expected="Reboot counter compared against threshold for escalation",
            actual="present" if has_threshold else "missing — no escalation logic",
            check_type="constraint",
        )
    )

    # Check 3: NVS write (increment counter)
    has_nvs_write = bool(
        re.search(r"nvs_write|settings_save|settings_runtime_set", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="nvs_write_counter",
            passed=has_nvs_write,
            expected="NVS write to persist incremented counter",
            actual="present" if has_nvs_write else "missing — counter not persisted",
            check_type="exact_match",
        )
    )

    # Check 4: Counter reset to 0 after stable period (the key insight)
    # Look for writing 0 back to NVS after a delay/stable period
    has_counter_reset = bool(
        re.search(
            r"=\s*0\s*;.*nvs_write|nvs_write.*\b0\b|"
            r"counter\s*=\s*0|count\s*=\s*0|"
            r"reset.*counter|counter.*reset|clear.*counter",
            generated_code,
            re.IGNORECASE | re.DOTALL,
        )
    )
    details.append(
        CheckDetail(
            check_name="counter_reset_after_stable",
            passed=has_counter_reset,
            expected="Counter reset to 0 in NVS after stable operation period",
            actual="present"
            if has_counter_reset
            else "missing — counter never cleared",
            check_type="constraint",
        )
    )

    # Check 5: wdt_setup called
    has_wdt_setup = scoped_contains(generated_code, 'wdt_setup', scope='code_only')
    details.append(
        CheckDetail(
            check_name="wdt_setup_called",
            passed=has_wdt_setup,
            expected="wdt_setup() called to start watchdog",
            actual="present" if has_wdt_setup else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: wdt_feed called
    has_wdt_feed = scoped_contains(generated_code, 'wdt_feed', scope='code_only')
    details.append(
        CheckDetail(
            check_name="wdt_feed_called",
            passed=has_wdt_feed,
            expected="wdt_feed() called to periodically reset watchdog",
            actual="present" if has_wdt_feed else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: Two distinct code paths (normal vs recovery mode)
    has_normal_mode = bool(
        re.search(r"normal|NORMAL|regular|REGULAR", generated_code)
    )
    has_recovery_mode = bool(
        re.search(r"recovery|RECOVERY|safe|SAFE|fallback|FALLBACK", generated_code)
    )
    has_two_paths = has_normal_mode and has_recovery_mode
    details.append(
        CheckDetail(
            check_name="two_distinct_code_paths",
            passed=has_two_paths,
            expected="Two distinct modes: normal operation and recovery/safe mode",
            actual=(
                f"normal={'yes' if has_normal_mode else 'no'}, "
                f"recovery={'yes' if has_recovery_mode else 'no'}"
            ),
            check_type="constraint",
        )
    )

    # Check 8: wdt_install_timeout called
    has_install_timeout = scoped_contains(generated_code, 'wdt_install_timeout', scope='code_only')
    details.append(
        CheckDetail(
            check_name="wdt_install_timeout_called",
            passed=has_install_timeout,
            expected="wdt_install_timeout() called to configure watchdog timeout",
            actual="present" if has_install_timeout else "missing",
            check_type="exact_match",
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
