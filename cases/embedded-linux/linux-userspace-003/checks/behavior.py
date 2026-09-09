"""Behavioral checks for linux-userspace-003 (systemd watchdog triad).

The three-of-three correctness property:
  - Type=notify is REQUIRED for WatchdogSec to function
  - WatchdogSec must be a positive integer (seconds) or valid unit
  - Restart=on-watchdog (or always / on-failure family) is REQUIRED so
    a watchdog timeout actually triggers restart, not just a kill

Two-of-three = silent no-op: the service watchdog is configured but
either never listens for pings (Type=simple) or pings-missed kills
the daemon but nothing restarts it.
"""

import re

from embedeval.check_utils import systemd_unit_section_has
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # 1. [Service] Type=notify (mandatory for watchdog + sd_notify readiness).
    type_value = systemd_unit_section_has(generated_code, "Service", "Type")
    details.append(
        CheckDetail(
            check_name="type_notify_set",
            passed=type_value == "notify",
            expected="Type=notify (required for WatchdogSec / sd_notify)",
            actual=f"Type={type_value!r}" if type_value else "missing",
            check_type="constraint",
        )
    )

    # 2. WatchdogSec is a positive integer or systemd duration (we accept
    # bare integer "30" or "30s" or "30sec" or "1min").
    wdog = systemd_unit_section_has(generated_code, "Service", "WatchdogSec")
    wdog_ok = bool(wdog) and bool(
        re.match(r"^\d+(?:\s*(?:s|sec|seconds|min|minutes))?$", wdog.strip())
    )
    wdog_is_30 = bool(wdog) and re.match(r"^30(?:s|sec|seconds)?$", wdog.strip())
    details.append(
        CheckDetail(
            check_name="watchdog_sec_positive_duration",
            passed=wdog_ok,
            expected="WatchdogSec set to a positive duration",
            actual=f"WatchdogSec={wdog!r}" if wdog else "missing",
            check_type="constraint",
        )
    )
    details.append(
        CheckDetail(
            check_name="watchdog_sec_matches_30s_requirement",
            passed=bool(wdog_is_30),
            expected="WatchdogSec=30 (or 30s / 30sec) — per prompt requirement",
            actual=f"WatchdogSec={wdog!r}" if wdog else "missing",
            check_type="constraint",
        )
    )

    # 3. Restart must cover the watchdog-kill case. Valid values:
    #    on-watchdog (specific), always, on-abnormal, on-failure (covers
    #    SIGABRT from watchdog since exit code is non-zero).
    # Invalid: no, on-success. on-abort alone is borderline — it doesn't
    # clearly document watchdog intent; we reject here.
    restart = systemd_unit_section_has(generated_code, "Service", "Restart")
    restart_covers_watchdog = restart in {
        "on-watchdog",
        "always",
        "on-abnormal",
        "on-failure",
    }
    details.append(
        CheckDetail(
            check_name="restart_covers_watchdog_timeout",
            passed=restart_covers_watchdog,
            expected="Restart set to on-watchdog / always / on-abnormal / on-failure",
            actual=f"Restart={restart!r}" if restart else "missing",
            check_type="constraint",
        )
    )

    # 4. RestartSec cool-down set to ≥1 second (5 per prompt, but accept
    # any reasonable positive integer — the classic LLM bug is 0 or
    # unset which causes restart storm).
    restart_sec = systemd_unit_section_has(generated_code, "Service", "RestartSec")
    restart_sec_match = (
        re.match(r"^(\d+)(?:\s*(?:s|sec|seconds))?$", restart_sec.strip())
        if restart_sec
        else None
    )
    restart_sec_ok = bool(restart_sec_match) and int(restart_sec_match.group(1)) >= 1
    details.append(
        CheckDetail(
            check_name="restart_sec_positive",
            passed=restart_sec_ok,
            expected="RestartSec set to ≥1 second (avoids restart storm)",
            actual=f"RestartSec={restart_sec!r}" if restart_sec else "missing",
            check_type="constraint",
        )
    )

    # 5. StartLimitBurst + StartLimitIntervalSec paired — if one exists
    # without the other, ratelimit is undefined.
    # Since systemd v229 the start rate limiter lives in [Unit]; systemd 250
    # ignores these keys under [Service]. Demanding [Service] rewarded a unit
    # file that silently has no rate limit at all, so accept either section
    # and prefer [Unit].
    burst = systemd_unit_section_has(
        generated_code, "Unit", "StartLimitBurst"
    ) or systemd_unit_section_has(generated_code, "Service", "StartLimitBurst")
    interval = systemd_unit_section_has(
        generated_code, "Unit", "StartLimitIntervalSec"
    ) or systemd_unit_section_has(
        generated_code, "Service", "StartLimitIntervalSec"
    )
    both_or_neither = (burst is None) == (interval is None)
    both_present = burst is not None and interval is not None
    details.append(
        CheckDetail(
            check_name="start_limit_burst_and_interval_paired",
            passed=bool(both_present),
            expected="StartLimitBurst + StartLimitIntervalSec both set",
            actual=f"burst={burst!r}, interval={interval!r}",
            check_type="constraint",
        )
    )
    details.append(
        CheckDetail(
            check_name="start_limit_not_half_declared",
            passed=both_or_neither,
            expected="Either both of (StartLimitBurst, StartLimitIntervalSec) set or neither",
            actual=f"burst={burst!r}, interval={interval!r}",
            check_type="constraint",
        )
    )

    # 6. ExecStart is an absolute path.
    exec_start = systemd_unit_section_has(generated_code, "Service", "ExecStart")
    exec_abs = bool(exec_start) and exec_start.lstrip().startswith("/")
    details.append(
        CheckDetail(
            check_name="exec_start_absolute_path",
            passed=exec_abs,
            expected="ExecStart begins with an absolute path",
            actual=f"ExecStart={exec_start!r}" if exec_start else "missing",
            check_type="constraint",
        )
    )

    # 7. After=network.target ordering.
    after = systemd_unit_section_has(generated_code, "Unit", "After")
    after_network = bool(after) and "network.target" in after
    details.append(
        CheckDetail(
            check_name="after_network_target",
            passed=after_network,
            expected="After=network.target in [Unit]",
            actual=f"After={after!r}" if after else "missing",
            check_type="constraint",
        )
    )

    # 8. WantedBy=multi-user.target.
    wanted_by = systemd_unit_section_has(generated_code, "Install", "WantedBy")
    mu_target = bool(wanted_by) and "multi-user.target" in wanted_by
    details.append(
        CheckDetail(
            check_name="wantedby_multi_user_target",
            passed=mu_target,
            expected="WantedBy=multi-user.target in [Install]",
            actual=f"WantedBy={wanted_by!r}" if wanted_by else "missing",
            check_type="constraint",
        )
    )

    # 9. Guard against Type=simple + WatchdogSec (silent no-op — watchdog
    # ignored because sd_notify readiness never arrives).
    type_is_simple_with_watchdog = type_value == "simple" and wdog is not None
    details.append(
        CheckDetail(
            check_name="no_watchdog_with_simple_type",
            passed=not type_is_simple_with_watchdog,
            expected="WatchdogSec not combined with Type=simple (watchdog inert)",
            actual=(
                "WRONG: simple+watchdog" if type_is_simple_with_watchdog else "clean"
            ),
            check_type="constraint",
        )
    )

    return details
