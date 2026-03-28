"""Shared utilities for EmbedEval check modules.

Provides context-aware code analysis, forbidden API detection,
and numeric extraction for static and behavioral checks.
"""

import re


def strip_comments(code: str) -> str:
    """Remove C-style block and line comments from code."""
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//.*", "", code)
    return code


def extract_function_body(code: str, func_name: str) -> str | None:
    """Extract the body of a named function (brace-matched).

    Returns the content between { and matching }, or None if not found.
    """
    pattern = re.compile(
        rf"(?:static\s+)?(?:inline\s+)?\w[\w\s\*]*\b{re.escape(func_name)}"
        rf"\s*\([^)]*\)\s*\{{",
        re.DOTALL,
    )
    match = pattern.search(code)
    if not match:
        return None

    start = match.end()
    depth = 1
    for i in range(start, len(code)):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
        if depth == 0:
            return code[start:i]
    return None


def find_isr_bodies(code: str) -> list[str]:
    """Extract all ISR/interrupt handler function bodies."""
    isr_patterns = [
        r"void\s+\w*(?:isr|irq|interrupt|handler)\w*\s*\(",
        r"ISR_DIRECT_DECLARE\s*\(\s*\w+\s*\)",
    ]
    bodies: list[str] = []
    for pat in isr_patterns:
        for match in re.finditer(pat, code, re.IGNORECASE):
            # Find the opening brace after this match
            rest = code[match.start() :]
            brace = rest.find("{")
            if brace == -1:
                continue
            start = match.start() + brace + 1
            depth = 1
            for i in range(start, len(code)):
                if code[i] == "{":
                    depth += 1
                elif code[i] == "}":
                    depth -= 1
                if depth == 0:
                    bodies.append(code[start:i])
                    break
    return bodies


# --- Forbidden API lists ---

ISR_FORBIDDEN = [
    "k_malloc",
    "k_free",
    "k_calloc",
    "printk",
    "printf",
    "k_sleep",
    "k_msleep",
    "k_mutex_lock",
    "k_sem_take",  # with K_FOREVER is forbidden, K_NO_WAIT is OK
    "k_msgq_get",  # blocking get forbidden in ISR
    "LOG_ERR",
    "LOG_WRN",
    "LOG_INF",
    "LOG_DBG",
]

ZEPHYR_DEPRECATED = [
    "device_get_binding",
    "device_pm_control",
    "gpio_pin_configure(",  # without _dt suffix
]

CROSS_PLATFORM_FORBIDDEN = {
    "FreeRTOS": [
        "xTaskCreate",
        "vTaskDelay",
        "xQueueSend",
        "xQueueReceive",
        "xSemaphoreTake",
        "xSemaphoreGive",
        "xTimerCreate",
        "vTaskDelete",
        "portYIELD",
    ],
    "Arduino": [
        "analogRead",
        "analogWrite",
        "digitalRead",
        "digitalWrite",
        "Serial.print",
        "Serial.begin",
        "delay(",
        "millis(",
        "pinMode(",
    ],
    "STM32_HAL": [
        "HAL_GPIO_WritePin",
        "HAL_GPIO_ReadPin",
        "HAL_UART_Transmit",
        "HAL_SPI_Transmit",
        "HAL_I2C_Master_Transmit",
        "HAL_ADC_Start",
        "HAL_TIM_Base_Start",
    ],
    "POSIX": [
        "pthread_create",
        "pthread_mutex_lock",
        "pthread_mutex_unlock",
        "sem_wait",
        "sem_post",
    ],
    "Linux_Userspace": [
        "open(",
        "close(",
        "ioctl(",
        "mmap(",
    ],
}


def check_no_cross_platform_apis(
    code: str,
    skip_platforms: list[str] | None = None,
) -> list[tuple[str, str]]:
    """Check for cross-platform API contamination.

    Returns list of (api_name, platform) tuples found in code.
    """
    stripped = strip_comments(code)
    found: list[tuple[str, str]] = []
    skip = set(skip_platforms or [])
    for platform, apis in CROSS_PLATFORM_FORBIDDEN.items():
        if platform in skip:
            continue
        for api in apis:
            if api.endswith("("):
                # Deliberate substring pattern (e.g., "delay(", "open(")
                if api in stripped:
                    found.append((api, platform))
            else:
                # Word-boundary safe API names (e.g., "xTaskCreate")
                if has_api_call(stripped, api):
                    found.append((api, platform))
    return found


def check_no_isr_forbidden(code: str) -> list[str]:
    """Check ISR bodies for forbidden API calls.

    Returns list of forbidden APIs found inside ISR bodies.
    """
    stripped = strip_comments(code)
    isr_bodies = find_isr_bodies(stripped)
    violations: list[str] = []
    for body in isr_bodies:
        for api in ISR_FORBIDDEN:
            if api == "k_sem_take":
                # k_sem_take with K_FOREVER is forbidden, K_NO_WAIT is OK
                if "k_sem_take" in body and "K_FOREVER" in body:
                    violations.append("k_sem_take(K_FOREVER)")
            elif api in body:
                violations.append(api)
    return list(set(violations))


