"""Behavioral checks for sensor-filter-UART task architecture."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    extract_function_body,
    strip_comments,
)
from embedeval.models import CheckDetail


def _extract_defines(code: str) -> dict[str, int]:
    """Return all #define NAME NUMBER entries as a name->int dict."""
    return {
        name: int(val)
        for name, val in re.findall(r'#define\s+(\w+)\s+(-?\d+)', code)
    }


def _resolve_int(token: str, defines: dict[str, int]) -> int | None:
    """Resolve a token to an integer — direct literal or via #define lookup."""
    try:
        return int(token)
    except ValueError:
        return defines.get(token)


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []
    stripped = strip_comments(generated_code)
    defines = _extract_defines(stripped)

    # Check 1: At least 2 threads defined (task decomposition)
    thread_defs = len(re.findall(r'K_THREAD_DEFINE|k_thread_create', stripped))
    details.append(CheckDetail(
        check_name="multiple_threads",
        passed=thread_defs >= 2,
        expected="At least 2 threads (sensor and output separated)",
        actual=f"{thread_defs} thread definitions found",
        check_type="constraint",
    ))

    # Check 2: Inter-thread communication (not shared globals)
    has_ipc = any(kw in stripped for kw in [
        "k_msgq", "k_fifo", "k_pipe", "k_mbox", "k_queue",
    ])
    details.append(CheckDetail(
        check_name="inter_thread_communication",
        passed=has_ipc,
        expected="Message queue, FIFO, pipe, or mailbox for inter-thread data",
        actual="IPC mechanism found" if has_ipc else "no IPC — likely using shared globals (race condition risk)",
        check_type="constraint",
    ))

    # Check 3: Sensor thread has higher priority than output thread.
    # K_THREAD_DEFINE(name, stack_size, entry, p1, p2, p3, prio, options, delay)
    # prio is the 7th argument (index 6); may be a numeric literal or #define symbol.
    raw_prios = re.findall(
        r'K_THREAD_DEFINE\s*\([^,]+,[^,]+,[^,]+,[^,]+,[^,]+,[^,]+,\s*(-?\w+)',
        stripped,
        re.DOTALL,
    )
    priorities = [_resolve_int(p, defines) for p in raw_prios]
    priorities = [p for p in priorities if p is not None]
    has_priority_diff = len(set(priorities)) >= 2 if len(priorities) >= 2 else False
    details.append(CheckDetail(
        check_name="priority_differentiation",
        passed=has_priority_diff,
        expected="Sensor and output threads have different priorities",
        actual=f"priorities: {priorities}" if priorities else f"could not extract priorities (raw tokens: {raw_prios})",
        check_type="constraint",
    ))

    # Check 4: Periodic sensor read (100ms interval).
    # Accept literal K_MSEC(100) or a named constant that resolves to 100.
    has_100ms_literal = bool(re.search(r'K_MSEC\s*\(\s*100\s*\)', stripped))
    # Match K_MSEC(<SYMBOL>) where SYMBOL resolves to 100
    symbol_match = re.search(r'K_MSEC\s*\(\s*([A-Z_][A-Z0-9_]*)\s*\)', stripped)
    has_100ms_define = (
        symbol_match is not None
        and _resolve_int(symbol_match.group(1), defines) == 100
    )
    has_periodic = has_100ms_literal or has_100ms_define
    details.append(CheckDetail(
        check_name="periodic_sensor_read",
        passed=has_periodic,
        expected="100ms periodic sensor read interval",
        actual="100ms period found" if has_periodic else "no 100ms period detected",
        check_type="constraint",
    ))

    # Check 5: Moving average with circular buffer (modulo index)
    has_circular = bool(re.search(r'%\s*(?:10|WINDOW|SIZE|NUM_SAMPLES|FILTER_LEN)', stripped)) or \
                   bool(re.search(r'idx\s*=\s*\(\s*idx\s*\+\s*1\s*\)\s*%', stripped)) or \
                   bool(re.search(r'index\s*=\s*\(\s*index\s*\+\s*1\s*\)\s*%', stripped))
    details.append(CheckDetail(
        check_name="circular_buffer_filter",
        passed=has_circular,
        expected="Moving average uses modulo index (circular buffer)",
        actual="circular buffer pattern found" if has_circular else "no circular buffer — may recompute from scratch",
        check_type="constraint",
    ))

    # Check 6: UART output at 1-second interval (not 100ms).
    # Accept K_SECONDS(1), K_MSEC(1000), or a named constant resolving to 1000.
    has_1s_literal = bool(re.search(r'K_SECONDS\s*\(\s*1\s*\)', stripped)) or \
                     bool(re.search(r'K_MSEC\s*\(\s*1000\s*\)', stripped))
    output_symbol_match = re.search(
        r'K_(?:MSEC|SECONDS)\s*\(\s*([A-Z_][A-Z0-9_]*)\s*\)', stripped
    )
    has_1s_define = (
        output_symbol_match is not None
        and _resolve_int(output_symbol_match.group(1), defines) in (1, 1000)
    )
    has_uart_period = has_1s_literal or has_1s_define
    details.append(CheckDetail(
        check_name="uart_output_1s_interval",
        passed=has_uart_period,
        expected="UART output every 1 second (not coupled to 100ms sensor rate)",
        actual="1s interval found" if has_uart_period else "no 1s interval — output may block sensor",
        check_type="constraint",
    ))

    # Check 7: No blocking UART in sensor thread.
    # The sensor function should NOT contain uart_poll_out or printk.
    sensor_funcs = re.findall(r'void\s+(\w*sensor\w*)\s*\(', stripped, re.IGNORECASE)
    uart_in_sensor = False
    for func_name in sensor_funcs:
        body = extract_function_body(stripped, func_name)
        if body and ("uart_poll_out" in body or "printk" in body):
            uart_in_sensor = True
    details.append(CheckDetail(
        check_name="no_blocking_io_in_sensor",
        passed=not uart_in_sensor,
        expected="No UART/printk calls in sensor thread (decoupled architecture)",
        actual="clean" if not uart_in_sensor else "UART output in sensor thread — violates decoupling",
        check_type="constraint",
    ))

    # Check 8: Cross-platform contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
