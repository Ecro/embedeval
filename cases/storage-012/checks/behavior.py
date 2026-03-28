"""Behavioral checks for flash-wear-aware persistent data logger."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    has_api_call,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []
    stripped = strip_comments(generated_code)

    # Check 1: Uses NVS (not raw flash_write)
    has_nvs = (
        "nvs_read" in stripped
        or "nvs_write" in stripped
        or "settings_load" in stripped
    )
    has_raw_flash = "flash_write" in stripped and "nvs" not in stripped.lower()
    details.append(
        CheckDetail(
            check_name="uses_nvs_not_raw_flash",
            passed=has_nvs and not has_raw_flash,
            expected="NVS API used (not raw flash_write) — NVS handles wear leveling",
            actual=(
                "NVS used"
                if has_nvs
                else "raw flash_write or no persistent storage"
            ),
            check_type="constraint",
        )
    )

    # Check 2: No k_malloc in main loop (memory leak prevention)
    # Find the main loop (while/for after main function)
    main_pos = max(
        stripped.find("int main("),
        stripped.find("void main("),
        stripped.find("int main(void"),
        stripped.find("void main(void"),
    )
    if main_pos != -1:
        main_body = stripped[main_pos:]
        loop_match = re.search(r'while\s*\(|for\s*\(', main_body)
        if loop_match:
            loop_body = main_body[loop_match.start():]
            has_malloc_in_loop = (
                "k_malloc" in loop_body or "malloc" in loop_body
            )
        else:
            has_malloc_in_loop = False
    else:
        has_malloc_in_loop = False
    details.append(
        CheckDetail(
            check_name="no_malloc_in_loop",
            passed=not has_malloc_in_loop,
            expected="No k_malloc/malloc in main loop (leak prevention for long-term operation)",
            actual=(
                "clean"
                if not has_malloc_in_loop
                else "malloc in loop — memory leak over time"
            ),
            check_type="constraint",
        )
    )

    # Check 3: Static/stack allocation for buffers
    has_static_buf = bool(
        re.search(r'static\s+(?:uint\w+|int\w*|char|struct)', stripped)
    ) or bool(
        re.search(
            r'(?:uint8_t|uint16_t|uint32_t|int)\s+\w+\s*(?:\[|;)', stripped
        )
    )
    details.append(
        CheckDetail(
            check_name="static_allocation",
            passed=has_static_buf,
            expected="Static or stack allocation for data buffers (no dynamic allocation)",
            actual=(
                "static/stack allocation found"
                if has_static_buf
                else "no static allocation detected"
            ),
            check_type="constraint",
        )
    )

    # Check 4: NVS full/error handling (ENOSPC or return value check)
    has_full_handling = bool(
        re.search(
            r'ENOSPC|NVS.*full|nvs_calc_free|no.*space',
            stripped,
            re.IGNORECASE,
        )
    ) or bool(
        re.search(r'ret\s*[<!=]+\s*0.*nvs|nvs.*ret\s*[<!=]+\s*0', stripped)
    )
    details.append(
        CheckDetail(
            check_name="nvs_full_handling",
            passed=has_full_handling,
            expected="NVS full/error condition handled (ENOSPC or return value check)",
            actual=(
                "error handling found"
                if has_full_handling
                else "no NVS error handling — will fail silently when full"
            ),
            check_type="constraint",
        )
    )

    # Check 5: Counter persisted across reboots
    has_persistent_counter = (
        ("nvs_read" in stripped or "settings_runtime_get" in stripped)
        and ("nvs_write" in stripped or "settings_runtime_set" in stripped)
        and bool(
            re.search(r'count|sample|index|sequence', stripped, re.IGNORECASE)
        )
    )
    details.append(
        CheckDetail(
            check_name="persistent_counter",
            passed=has_persistent_counter,
            expected="Sample counter read from and written to NVS (survives reboot)",
            actual=(
                "persistent counter found"
                if has_persistent_counter
                else "counter not persisted"
            ),
            check_type="constraint",
        )
    )

    # Check 6: Write rate not excessive (batching or rate-limiting)
    # For long-term operation, writing every cycle without rate consideration
    # wears flash. Check for sleep >= 1 second between writes, or batching logic.
    sleep_patterns = re.findall(r'K_SECONDS\s*\(\s*(\d+)\s*\)', stripped)
    sleep_patterns += [
        str(int(m) // 1000)
        for m in re.findall(r'K_MSEC\s*\(\s*(\d+)\s*\)', stripped)
        if int(m) >= 1000
    ]
    has_rate_limit = (
        any(int(s) >= 1 for s in sleep_patterns if s.isdigit())
        if sleep_patterns
        else False
    )
    # Also accept batch/buffer patterns
    has_batch = bool(
        re.search(
            r'batch|buffer.*count|count.*threshold|BATCH_SIZE|WRITE_INTERVAL',
            stripped,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="write_rate_limited",
            passed=has_rate_limit or has_batch,
            expected="Write rate limited (>= 1s interval or batch buffering) for flash endurance",
            actual=(
                "rate-limited"
                if (has_rate_limit or has_batch)
                else "no rate limiting — excessive flash wear"
            ),
            check_type="constraint",
        )
    )

    # Check 7: Wrapping-safe counter type
    # For long-term: uint32_t counter wraps cleanly; signed int wraps with UB.
    has_unsigned_counter = bool(
        re.search(r'uint32_t\s+\w*count', stripped, re.IGNORECASE)
    ) or bool(
        re.search(r'uint64_t\s+\w*count', stripped, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="unsigned_counter_type",
            passed=has_unsigned_counter,
            expected="Counter uses uint32_t or uint64_t (not int — wraps correctly)",
            actual=(
                "unsigned type found"
                if has_unsigned_counter
                else "counter may be signed int — wrapping undefined behavior"
            ),
            check_type="constraint",
        )
    )

    # Check 8: Cross-platform contamination
    cross_plat = check_no_cross_platform_apis(
        generated_code, skip_platforms=["Linux_Userspace"]
    )
    details.append(
        CheckDetail(
            check_name="no_cross_platform_apis",
            passed=len(cross_plat) == 0,
            expected="No FreeRTOS/Arduino/STM32_HAL APIs",
            actual=(
                "clean"
                if not cross_plat
                else f"found: {[a for a, _ in cross_plat]}"
            ),
            check_type="constraint",
        )
    )

    return details
