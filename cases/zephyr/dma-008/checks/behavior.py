"""Behavioral checks for DMA error handling with callback status check."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code
from embedeval.check_utils import strip_comments


_ERROR_FLAG_DECL = re.compile(
    r"(?P<qualifiers>(?:static\s+|volatile\s+)*)"
    r"(?P<type>atomic_t|_Atomic\s+\w+|(?:unsigned\s+|signed\s+)?"
    r"(?:int|long|short|char|bool|uint\d+_t|int\d+_t))\s+"
    r"(?P<name>\w*(?:error|err)\w*)\s*(?:=|;|\[)",
)


def _find_error_flag(code_only: str) -> "re.Match[str] | None":
    """Locate the declaration of the DMA error flag.

    Matches the *declaration* rather than any ``*err*`` token so the
    ``error_callback_dis`` field of ``struct dma_config`` is not mistaken for
    the flag, and covers both storage choices: ``volatile int dma_error_flag``
    and ``atomic_t dma_error``.
    """
    return _ERROR_FLAG_DECL.search(code_only)


def _branch_after(code: str, start: int) -> str:
    """Return the branch body that begins at ``start``.

    Handles both ``{ ... }`` blocks and braceless single statements — a
    ``if (flag) return -EIO;`` guard is as much a return path as a braced one,
    and searching for the next ``{`` would wander into an unrelated block.
    """
    semicolon = code.find(";", start)
    open_brace = code.find("{", start)
    if open_brace == -1 or (semicolon != -1 and semicolon < open_brace):
        return code[start : semicolon + 1] if semicolon != -1 else code[start:]
    depth = 0
    for i in range(open_brace, len(code)):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                return code[open_brace : i + 1]
    return code[open_brace:]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA error handling behavioral properties and domain invariants."""
    details: list[CheckDetail] = []
    # Comment-free view: the checks below reason about declarations, call order
    # and branch bodies, none of which should be satisfiable from prose.
    code_only = strip_comments(generated_code)
    flag_decl = _find_error_flag(code_only)
    error_flag_name = flag_decl.group("name") if flag_decl else None
    flag_is_atomic = bool(flag_decl) and "atomic" in flag_decl.group("type")
    flag_is_volatile = bool(flag_decl) and "volatile" in flag_decl.group("qualifiers")

    # Check 1: Callback inspects the status parameter (status != 0 check)
    has_status_check = (
        scoped_contains(generated_code, 'status != 0', scope='code_only')
        or scoped_contains(generated_code, 'status < 0', scope='code_only')
        or scoped_contains(generated_code, 'if (status)', scope='code_only')
        or scoped_contains(generated_code, 'if(status)', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="callback_checks_status_parameter",
            passed=has_status_check,
            expected="DMA callback checks status parameter for non-zero (error) value",
            actual="present" if has_status_check else "missing status check in callback",
            check_type="constraint",
        )
    )

    # Check 2: the error flag itself must survive compiler optimisation and the
    # callback/thread race — `volatile` or `atomic_t` on the *flag* (not on some
    # buffer next to it). atomic_t is the stronger choice: volatile alone gives
    # no atomicity, so rejecting it punished the more correct answer.
    has_volatile_flag = flag_is_volatile or flag_is_atomic
    details.append(
        CheckDetail(
            check_name="error_flag_is_volatile",
            passed=has_volatile_flag,
            expected="Error flag declared volatile or atomic_t (not a plain int)",
            actual=(
                f"{flag_decl.group('type')} {error_flag_name}"
                if has_volatile_flag
                else "missing volatile/atomic on error flag — may be optimized away"
            ),
            check_type="constraint",
        )
    )

    # Check 3: dma_stop called on error (in callback or after)
    dma_stop_pos = find_in_code(generated_code, "dma_stop(")
    has_dma_stop = dma_stop_pos != -1
    details.append(
        CheckDetail(
            check_name="dma_stop_on_error",
            passed=has_dma_stop,
            expected="dma_stop() called when DMA error is detected",
            actual="present" if has_dma_stop else "missing — DMA channel not stopped on error",
            check_type="constraint",
        )
    )

    # Check 4: Error flag checked after semaphore wait in main
    # Use rfind to find the LAST usage of the error flag (the check in main, not the declaration)
    sem_pos = code_only.find("k_sem_take")
    if error_flag_name:
        # Last occurrence = the read in main (atomic_get(&flag) counts), not the
        # declaration.
        error_flag_last_pos = code_only.rfind(error_flag_name)
    else:
        error_flag_last_pos = -1
    error_checked_after_wait = (
        sem_pos != -1
        and error_flag_last_pos != -1
        and error_flag_last_pos > sem_pos
    )
    details.append(
        CheckDetail(
            check_name="error_flag_checked_after_wait",
            passed=error_checked_after_wait,
            expected="Error flag checked after semaphore wait (in main, not just in callback)",
            actual="correct order" if error_checked_after_wait else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 5: dma_stop present in code (error path guard)
    has_stop_near_error = has_dma_stop
    details.append(
        CheckDetail(
            check_name="dma_stop_in_error_path",
            passed=has_stop_near_error,
            expected="dma_stop() present in error-handling path",
            actual="present" if has_stop_near_error else "dma_stop missing from error path",
            check_type="constraint",
        )
    )

    # Check 6: Inside callback body, error flag is set when status != 0
    # LLM failure: checking status but not propagating it to the error flag
    callback_match = re.search(
        r'void\s+\w*(?:dma_callback|callback)\w*\s*\([^)]*(?:status)[^)]*\)\s*\{',
        generated_code, re.IGNORECASE
    )
    if not callback_match:
        # Broader fallback: any function with "callback" in name
        callback_match = re.search(
            r'void\s+\w*callback\w*\s*\([^{]*\)\s*\{',
            generated_code, re.IGNORECASE
        )
    if callback_match:
        cb_body_start = callback_match.end()
        cb_body = generated_code[cb_body_start:cb_body_start + 1000]
        status_check_match = re.search(r'if\s*\(\s*status|if\s*\(status', cb_body)
        if status_check_match:
            after_status_check = cb_body[status_check_match.start():status_check_match.start() + 200]
            # Recording the error can be an assignment or an atomic store —
            # `atomic_set(&dma_error, status)` propagates it exactly like
            # `dma_error_flag = 1`, and requiring `=` failed the atomic form.
            flag_pattern = re.escape(error_flag_name) if error_flag_name else r"\w*(?:error|err)\w*"
            flag_set_in_error = bool(
                re.search(r'(?:dma_error\w*|error_flag|error_status)\s*=\s*(?!\s*0\b)', after_status_check)
            ) or bool(
                re.search(
                    rf"atomic_(?:set|or|add|inc)\s*\(\s*&?{flag_pattern}",
                    after_status_check,
                )
            )
            actual_cb_msg = (
                "error flag set within status check branch"
                if flag_set_in_error
                else "status checked but error flag NOT set in that branch"
            )
        else:
            flag_set_in_error = False
            actual_cb_msg = "no status check (if status) found in callback body"
    else:
        flag_set_in_error = False
        actual_cb_msg = "callback function with status parameter not found"
    details.append(
        CheckDetail(
            check_name="callback_sets_flag_on_error_status",
            passed=flag_set_in_error,
            expected="Inside callback: when status != 0, error flag is assigned (not just checked)",
            actual=actual_cb_msg,
            check_type="constraint",
        )
    )

    # Check 7 (new): Error flag check in main actually causes a return/abort.
    # LLM failure: reads the flag and prints a message but never returns on error,
    # allowing execution to proceed as if the DMA completed successfully.
    # Find error flag check in main — use the detected variable name
    # The guard may test the flag directly (`if (dma_error_flag != 0)`) or a
    # local snapshot of it (`err = atomic_get(&dma_error); if (err != 0)`).
    # Either way the *branch body* must leave — a `return 0;` at the end of main
    # is not error handling.
    error_causes_return = False
    if error_flag_name:
        tail = code_only[sem_pos:] if sem_pos != -1 else code_only
        snapshots = set(
            re.findall(rf"(\w+)\s*=[^;]*\b{re.escape(error_flag_name)}\b", tail)
        )
        guarded_names = {error_flag_name} | snapshots
        for guard in re.finditer(r"if\s*\(([^)]*)\)", tail):
            if not any(re.search(rf"\b{re.escape(n)}\b", guard.group(1)) for n in guarded_names):
                continue
            branch = _branch_after(tail, guard.end())
            if "return" in branch or "goto" in branch:
                error_causes_return = True
                break
    details.append(
        CheckDetail(
            check_name="error_flag_causes_return",
            passed=error_causes_return,
            expected="Error flag check followed by a return (not just a log message)",
            actual="return present after error check" if error_causes_return else "error checked but no return — execution continues on error",
            check_type="constraint",
        )
    )

    # Check 8: Error flag read AFTER k_sem_take (not before synchronization)
    # LLM failure: reading error flag before waiting for DMA completion semaphore
    sem_take_pos = code_only.rfind("k_sem_take")
    # Reuse the already-detected error flag variable name
    error_flag_name_c7 = error_flag_name
    if error_flag_name_c7 and sem_take_pos != -1:
        # The flag must be read after the wait and that read must feed a branch.
        # Matching only `if (flag` missed `err = atomic_get(&flag); if (err)`.
        tail = code_only[sem_take_pos:]
        flag_read = tail.find(error_flag_name_c7)
        error_check_in_tail = flag_read != -1 and bool(
            re.search(r"if\s*\(", tail[flag_read:])
        )
        actual_order_msg = (
            "correct: error flag checked after k_sem_take"
            if error_check_in_tail
            else "error flag check not found after last k_sem_take (checked too early or missing)"
        )
    elif sem_take_pos == -1:
        error_check_in_tail = False
        actual_order_msg = "k_sem_take not found — cannot verify ordering"
    else:
        error_check_in_tail = False
        actual_order_msg = "error flag variable not identified — cannot verify ordering"
    details.append(
        CheckDetail(
            check_name="error_flag_read_after_sync",
            passed=error_check_in_tail,
            expected="Error flag checked (if dma_error_flag) AFTER k_sem_take completes",
            actual=actual_order_msg,
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
