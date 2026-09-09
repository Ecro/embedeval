"""Shared utilities for EmbedEval check modules.

Provides context-aware code analysis, forbidden API detection,
and numeric extraction for static and behavioral checks.
"""

import re
from functools import lru_cache
from importlib.resources import files
from typing import cast

import yaml


def strip_comments(code: str) -> str:
    """Remove C-style block and line comments from code."""
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//.*", "", code)
    return code


def blank_comments(code: str) -> str:
    """Blank out C comment bodies with spaces, preserving every offset.

    Unlike :func:`strip_comments`, the result has the same length as the input,
    so an index found in it is still valid in the original code — checks that
    slice a window around a match (``code[pos : pos + 300]``) keep working.
    Newlines survive, so line numbers are preserved too.
    """

    def _blank(match: "re.Match[str]") -> str:
        return re.sub(r"\S", " ", match.group(0))

    code = re.sub(r"/\*.*?\*/", _blank, code, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", _blank, code)


def find_in_code(code: str, needle: str) -> int:
    """Index of ``needle`` in ``code``, ignoring matches inside C comments.

    Drop-in replacement for ``code.find(needle)`` in ordering checks. A model
    that documents an API in a header comment ("Unless the firmware calls
    boot_write_img_confirmed(), ...") must not be judged as *calling* it there:
    on raw text that comment lands before the real call and inverts every
    position comparison. The 2026-09-08 opus5 run lost 8 cases to exactly this
    (ota-001/004/006/008, power-mgmt-004, security-005, networking-005,
    ota-005) while a model that wrote the same code with fewer comments passed.

    Offsets stay valid in ``code`` itself (see :func:`blank_comments`), so
    existing call sites that slice a window from the returned index are safe.

    BitBake recipes use ``#`` comments and embed ``file://`` URIs that C
    comment handling would mangle; use :func:`find_in_yocto` there.
    """
    return blank_comments(code).find(needle)


def expand_string_defines(code: str) -> str:
    """Inline ``#define NAME "value"`` macros at their use sites.

    Checks that demand a literal string argument (``open("/dev/spidev0.0"``,
    ``sd_bus_request_name(bus, "com.embedeval.Example"``) otherwise reject the
    equivalent — and more maintainable — macro form that names the constant
    once. Run this before matching such a literal.

    Only object-like macros whose body is a single string literal are
    substituted; function-like macros and numeric ones are left alone
    (:func:`resolve_define` covers the numeric case).
    """
    defines = dict(re.findall(r'#define\s+(\w+)\s+("(?:[^"\\]|\\.)*")', code))
    if not defines:
        return code
    # Longest names first so a macro that prefixes another isn't clobbered.
    pattern = re.compile(
        r"\b("
        + "|".join(sorted(map(re.escape, defines), key=len, reverse=True))
        + r")\b"
    )
    return pattern.sub(lambda m: defines[m.group(1)], code)


def find_in_yocto(text: str, needle: str) -> int:
    """Index of ``needle`` in recipe ``text``, ignoring ``#`` comments.

    Yocto counterpart of :func:`find_in_code` — keeps ``file://`` style URIs
    intact (see :func:`strip_yocto_comments`). Comment removal shifts offsets,
    so use the result for presence and ordering only, not for slicing ``text``.
    """
    return strip_yocto_comments(text).find(needle)


def strip_string_literals(code: str) -> str:
    """Remove C string and char literal contents, keeping quotes as sentinels.

    Prevents substring checks from matching identifiers that only appear
    inside log messages or format strings (e.g. printk("use k_malloc"))
    from tripping a "no k_malloc" check.

    Escape sequences are handled; the quotes themselves remain to preserve
    offset structure.
    """
    # Double-quoted string literals (with escape handling)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code, flags=re.DOTALL)
    # Single-quoted char literals
    code = re.sub(r"'(?:[^'\\]|\\.)*'", "''", code, flags=re.DOTALL)
    return code


def scoped_contains(
    code: str,
    needle: str,
    *,
    scope: str = "stripped",
) -> bool:
    """Substring check with explicit scope discipline.

    scope='stripped'  : strip comments AND string literals (default, safest).
                        Matches identifier-level substrings only.
    scope='code_only' : strip comments but keep string literals intact.
                        Use when matching quoted content deliberately.
    scope='raw'       : match anywhere — rare; inline comment must justify.

    Use this helper in static.py / behavior.py instead of `needle in code`
    to avoid matching inside comments or log-message string literals.
    """
    if scope == "stripped":
        return needle in strip_string_literals(strip_comments(code))
    if scope == "code_only":
        return needle in strip_comments(code)
    if scope == "raw":
        return needle in code
    raise ValueError(f"unknown scope {scope!r}; use 'stripped' | 'code_only' | 'raw'")


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


def function_bodies(code: str) -> list[tuple[str, str]]:
    """Return ``(name, body)`` for every brace-matched function definition.

    Comments are blanked first so a commented-out signature never opens a
    phantom body. Bodies exclude the outer braces.
    """
    blanked = blank_comments(code)
    signature = re.compile(
        r"^[A-Za-z_][\w \t\*]*?\b(\w+)\s*\([^;{]*?\)\s*\{",
        re.MULTILINE | re.DOTALL,
    )
    bodies: list[tuple[str, str]] = []
    for match in signature.finditer(blanked):
        start = match.end()
        depth = 1
        for i in range(start, len(blanked)):
            if blanked[i] == "{":
                depth += 1
            elif blanked[i] == "}":
                depth -= 1
                if depth == 0:
                    bodies.append((match.group(1), blanked[start:i]))
                    break
    return bodies


def ordered_in_same_function(code: str, first: str, second: str) -> bool:
    """True when some function calls ``first`` and then ``second`` after it.

    Ordering checks that compare whole-file offsets break the moment a model
    factors code into helpers: a re-arm helper defined above ``main`` puts
    ``uart_rx_enable`` before the ``uart_callback_set`` that main runs first,
    and a helper that appends CoAP options sits above the ``coap_packet_init``
    call site. What the constraint actually means is "inside the setup path,
    first comes before second", which is a per-function question.

    Callers that must also accept the fully factored shape (``first`` and
    ``second`` in *different* functions, where text says nothing about order)
    should OR this with their own presence check.
    """
    return any(
        first in body and second in body and body.find(first) < body.find(second)
        for _name, body in function_bodies(code)
    )


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


@lru_cache(maxsize=1)
def _load_forbidden_apis() -> dict[str, list[str]]:
    """Load cross-platform forbidden API blacklist from packaged YAML.

    Single source of truth — downstream tools (e.g. Hiloop rule pack)
    should consume the same YAML, not re-hardcode the list.
    """
    text = files("embedeval.data").joinpath("forbidden_apis.yaml").read_text()
    data = yaml.safe_load(text)
    platforms = data.get("platforms", {})
    if not isinstance(platforms, dict):
        raise ValueError("forbidden_apis.yaml: 'platforms' must be a mapping")
    return cast(dict[str, list[str]], platforms)


def get_cross_platform_forbidden() -> dict[str, list[str]]:
    """Return the cross-platform forbidden API mapping.

    Kept as a function (not module-level constant) so tests can clear
    the lru_cache if they swap the data file.
    """
    return _load_forbidden_apis()


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
    for platform, apis in get_cross_platform_forbidden().items():
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
    for match in re.finditer(r"if\s*\(\s*\w+\s*[<!=]+\s*0\s*\)\s*\{", code):
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
    return bool(re.search(rf"\b{re.escape(word)}\b", code))


def has_api_call(code: str, api: str) -> bool:
    """Check for an API call with word-boundary matching.

    Handles both function-like APIs (e.g., 'copy_to_user') and
    APIs with parens (e.g., 'delay(') by using word boundary on the base name.
    """
    base = api.rstrip("(")
    return bool(re.search(rf"\b{re.escape(base)}\s*\(", code))


def has_any_api_call(code: str, apis: list[str]) -> bool:
    """Check for any of several equivalent API spellings.

    Many SDKs offer aliases or version-renamed APIs that are functionally
    equivalent (e.g. Zephyr's `dma_config()` vs `dma_configure()`).
    Checks that demand exactly one spelling produce false negatives when
    the LLM picks the other valid form — surfaced empirically by Context
    Quality Mode trade-off analysis (2026-04-18). Use this helper for any
    check where multiple SDK spellings are correct.
    """
    return any(has_api_call(code, a) for a in apis)


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
    return bool(
        re.search(
            rf"\b{re.escape(qualifier)}\b[^;]*\b({var_pattern})\b\s*[;=\[]",
            stripped,
        )
    )


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
    return bool(re.search(r"\b(?:k_sleep|k_msleep|k_usleep)\s*\(", stripped))


def has_output_call(code: str) -> bool:
    """Check for any output/logging function."""
    stripped = strip_comments(code)
    return bool(
        re.search(
            r"\b(?:printk|printf|LOG_INF|LOG_ERR|LOG_WRN|LOG_DBG"
            r"|pr_info|pr_err|pr_warn|pr_debug)\s*\(",
            stripped,
        )
    )


def resolve_define(code: str, name: str) -> int | None:
    """Resolve a #define macro to its integer value."""
    match = re.search(rf"#define\s+{re.escape(name)}\s+(\d+)", code)
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


# ---------------------------------------------------------------------------
# Linux kernel 5.15+ helpers.
#
# Used by cases/embedded-linux/linux-driver-* checks. Kept here (not in a
# per-TC module) so every linux-driver TC uses the same regex discipline and
# known false-positive traps are fixed in one place.
# ---------------------------------------------------------------------------

_LINUX_INIT_PATTERNS = (
    # static int probe(struct platform_device *pdev)
    r"static\s+(?:int\s+(?:__init\s+)?|__init\s+int\s+)"
    r"(?P<name>\w+)\s*\(\s*struct\s+platform_device\s*\*\s*\w+\s*\)\s*\{",
    # static int __init module_init_fn(void)
    r"static\s+int\s+__init\s+(?P<name2>\w+)\s*\([^)]*\)\s*\{",
    # int __init name(void)   (no static)
    r"\bint\s+__init\s+(?P<name3>\w+)\s*\([^)]*\)\s*\{",
)

_LINUX_EXIT_PATTERNS = (
    # static int remove(struct platform_device *pdev)
    r"static\s+(?:int|void)\s+(?:__exit\s+)?"
    r"(?P<name>\w*(?:remove|cleanup|exit)\w*)\s*"
    r"\(\s*struct\s+platform_device\s*\*\s*\w+\s*\)\s*\{",
    # static void __exit module_exit_fn(void)
    r"static\s+void\s+__exit\s+(?P<name2>\w+)\s*\([^)]*\)\s*\{",
    # void __exit name(void)
    r"\bvoid\s+__exit\s+(?P<name3>\w+)\s*\([^)]*\)\s*\{",
)


def _extract_body_from_brace(code: str, start_after_brace: int) -> str | None:
    depth = 1
    for i in range(start_after_brace, len(code)):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                return code[start_after_brace:i]
    return None


def extract_module_init_body(code: str) -> str | None:
    """Extract the body of a Linux driver's probe/init function.

    Recognizes ``static int probe(struct platform_device *)``,
    ``static int __init name(void)``, and ``int __init name(void)``.

    Returns the brace body or None if nothing matches. Only the first
    match is returned — drivers with multiple probes should use
    ``extract_function_body`` directly.
    """
    stripped = strip_comments(code)
    for pat in _LINUX_INIT_PATTERNS:
        match = re.search(pat, stripped)
        if match:
            body = _extract_body_from_brace(stripped, match.end())
            if body is not None:
                return body
    return None


def extract_module_exit_body(code: str) -> str | None:
    """Extract the body of a Linux driver's remove/exit function.

    Recognizes ``static int remove(struct platform_device *)``,
    ``static void __exit name(void)``, and ``void __exit name(void)``.

    Kept separate from ``extract_module_init_body`` because the
    ``init_error_path_cleanup`` blind-spot documented in
    PLAN-remaining-blindspots relies on scoping cleanup checks strictly
    to the init body — an identical call in the exit body must not
    satisfy an init-path check.
    """
    stripped = strip_comments(code)
    for pat in _LINUX_EXIT_PATTERNS:
        match = re.search(pat, stripped)
        if match:
            body = _extract_body_from_brace(stripped, match.end())
            if body is not None:
                return body
    return None


# devm_* allocators and managed-resource getters that automatically release
# on device detach. Manually pairing a matching kfree/put/free call is a
# double-free bug (see CVE-2026-23068 spi-sprd-adi).
_DEVM_TO_MANUAL_FREE: dict[str, tuple[str, ...]] = {
    "devm_kmalloc": ("kfree",),
    "devm_kzalloc": ("kfree",),
    "devm_kcalloc": ("kfree",),
    "devm_kstrdup": ("kfree",),
    "devm_clk_get": ("clk_put",),
    "devm_clk_get_optional": ("clk_put",),
    "devm_gpiod_get": ("gpiod_put",),
    "devm_gpiod_get_optional": ("gpiod_put",),
    "devm_regulator_get": ("regulator_put",),
    "devm_request_irq": ("free_irq",),
    "devm_request_threaded_irq": ("free_irq",),
    "devm_ioremap": ("iounmap",),
    "devm_ioremap_resource": ("iounmap",),
    "devm_platform_ioremap_resource": ("iounmap",),
}


def has_manual_free_paired_with_devm(code: str) -> list[tuple[str, str]]:
    """Find devm_* calls whose matching manual free is also present.

    Returns a list of ``(devm_call, manual_free_call)`` pairs. Empty list
    means no double-free bug pattern detected. Intended for the
    ``no_manual_free_for_devm_resource`` negative check that mirrors
    CVE-2026-23068: devm automatic release + manual free on the same
    resource produces a double free.

    Caveat from CLAUDE.md 2026-03-29: uses ``has_api_call`` (word-boundary
    + open paren) so ``__devm_kfree`` does not match ``devm_kmalloc`` and
    ``kfree_rcu`` does not match ``kfree``.
    """
    stripped = strip_comments(code)
    found: list[tuple[str, str]] = []
    for devm, manuals in _DEVM_TO_MANUAL_FREE.items():
        if not has_api_call(stripped, devm):
            continue
        for manual in manuals:
            if has_api_call(stripped, manual):
                found.append((devm, manual))
    return found


# APIs that return ERR_PTR on failure. Callers must guard with IS_ERR;
# a plain ``if (!ret)`` check is a bug because ERR_PTR values are
# non-NULL pointers in the kernel's error-coded pointer range.
_ERR_PTR_RETURNING_APIS = (
    "clk_get",
    "clk_get_optional",
    "devm_clk_get",
    "devm_clk_get_optional",
    "devm_gpiod_get",
    "devm_gpiod_get_optional",
    "devm_regulator_get",
    "devm_platform_ioremap_resource",
    "devm_ioremap_resource",
    "platform_get_resource",
    "of_find_node_by_name",
    "regmap_init_i2c",
    "devm_regmap_init_i2c",
)


def returns_err_ptr(api_name: str) -> bool:
    """Whether an API returns ERR_PTR on failure (requires IS_ERR guard)."""
    return api_name in _ERR_PTR_RETURNING_APIS


def has_is_err_guard(code: str, api_name: str) -> bool:
    """Check that an ERR_PTR-returning API is guarded by IS_ERR.

    Matches patterns like:
        x = api_name(...);
        if (IS_ERR(x))

    Supports struct-member LHS (``priv->regs``, ``dev->clk``,
    ``state.handle``) as well as plain identifiers.

    False-positive trap: plain ``if (!x)`` is NOT an IS_ERR guard —
    ERR_PTR values are non-NULL kernel pointers. See kernel.org
    err.h semantics.

    Known limitation: the ``[^;]*`` argument-list matcher stops at the
    first semicolon; a macro expansion containing ``;`` inside a devm_*
    argument list would truncate early. No current kernel idiom hits
    this; revisit if a concrete false negative surfaces.
    """
    stripped = strip_comments(code)
    if not has_api_call(stripped, api_name):
        return False
    # LHS can be: ident  |  ident->field->field  |  ident.field.field
    # (no whitespace inside the chain, which is standard C formatting).
    # DOTALL is intentionally NOT set: ``[^;]*`` already matches newlines
    # by character-class semantics, and the leading ``{lhs}`` contains no
    # ``.`` wildcards — adding DOTALL was dead-weight in earlier revisions.
    lhs = r"[A-Za-z_]\w*(?:(?:\s*->\s*|\s*\.\s*)\w+)*"
    call_pat = re.compile(
        rf"({lhs})\s*=\s*{re.escape(api_name)}\s*\([^;]*\)\s*;",
    )
    for m in call_pat.finditer(stripped):
        var = re.sub(r"\s+", "", m.group(1))
        tail = stripped[m.end() : m.end() + 400]
        # Normalize whitespace in tail so a loose ``IS_ERR( priv -> regs )``
        # still matches a normalized LHS token.
        tail_norm = re.sub(r"\s+", "", tail)
        if re.search(rf"IS_ERR(?:_OR_NULL)?\({re.escape(var)}\)", tail_norm):
            return True
    return False


# Sleepable kernel APIs forbidden inside atomic contexts (spin_lock /
# irq handler / RCU read side). Not exhaustive — covers the classes
# LLMs most often mis-place.
_ATOMIC_CTX_FORBIDDEN = (
    "msleep",
    "usleep_range",
    "schedule",
    "schedule_timeout",
    "wait_for_completion",  # without _timeout variants below
    "mutex_lock",
    "down",
    "down_interruptible",
    "kmalloc",  # with GFP_KERNEL — checked separately
    "copy_to_user",
    "copy_from_user",
    "vmalloc",
)


def sleepable_calls_in_atomic_ctx(body: str) -> list[str]:
    """Return sleepable kernel API calls found in an atomic-ctx body.

    Pass the body of a spin-locked region, IRQ handler, or RCU read-side
    critical section. Returns a list of forbidden API names found.

    False-positive trap: ``mutex_lock`` inside an RCU read-side section
    is forbidden; ``mutex_lock`` in a plain threaded handler is fine.
    Callers must decide which set to consult based on context type.
    """
    stripped = strip_comments(body)
    found: list[str] = []
    for api in _ATOMIC_CTX_FORBIDDEN:
        if has_api_call(stripped, api):
            found.append(api)
    return found


# ---------------------------------------------------------------------------
# Yocto/BitBake recipe helpers.
#
# Yocto recipe files (.bb/.bbappend/.bbclass/.inc) use ``#`` line comments
# and embed URIs like ``file://``, ``git://``, ``http://`` that must not be
# clobbered by C-style comment stripping. CLAUDE.md 2026-04-19 corrections
# apply: use scope='raw' from scoped_contains for .bb checks, OR use the
# yocto-aware helpers below.
# ---------------------------------------------------------------------------


def strip_yocto_comments(text: str) -> str:
    """Strip shell-style ``#`` line comments from BitBake recipe text.

    Preserves ``file://``/``git://``/``http://`` URIs by only stripping
    ``#`` when it is the first non-whitespace character on a line, or is
    preceded by whitespace and NOT by a colon (which would mean we're
    inside a URI scheme).
    """
    out: list[str] = []
    for line in text.splitlines():
        # Drop full-line comment or leading-whitespace comment
        if re.match(r"\s*#", line):
            continue
        # Drop trailing "  # comment" but keep URIs intact. The single
        # ``(?<!:)`` lookbehind suffices — it rejects any whitespace-#
        # whose preceding char is a colon (e.g., end of ``file:`` just
        # before a space). A prior revision had a second, redundant
        # ``(?<!:\/)`` lookbehind; removed as dead code.
        stripped = re.sub(r"(?<!:)\s+#.*$", "", line)
        out.append(stripped)
    return "\n".join(out)


def yocto_contains(text: str, needle: str) -> bool:
    """Yocto-aware substring check: strips #-comments, keeps URIs.

    Use instead of ``scoped_contains(..., scope='raw')`` when the check
    needs to ignore commented-out recipe lines but must still match
    tokens that could accidentally live next to URI schemes.
    """
    return needle in strip_yocto_comments(text)


def yocto_has_override(text: str, var: str, override: str) -> bool:
    """Detect a BitBake variable override in the modern colon form.

    Kirkstone (Yocto 4.0) supports both ``VAR_append`` (legacy underscore)
    and ``VAR:append`` (modern colon) forms. This helper matches the colon
    form only — the preferred kirkstone canonical syntax.

    Example: ``yocto_has_override(text, 'FILESEXTRAPATHS', 'prepend')``
    matches ``FILESEXTRAPATHS:prepend := "..."``.
    """
    body = strip_yocto_comments(text)
    return bool(
        re.search(
            rf"\b{re.escape(var)}:{re.escape(override)}\b\s*[:+?]?=",
            body,
        )
    )


def yocto_has_legacy_override(text: str, var: str, override: str) -> bool:
    """Detect the legacy underscore override form (discouraged on kirkstone+).

    Use as a negative check: a TC that rewards colon form should also
    penalize the underscore form.
    """
    body = strip_yocto_comments(text)
    return bool(
        re.search(
            rf"\b{re.escape(var)}_{re.escape(override)}\b\s*[:+?]?=",
            body,
        )
    )


# ---------------------------------------------------------------------------
# Linux userspace helpers (Phase B).
#
# Shared by cases/embedded-linux/linux-userspace-* TCs. Covers systemd unit
# files, udev rules, libgpiod v1-vs-v2 detection, sd-bus vs libdbus
# detection, and eBPF CO-RE marker detection.
#
# systemd / udev / NetworkManager share ``#`` line-comment semantics with
# Yocto recipes; strip_yocto_comments is reused as the canonical stripper.
# ---------------------------------------------------------------------------

# Alias — keeps user-facing API readable ("I'm stripping a systemd unit,
# not a Yocto recipe") while sharing implementation.
strip_systemd_comments = strip_yocto_comments


def systemd_unit_section_has(
    text: str,
    section: str,
    directive: str,
) -> str | None:
    """Return the RHS value of ``<directive>=<value>`` inside ``[section]``.

    Args:
        text: unit file contents.
        section: section name without brackets (e.g. ``Service``, ``Unit``,
            ``Install``, ``Timer``).
        directive: directive key (e.g. ``Type``, ``WatchdogSec``, ``Restart``).

    Returns:
        The RHS string (trimmed) if the directive appears inside the named
        section, None otherwise. If the same directive appears multiple times
        in the section, returns the last occurrence (systemd's own precedence).
    """
    body = strip_systemd_comments(text)
    # Fold systemd-style line continuations ``\<newline>`` into a single
    # space so that multi-line directive values (e.g. ``ExecStart=foo \``
    # continued on the next line with ``--arg1 --arg2``) are visible as
    # one logical RHS to the directive regex.
    body = re.sub(r"\\\n\s*", " ", body)

    # Locate section boundary: from ``[section]`` line to the next ``[...]``
    # header or end of file.
    sec_pat = re.compile(rf"^\[{re.escape(section)}\]\s*$", re.MULTILINE)
    m = sec_pat.search(body)
    if not m:
        return None
    start = m.end()
    next_hdr = re.search(r"^\[[^\]]+\]\s*$", body[start:], re.MULTILINE)
    end = start + next_hdr.start() if next_hdr else len(body)
    section_body = body[start:end]

    # Match ``Directive=value`` with optional whitespace around ``=``.
    directive_pat = re.compile(
        rf"^\s*{re.escape(directive)}\s*=\s*(.*?)\s*$",
        re.MULTILINE,
    )
    matches = directive_pat.findall(section_body)
    return matches[-1] if matches else None


# udev rule keys that are strictly match-only (must use ``==`` or numeric
# ops). Using plain ``=`` on these is a classic bug — it becomes an
# assignment to a non-assignable key and the rule silently no-ops or
# errors out.
#
# Dual-use keys (match via ``==`` OR assign via ``=`` / ``+=``) are NOT
# in this set:
#   - ``ENV{foo}``   — match device env (``==``) OR assign new env (``=``)
#   - ``ATTR{foo}``  — match child-device sysfs attribute (``==``) OR
#                       WRITE to that attribute (``=``, e.g.
#                       ``ATTR{brightness}="200"`` to set backlight).
# ``ATTRS`` (plural, walks parent chain) stays in the match-only set —
# the kernel has no concept of writing to a parent device attribute.
_UDEV_MATCH_ONLY_KEYS = frozenset(
    {
        "ACTION",
        "SUBSYSTEM",
        "SUBSYSTEMS",
        "DEVPATH",
        "KERNEL",
        "KERNELS",
        "DRIVER",
        "DRIVERS",
        "ATTRS",
        "SYSCTL",
        "TEST",
        "RESULT",
    }
)

# udev rule keys that are assignment-only (``=``, ``+=``, ``:=``, ``-=``).
_UDEV_ASSIGN_ONLY_KEYS = frozenset(
    {
        "NAME",
        "SYMLINK",
        "OWNER",
        "GROUP",
        "MODE",
        "TAG",
        "RUN",
        "LABEL",
        "GOTO",
        "IMPORT",
        "OPTIONS",
    }
)


def udev_rule_matches(text: str, key: str) -> str | None:
    """Return the RHS value of a udev ``key==value`` match.

    Handles ``key{subkey}`` form (e.g. ``ATTRS{idVendor}``). Returns the
    RHS with surrounding quotes stripped, or None if no match present.
    """
    body = strip_systemd_comments(text)
    # Escape the key but allow optional ``{subkey}`` qualifier.
    pat = re.compile(rf'\b{re.escape(key)}(?:\{{[^}}]+\}})?\s*==\s*"([^"]*)"')
    m = pat.search(body)
    return m.group(1) if m else None


def udev_rule_assigns(text: str, key: str) -> tuple[str, str] | None:
    """Return ``(operator, value)`` for a udev ``key <op> value`` assignment.

    Operators: ``=``, ``+=``, ``:=``, ``-=``.
    """
    body = strip_systemd_comments(text)
    pat = re.compile(
        rf'\b{re.escape(key)}(?:\{{[^}}]+\}})?\s*(\+=|:=|-=|=)\s*"([^"]*)"'
    )
    m = pat.search(body)
    return (m.group(1), m.group(2)) if m else None


def udev_match_key_used_as_assign(text: str) -> list[str]:
    """Return the list of match-only keys that the text assigns to via ``=``.

    Classic udev bug: writing ``SUBSYSTEM="usb"`` (assignment) instead of
    ``SUBSYSTEM=="usb"`` (match) — the rule silently fails to filter and
    either matches every device or errors out at rule-load time.
    """
    body = strip_systemd_comments(text)
    offenders: list[str] = []
    for key in _UDEV_MATCH_ONLY_KEYS:
        # Find ``KEY="..."`` (single =, not ==, not +=) on the same line.
        # Dual-use keys (ENV, ATTR) are excluded at the set level, so no
        # per-iteration skip is needed here.
        pat = re.compile(
            rf'\b{re.escape(key)}(?:\{{[^}}]+\}})?\s*(?<![=+:\-])=(?!=)\s*"'
        )
        if pat.search(body):
            offenders.append(key)
    return offenders


# libgpiod v1-exclusive symbols (deprecated in v2). Presence of ANY
# indicates the code targets the 2017-era API rather than the 2023 v2
# character-device rewrite.
_LIBGPIOD_V1_EXCLUSIVE = (
    "gpiod_chip_open_by_name",
    "gpiod_chip_open_by_number",
    "gpiod_chip_open_lookup",
    "gpiod_chip_get_line",
    "gpiod_chip_get_lines",
    "gpiod_chip_get_all_lines",
    "gpiod_line_request_output",
    "gpiod_line_request_input",
    "gpiod_line_request_both_edges_events",
    "gpiod_line_request_rising_edge_events",
    "gpiod_line_request_falling_edge_events",
    "gpiod_line_request_bulk_output",
    "gpiod_line_request_bulk_input",
    "gpiod_line_get_value",
    "gpiod_line_set_value",
    "gpiod_line_event_wait",
    "gpiod_line_event_read",
    "gpiod_line_release",
    "gpiod_line_release_bulk",
    "gpiod_line_name",
)

# libgpiod v2-exclusive symbols. These did not exist before v2.0 (March 2023).
_LIBGPIOD_V2_EXCLUSIVE = (
    "gpiod_line_settings_new",
    "gpiod_line_settings_set_direction",
    "gpiod_line_settings_set_edge_detection",
    "gpiod_line_settings_set_output_value",
    "gpiod_line_settings_set_bias",
    "gpiod_line_settings_free",
    "gpiod_line_config_new",
    "gpiod_line_config_add_line_settings",
    "gpiod_line_config_free",
    "gpiod_request_config_new",
    "gpiod_request_config_set_consumer",
    "gpiod_request_config_free",
    "gpiod_chip_request_lines",
    "gpiod_line_request_get_value",
    "gpiod_line_request_set_value",
    "gpiod_line_request_read_edge_events",
    "gpiod_line_request_wait_edge_events",
    "gpiod_line_request_release",
    "gpiod_edge_event_buffer_new",
    "gpiod_edge_event_buffer_free",
    "gpiod_edge_event_get_line_offset",
    "gpiod_edge_event_get_event_type",
)


def has_libgpiod_v1_api(code: str) -> list[str]:
    """Return list of v1-exclusive libgpiod symbols detected in ``code``.

    Non-empty list means the code uses the deprecated 2017-era API. v2
    symbols are NOT listed here even though both generations coexist in
    libgpiod 2.x source — they're in ``_LIBGPIOD_V2_EXCLUSIVE``.
    """
    stripped = strip_comments(code)
    return [api for api in _LIBGPIOD_V1_EXCLUSIVE if has_api_call(stripped, api)]


def has_libgpiod_v2_api(code: str) -> list[str]:
    """Return list of v2-exclusive libgpiod symbols detected in ``code``."""
    stripped = strip_comments(code)
    return [api for api in _LIBGPIOD_V2_EXCLUSIVE if has_api_call(stripped, api)]


# sd-bus symbols — the modern Linux-only D-Bus client library shipped in
# libsystemd. Official recommendation for systemd-based embedded Linux
# since systemd 221 (2015).
_SD_BUS_API_SYMBOLS = (
    "sd_bus_open_system",
    "sd_bus_open_user",
    "sd_bus_open",
    "sd_bus_default",
    "sd_bus_default_system",
    "sd_bus_default_user",
    "sd_bus_request_name",
    "sd_bus_release_name",
    "sd_bus_add_object_vtable",
    "sd_bus_add_object",
    "sd_bus_process",
    "sd_bus_wait",
    "sd_bus_slot_unref",
    "sd_bus_unref",
    "sd_bus_flush_close_unref",
    "sd_bus_reply_method_return",
    "sd_bus_message_append",
    "sd_bus_message_read",
    "sd_bus_message_new_method_call",
    "sd_bus_error_set",
    "sd_bus_error_set_errno",
    "sd_bus_error_free",
)

# libdbus symbols — the cross-platform, deprecated-for-Linux-only-daemons
# reference D-Bus library. Officially discouraged by freedesktop.org
# ("signing up for some pain"). TCs that require sd-bus must reject these.
_LIBDBUS_API_SYMBOLS = (
    "dbus_bus_get",
    "dbus_bus_request_name",
    "dbus_connection_open",
    "dbus_connection_read_write_dispatch",
    "dbus_connection_read_write",
    "dbus_connection_send",
    "dbus_connection_pop_message",
    "dbus_message_new_method_call",
    "dbus_message_new_method_return",
    "dbus_message_iter_init",
    "dbus_message_iter_append_basic",
    "dbus_message_unref",
    "dbus_error_init",
    "dbus_error_free",
    "dbus_error_is_set",
)


def has_sd_bus_api(code: str) -> list[str]:
    """Return sd-bus symbols detected in ``code``."""
    stripped = strip_comments(code)
    return [api for api in _SD_BUS_API_SYMBOLS if has_api_call(stripped, api)]


def has_libdbus_api(code: str) -> list[str]:
    """Return libdbus symbols detected in ``code``.

    False-positive trap: ``sd_bus_*`` and ``dbus_*`` share the substring
    ``_bus_`` — word-boundary matching (``has_api_call``) handles this.
    """
    stripped = strip_comments(code)
    return [api for api in _LIBDBUS_API_SYMBOLS if has_api_call(stripped, api)]


# BPF SEC() macro flavours. Detecting the presence of SEC macros is the
# cheapest way to confirm a file is a BPF program (vs a userspace loader).
_BPF_SEC_PROGRAM_TYPES = (
    "kprobe",
    "kretprobe",
    "tp",
    "tracepoint",
    "raw_tracepoint",
    "fentry",
    "fexit",
    "xdp",
    "cgroup_skb",
    "cgroup_sock",
    "perf_event",
    "socket",
    "lsm",
    "iter",
)


def has_bpf_sec_macro(code: str) -> list[str]:
    """Return list of BPF SEC program-type attachments detected.

    Recognizes ``SEC("<type>/<attach>")`` forms. Also detects the special
    non-program sections ``.maps`` and ``license`` separately.
    """
    stripped = strip_comments(code)
    found: list[str] = []
    for prog_type in _BPF_SEC_PROGRAM_TYPES:
        if re.search(rf'SEC\(\s*"{re.escape(prog_type)}(?:/[^"]*)?"\s*\)', stripped):
            found.append(prog_type)
    # Special non-program sections.
    if re.search(r'SEC\(\s*"\.maps"\s*\)', stripped):
        found.append(".maps")
    if re.search(r'SEC\(\s*"license"\s*\)', stripped):
        found.append("license")
    return found


def has_bpf_core_read(code: str) -> bool:
    """Whether the code uses any BPF CO-RE read macro variant."""
    stripped = strip_comments(code)
    return any(
        has_api_call(stripped, macro)
        for macro in (
            "BPF_CORE_READ",
            "BPF_CORE_READ_INTO",
            "BPF_CORE_READ_STR_INTO",
            "BPF_CORE_READ_USER",
            "BPF_CORE_READ_USER_INTO",
            "BPF_CORE_READ_USER_STR_INTO",
        )
    )


# ---------------------------------------------------------------------------
# OTA helpers (Phase C-1).
#
# Shared by cases/embedded-linux/ota-swupdate-* and ota-rauc-* TCs.
# SWUpdate uses libconfig (``key = value;`` + ``section = { ... };`` +
# ``list: ( item, item );`` with ``#`` line comments). RAUC uses INI
# (``[section]`` + ``key=value`` with ``#`` line comments and dotted
# section names like ``[image.rootfs.0]``).
#
# Both share ``#`` line-comment semantics with systemd / Yocto, so
# ``strip_systemd_comments`` is reused as the canonical stripper.
# ---------------------------------------------------------------------------


def libconfig_section_body(text: str, section_path: str) -> str | None:
    """Return the brace-body of a libconfig section (possibly nested).

    ``section_path`` is a dot-separated path such as ``"software"`` or
    ``"software.stable"`` or ``"stable.copy-1"``. Walks into nested
    ``name = { ... };`` blocks.

    Returns the text inside the innermost matching ``{ ... }`` (exclusive
    of braces), or None if any path component is missing. Comments are
    stripped via ``strip_systemd_comments`` before matching.
    """
    body = strip_systemd_comments(text)
    remaining = body
    for name in section_path.split("."):
        # Find ``<name>\s*=\s*{``. Dashes are allowed in libconfig section
        # names (e.g. ``copy-1``).
        pat = re.compile(rf"\b{re.escape(name)}\s*=\s*\{{", re.MULTILINE)
        m = pat.search(remaining)
        if not m:
            return None
        # Brace-count to find the matching close.
        depth = 1
        i = m.end()
        while i < len(remaining) and depth:
            c = remaining[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        if depth:
            return None  # Unbalanced — treat as absent.
        remaining = remaining[m.end() : i - 1]
    return remaining


def swupdate_libconfig_has(
    text: str,
    section_path: str,
    key: str,
) -> str | None:
    """Return the RHS value of ``<key> = <value>;`` inside a libconfig section.

    Args:
        text: sw-description contents.
        section_path: dot-separated path, e.g. ``"software"`` or
            ``"software.stable.copy-1"``.
        key: directive key (e.g. ``version``, ``description``, ``format``).

    Returns:
        Trimmed RHS with outer quotes stripped and trailing ``;`` removed,
        or None if the section or key is absent. Accepts bool-ish values
        (``true``, ``1``, ``"true"``) and preserves case for comparison.
    """
    section = libconfig_section_body(text, section_path)
    if section is None:
        return None
    # Match ``key = <rhs>;`` where <rhs> is either a quoted string, an
    # array ``[ ... ]``, a bool/number literal, or anything up to ``;``.
    pat = re.compile(
        rf'^\s*{re.escape(key)}\s*=\s*(".*?"|\[.*?\]|.+?);',
        re.MULTILINE | re.DOTALL,
    )
    m = pat.search(section)
    if not m:
        return None
    val = m.group(1).strip()
    # Strip outer matched quotes only — leaves inner arrays / bool / int alone.
    if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
        val = val[1:-1]
    return val


# Matches a single `{ ... }` entry inside a libconfig list ``( ... )``.
# Used to enumerate image / file / script dict entries without parsing the
# full grammar. Brace-counting keeps nested structures intact.
def libconfig_list_entries(list_body: str) -> list[str]:
    entries: list[str] = []
    i = 0
    while i < len(list_body):
        if list_body[i] != "{":
            i += 1
            continue
        depth = 1
        start = i + 1
        j = i + 1
        while j < len(list_body) and depth:
            if list_body[j] == "{":
                depth += 1
            elif list_body[j] == "}":
                depth -= 1
            j += 1
        if depth == 0:
            entries.append(list_body[start : j - 1])
        i = j
    return entries


def libconfig_list_body(text: str, list_name: str) -> str | None:
    """Return the body of ``<list_name>: ( ... );`` or None."""
    body = strip_systemd_comments(text)
    pat = re.compile(rf"\b{re.escape(list_name)}\s*:\s*\(", re.MULTILINE)
    m = pat.search(body)
    if not m:
        return None
    # Paren-count to find matching close.
    depth = 1
    start = m.end()
    i = start
    while i < len(body) and depth:
        c = body[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        i += 1
    if depth:
        return None
    return body[start : i - 1]


def swupdate_images_has_sha256(text: str) -> bool:
    """Return True iff every entry in ``images: ( ... );`` has a ``sha256``
    field. Returns False if no ``images`` list is declared at all.
    """
    list_body = libconfig_list_body(text, "images")
    if list_body is None:
        return False
    entries = libconfig_list_entries(list_body)
    if not entries:
        return False
    sha_pat = re.compile(r"\bsha256\s*=\s*", re.MULTILINE)
    return all(sha_pat.search(e) for e in entries)


def swupdate_hardware_compatibility_list(text: str) -> list[str]:
    """Parse the top-level ``hardware-compatibility = [ "1.0", "1.2" ];``
    array and return the string values. Returns [] if the directive is
    missing or malformed.
    """
    body = strip_systemd_comments(text)
    m = re.search(
        r"\bhardware-compatibility\s*=\s*\[(.*?)\]\s*;",
        body,
        re.DOTALL,
    )
    if not m:
        return []
    # Extract double-quoted strings only; ignore anything else.
    return re.findall(r'"([^"]*)"', m.group(1))


def rauc_manifest_section_has(
    text: str,
    section: str,
    key: str,
) -> str | None:
    """Return the RHS of ``key=value`` inside ``[section]`` in a RAUC manifest.

    RAUC manifests use INI grammar with dotted section names such as
    ``[image.rootfs]`` or ``[image.rootfs.0]``. Python's ``configparser``
    treats dots as regular characters, but we implement a minimal parser
    here to avoid taking a configparser dependency on the check path.

    Args:
        text: manifest.raucm contents.
        section: full section name as written between brackets
            (e.g. ``"update"``, ``"image.rootfs"``, ``"image.rootfs.0"``).
        key: directive key (e.g. ``compatible``, ``version``, ``filename``).

    Returns:
        Trimmed RHS string (no surrounding quotes, no trailing whitespace),
        or None if section/key is absent. Last occurrence wins (matches
        INI convention).
    """
    body = strip_systemd_comments(text)
    # Allow leading whitespace before ``[section]`` — test fixtures and
    # real-world manifests are often indented.
    sec_pat = re.compile(rf"^\s*\[{re.escape(section)}\]\s*$", re.MULTILINE)
    m = sec_pat.search(body)
    if not m:
        return None
    start = m.end()
    # Next ``[...]`` header or EOF bounds the section.
    next_hdr = re.search(r"^\s*\[[^\]]+\]\s*$", body[start:], re.MULTILINE)
    end = start + next_hdr.start() if next_hdr else len(body)
    section_body = body[start:end]
    key_pat = re.compile(
        rf"^\s*{re.escape(key)}\s*=\s*(.*?)\s*$",
        re.MULTILINE,
    )
    matches = key_pat.findall(section_body)
    return matches[-1] if matches else None


def rauc_image_slots(text: str) -> list[str]:
    """Enumerate all ``[image.<slot>]`` sections in a RAUC manifest.

    Returns the slot suffix after ``image.`` — e.g. for ``[image.rootfs]``
    returns ``"rootfs"``; for ``[image.rootfs.0]`` returns ``"rootfs.0"``.
    Preserves declaration order.
    """
    body = strip_systemd_comments(text)
    return re.findall(
        r"^\s*\[image\.([^\]]+)\]\s*$",
        body,
        re.MULTILINE,
    )


# ---------------------------------------------------------------------------
# Linux networking-kernel helpers (Phase C-2).
#
# Shared by cases/embedded-linux/networking-kernel-001..005 TCs covering
# netfilter hooks, sk_buff lifecycle, netlink kernel sockets, generic
# netlink families, and netdevice notifiers. Targets linux-imx 5.15 LTS.
#
# Design notes:
#   - Each helper accepts raw or stripped code; callers pre-strip when
#     they care about string literals (the ``strip_comments`` call here
#     preserves strings but removes ``//`` and ``/* */`` which would
#     otherwise cause false positives on commented-out examples).
#   - ``has_nf_register_call`` accepts both the plural (``nf_register_net_hooks``)
#     and singular (``nf_register_net_hook``) forms — both are valid
#     on 5.15 even though the plural is preferred.
#   - ``has_netlink_kernel_api`` returns a list of detected symbols so
#     callers can assert specific endpoint-creation APIs without
#     over-matching generic netlink accessors.
# ---------------------------------------------------------------------------


def has_nf_hook_ops_struct(code: str) -> bool:
    """Detect a ``struct nf_hook_ops`` declaration (scalar or array).

    Matches:
      - ``struct nf_hook_ops ops = { ... };``
      - ``static struct nf_hook_ops ops[] = { ... };``
      - ``struct nf_hook_ops my_ops = { .hook = ... };``

    Ignores forward declarations without initialisers and ignores
    ``#include <linux/netfilter.h>`` where the identifier doesn't
    precede a variable name.
    """
    stripped = strip_comments(code)
    # Declaration with optional array brackets and optional initialiser.
    pat = re.compile(
        r"\bstruct\s+nf_hook_ops\s+\w+\s*(\[[^\]]*\])?\s*(=|;)",
    )
    return bool(pat.search(stripped))


def has_nf_register_call(code: str) -> bool:
    """Detect a netfilter hook registration call.

    Accepts BOTH ``nf_register_net_hooks`` (plural, 3-arg, preferred on
    5.15) and ``nf_register_net_hook`` (singular, legacy but still
    present). Also accepts per-namespace ``nf_register_hook`` /
    ``nf_register_hooks`` which are pre-namespace variants some
    older-style modules still use.
    """
    stripped = strip_comments(code)
    pat = re.compile(
        r"\bnf_register_(net_)?hooks?\s*\(",
    )
    return bool(pat.search(stripped))


_NETLINK_KERNEL_APIS = (
    "netlink_kernel_create",
    "netlink_kernel_release",
    "netlink_unicast",
    "netlink_broadcast",
    "nlmsg_parse",
    "nlmsg_hdr",
    "nlmsg_data",
    "nlmsg_put",
    "nlmsg_new",
    "nla_put",
    "nla_put_string",
    "nla_put_u32",
    "nla_put_u16",
    "nla_put_u8",
    "nla_get_string",
    "nla_get_u32",
)


def has_netlink_kernel_api(code: str) -> list[str]:
    """Return the list of netlink kernel-side APIs used in the code.

    Preserves call-order of first appearance in the source — not tuple
    order — so a prompt that reads "detect the first netlink API
    invoked" can assert on the returned list head. Matches identifier
    + ``(`` so struct fields named ``.input`` / ``.cfg`` don't
    false-positive. ``nla_put`` matches the prefix form — callers that
    need to distinguish ``nla_put`` vs ``nla_put_u32`` should grep the
    returned list.
    """
    stripped = strip_comments(code)
    # Scan the source left-to-right; emit each API on its first call site.
    pat = re.compile(
        r"\b(" + "|".join(re.escape(a) for a in _NETLINK_KERNEL_APIS) + r")\s*\(",
    )
    found: list[str] = []
    seen: set[str] = set()
    for m in pat.finditer(stripped):
        name = m.group(1)
        if name not in seen:
            found.append(name)
            seen.add(name)
    return found


def has_genl_family_struct(code: str) -> bool:
    """Detect a ``struct genl_family`` declaration with 5.15-era fields.

    Requires at least one of ``.ops`` / ``.small_ops`` / ``.n_ops`` to
    appear INSIDE the genl_family initializer body — this is what
    distinguishes the modern (>= 4.10) form from the deprecated
    pre-4.10 form that used ``genl_register_family_with_ops`` and
    didn't embed the ops pointer.

    Scopes the field-membership search to the ``{ ... }`` initializer
    of the genl_family declaration; a separate ``struct genl_ops`` array
    elsewhere in the file does not count.
    """
    stripped = strip_comments(code)
    m = re.search(
        r"\bstruct\s+genl_family\s+\w+\s*=\s*\{([^}]*)\}",
        stripped,
        flags=re.DOTALL,
    )
    if not m:
        return False
    body = m.group(1)
    return bool(re.search(r"\.(n_ops|ops|small_ops)\s*=", body))
