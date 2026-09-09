"""Behavioral checks for linux-userspace-007 (sd-bus vs libdbus).

Enforces:
  - sd-bus API selection (mandatory)
  - libdbus API absence (TC's discriminating trap — LLM default bias)
  - vtable declaration + method entry
  - bus name request + processing loop + cleanup
"""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    has_api_call,
    has_libdbus_api,
    has_sd_bus_api,
    scoped_contains,
    strip_comments,
)
from embedeval.models import CheckDetail
from embedeval.check_utils import expand_string_defines


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []
    stripped = strip_comments(generated_code)

    # 1. sd-bus API symbols present.
    sdb_found = set(has_sd_bus_api(generated_code))
    required_sdb = {
        "sd_bus_open_system",
        "sd_bus_add_object_vtable",
        "sd_bus_request_name",
        "sd_bus_process",
        "sd_bus_wait",
        "sd_bus_unref",
        "sd_bus_reply_method_return",
        "sd_bus_message_read",
    }
    missing_sdb = required_sdb - sdb_found
    details.append(
        CheckDetail(
            check_name="sd_bus_api_used",
            passed=not missing_sdb,
            expected="sd-bus core APIs: open_system, add_object_vtable, request_name, process, wait, reply_method_return, message_read, unref",
            actual=f"found: {sorted(sdb_found)}; missing: {sorted(missing_sdb)}",
            check_type="constraint",
        )
    )

    # 2. libdbus MUST be absent — discriminating trap.
    libdbus_found = has_libdbus_api(generated_code)
    details.append(
        CheckDetail(
            check_name="no_libdbus_api",
            passed=len(libdbus_found) == 0,
            expected="No libdbus symbols (dbus_bus_get, dbus_message_*, DBusConnection, ...)",
            actual="clean" if not libdbus_found else f"libdbus used: {libdbus_found}",
            check_type="constraint",
        )
    )

    # 3. vtable declared (SD_BUS_VTABLE_START + SD_BUS_VTABLE_END).
    has_vtable_start = "SD_BUS_VTABLE_START" in stripped
    has_vtable_end = "SD_BUS_VTABLE_END" in stripped
    details.append(
        CheckDetail(
            check_name="vtable_start_and_end_markers",
            passed=has_vtable_start and has_vtable_end,
            expected="Both SD_BUS_VTABLE_START and SD_BUS_VTABLE_END present",
            actual=f"start={has_vtable_start}, end={has_vtable_end}",
            check_type="constraint",
        )
    )

    # 4. SD_BUS_METHOD macro used with input/output signatures "s", "s".
    method_pat = re.search(
        r'SD_BUS_METHOD\s*\(\s*"Ping"\s*,\s*"s"\s*,\s*"s"', stripped
    )
    details.append(
        CheckDetail(
            check_name="ping_method_registered",
            passed=bool(method_pat),
            expected='SD_BUS_METHOD("Ping", "s", "s", callback, flags)',
            actual="present" if method_pat else "missing or wrong signature",
            check_type="constraint",
        )
    )

    # 5. Bus name request with com.embedeval.Example.
    # Naming the bus/interface once via `#define SERVICE_NAME "..."` is
    # equivalent to inlining the literal; expand string macros first.
    expanded = expand_string_defines(stripped)
    has_correct_name = bool(
        re.search(
            r'sd_bus_request_name\s*\([^,]+,\s*"com\.embedeval\.Example"',
            expanded,
        )
    )
    details.append(
        CheckDetail(
            check_name="bus_name_is_com_embedeval_example",
            passed=has_correct_name,
            expected='sd_bus_request_name(bus, "com.embedeval.Example", ...)',
            actual="present" if has_correct_name else "missing or wrong name",
            check_type="constraint",
        )
    )

    # 6. Processing loop alternates sd_bus_process + sd_bus_wait.
    has_process = has_api_call(stripped, "sd_bus_process")
    has_wait = has_api_call(stripped, "sd_bus_wait")
    details.append(
        CheckDetail(
            check_name="process_wait_loop_present",
            passed=has_process and has_wait,
            expected="sd_bus_process + sd_bus_wait used together",
            actual=f"process={has_process}, wait={has_wait}",
            check_type="constraint",
        )
    )

    # 7. Cleanup: sd_bus_unref OR sd_bus_flush_close_unref (the modern
    # atomic flush+close+unref) called on the bus. Accept either — the
    # latter is the idiomatic systemd-upstream recommendation.
    has_unref = has_api_call(stripped, "sd_bus_unref") or has_api_call(
        stripped, "sd_bus_flush_close_unref"
    )
    details.append(
        CheckDetail(
            check_name="bus_unref_on_exit",
            passed=has_unref,
            expected="sd_bus_unref(bus) or sd_bus_flush_close_unref(bus) on exit",
            actual="present" if has_unref else "missing",
            check_type="constraint",
        )
    )

    # 8. Object path "/com/embedeval/Example" present.
    has_object_path = (
        '"/com/embedeval/Example"' in stripped
    )
    details.append(
        CheckDetail(
            check_name="object_path_set",
            passed=has_object_path,
            expected='Object path "/com/embedeval/Example" used in add_object_vtable',
            actual="present" if has_object_path else "missing",
            check_type="constraint",
        )
    )

    # 9. Interface name appears in the sd_bus_add_object_vtable call
    # (not just anywhere in the file — otherwise renaming one reference
    # silently passes while the vtable registers under the wrong name).
    vtable_call_match = re.search(
        r'sd_bus_add_object_vtable\s*\([^;]*?"([^"]+)"\s*,\s*vtable|'
        r'sd_bus_add_object_vtable\s*\([^;]+;',
        stripped,
        re.DOTALL,
    )
    # Simpler: grep the call block for the interface string directly.
    vtable_block = re.search(
        r"sd_bus_add_object_vtable\s*\([^;]+;", expanded, re.DOTALL
    )
    has_interface = bool(vtable_block) and (
        '"com.embedeval.Example"' in vtable_block.group(0)
    )
    details.append(
        CheckDetail(
            check_name="interface_name_correct",
            passed=has_interface,
            expected='Interface "com.embedeval.Example" in add_object_vtable call',
            actual="present" if has_interface else "missing or renamed",
            check_type="constraint",
        )
    )

    # 10. Return value of sd_bus_open_system checked with ``< 0`` —
    # specifically for the open_system call. Slice from the open_system
    # call to the NEXT sd_bus_* call; the ``if (<var> < 0)`` check
    # must appear within that slice (before any subsequent API call
    # which would have its own error check). Variable name is NOT
    # hardcoded — accepts ``r``, ``ret``, ``rc``, ``err``, etc. per
    # CLAUDE.md 2026-04-19 rule on variable-name flexibility.
    open_sys_pos = stripped.find("sd_bus_open_system")
    open_sys_ok = False
    if open_sys_pos != -1:
        after = stripped[open_sys_pos + len("sd_bus_open_system") :]
        next_call = re.search(r"\bsd_bus_\w+\s*\(", after)
        end = next_call.start() if next_call else len(after)
        window = after[:end]
        open_sys_ok = bool(re.search(r"if\s*\(\s*\w+\s*<\s*0\s*\)", window))
    details.append(
        CheckDetail(
            check_name="error_propagation_r_lt_0",
            passed=open_sys_ok,
            expected="``if (<var> < 0)`` check between sd_bus_open_system and the next sd_bus_* call",
            actual="present" if open_sys_ok else "missing — open_system unchecked",
            check_type="constraint",
        )
    )
    _ = vtable_call_match  # silence unused-var; dual-regex kept for readability

    # 11. No cross-platform APIs.
    cross_plat = check_no_cross_platform_apis(
        generated_code, skip_platforms=["Linux_Userspace", "POSIX"]
    )
    details.append(
        CheckDetail(
            check_name="no_cross_platform_apis",
            passed=len(cross_plat) == 0,
            expected="No FreeRTOS / Zephyr / Arduino / STM32 HAL APIs",
            actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
            check_type="constraint",
        )
    )

    return details