def extract_error_blocks(code: str) -> list[str]:
    """Extract code blocks inside error-handling if statements.

    Matches patterns like: if (ret < 0) { ... }
    """
    blocks: list[str] = []
    for match in re.finditer(
        r"if\s*\(\s*\w+\s*[<!=]+\s*0\s*\)\s*\{", code
    ):
        start = match.end()
        depth = 1
        for i in range(start, len(code)):
            if code[i] == "{":
                depth += 1
            elif code[i] == "}":
                depth -= 1
            if depth == 0:
                blocks.append(code[start:i])
                break
    return blocks


def has_word(code: str, word: str) -> bool:
    """Check for a word with word-boundary matching.

    Prevents substring aliasing (e.g., __copy_to_user matching copy_to_user).
    """
    return bool(re.search(rf'\b{re.escape(word)}\b', code))


def has_api_call(code: str, api: str) -> bool:
    """Check for an API call with word-boundary matching.

    Handles both function-like APIs (e.g., 'copy_to_user') and
    APIs with parens (e.g., 'delay(') by using word boundary on the base name.
    """
    base = api.rstrip("(")
    return bool(re.search(rf'\b{re.escape(base)}\s*\(', code))


def check_qualifier_on_variable(
    code: str,
    qualifier: str,
    var_pattern: str,
) -> bool:
    """Check if a qualifier (e.g., volatile, const) is on a variable matching pattern.

    Args:
        code: Source code to check.
        qualifier: C qualifier to look for (e.g., 'volatile', 'const').
        var_pattern: Regex pattern for the variable name (e.g., r'flag|shared_data').

    Returns True if the qualifier appears on a declaration line with the variable.
    """
    stripped = strip_comments(code)
    return bool(re.search(
        rf'\b{re.escape(qualifier)}\b[^;]*\b({var_pattern})\b\s*[;=\[]',
        stripped,
    ))


def check_return_after_error(code: str, api_call: str | None = None) -> bool:
    """Verify that error-handling blocks contain return/goto (not just detection).

    If api_call is provided, only checks error blocks for that specific API.
    Returns True if ALL error blocks contain return or goto.
    Returns True if no error blocks found (nothing to check).
    """
    stripped = strip_comments(code)
    blocks = extract_error_blocks(stripped)
    if not blocks:
        return True

    for block in blocks:
        if api_call and api_call not in block:
            # Not related to the specified API — check if the error check
            # is immediately after the API call (within a few lines)
            continue
        if "return" not in block and "goto" not in block:
            return False
    return True


def check_api_in_function(
    code: str,
    api_name: str,
    func_name: str,
) -> bool:
    """Check if api_name appears inside func_name's body.

    Uses extract_function_body for scope-aware checking.
    """
    stripped = strip_comments(code)
    body = extract_function_body(stripped, func_name)
    if body is None:
        return False
    return has_word(body, api_name)


def check_cleanup_reverse_order(
    code: str,
    init_calls: list[str],
    func_name: str | None = None,
) -> bool:
    """Verify cleanup calls appear in reverse order of init calls.

    Checks error-handling paths for proper reverse-order cleanup.
    If func_name is provided, only checks within that function.
    """
    target = code
    if func_name:
        stripped = strip_comments(code)
        body = extract_function_body(stripped, func_name)
        if body is None:
            return False
        target = body

    blocks = extract_error_blocks(target)
    if not blocks:
        return True

    for block in blocks:
        # Find cleanup calls in the ORDER they appear in the block
        positions = []
        for call in init_calls:
            pos = block.find(call)
            if pos != -1:
                positions.append((pos, call))
        positions.sort()
        found_order = [call for _, call in positions]

        if len(found_order) >= 2:
            expected = [c for c in reversed(init_calls) if c in found_order]
            if found_order != expected:
                return False
    return True


def has_error_check(code: str) -> bool:
    """Check if code has return-value error handling.

    Accepts: < 0, != 0, if(ret..), if(err..), if(rc..), if(status..).
    Note: does NOT verify an error branch is taken — use
    check_return_after_error() for flow verification.
    """
    stripped = strip_comments(code)
    patterns = [
        r"<\s*0",
        r"!=\s*0",
        r"if\s*\(\s*ret\b",
        r"if\s*\(\s*err\b",
        r"if\s*\(\s*rc\b",
        r"if\s*\(\s*status\b",
    ]
    return any(re.search(p, stripped) for p in patterns)


def has_sleep_call(code: str) -> bool:
    """Check for any Zephyr sleep variant."""
    stripped = strip_comments(code)
    return bool(re.search(
        r'\b(?:k_sleep|k_msleep|k_usleep)\s*\(', stripped
    ))


def has_output_call(code: str) -> bool:
    """Check for any output/logging function."""
    stripped = strip_comments(code)
    return bool(re.search(
        r'\b(?:printk|printf|LOG_INF|LOG_ERR|LOG_WRN|LOG_DBG'
        r'|pr_info|pr_err|pr_warn|pr_debug)\s*\(',
        stripped,
    ))


def resolve_define(code: str, name: str) -> int | None:
    """Resolve a #define macro to its integer value."""
    match = re.search(
        rf"#define\s+{re.escape(name)}\s+(\d+)", code
    )
    if match:
        return int(match.group(1))
    return None


def extract_numeric(code: str, pattern: str) -> int | None:
    """Extract a numeric value matching a regex pattern with group(1)."""
    match = re.search(pattern, code)
    if match:
        val = match.group(1)
        if val.startswith("0x") or val.startswith("0X"):
            return int(val, 16)
        if val.isdigit():
            return int(val)
        # Try resolving as macro
        return resolve_define(code, val)
    return None
