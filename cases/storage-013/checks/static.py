"""Static checks for storage-013: flash wear via rate-limited writes."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    has_settings_h = "settings/settings.h" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_header",
            passed=has_settings_h,
            expected="zephyr/settings/settings.h included",
            actual="present" if has_settings_h else "missing",
            check_type="exact_match",
        )
    )

    uses_save_one = "settings_save_one" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_save_one_used",
            passed=uses_save_one,
            expected="settings_save_one() used to persist counter",
            actual="present" if uses_save_one else "missing",
            check_type="exact_match",
        )
    )

    loads_settings = "settings_load" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_load_called",
            passed=loads_settings,
            expected="settings_load() called at startup to restore counter",
            actual="present" if loads_settings else "missing",
            check_type="exact_match",
        )
    )

    # Rate-limiting evidence — at least one of:
    # (a) modulo pattern: (counter % N) == 0
    # (b) counter-based every-N pattern with stored threshold
    # (c) uptime-based rate limit
    has_mod_pattern = bool(
        re.search(
            r"%\s*\w+\s*\)\s*==\s*0|%\s*\d+\s*\)\s*==\s*0",
            generated_code,
        )
    )
    has_every_n = bool(
        re.search(
            r"(?:every|interval|period|rate|PERSIST_EVERY|PERSIST_INTERVAL)",
            generated_code,
            re.IGNORECASE,
        )
    )
    has_uptime_limit = "k_uptime_get" in generated_code

    rate_limit_present = has_mod_pattern or has_every_n or has_uptime_limit
    details.append(
        CheckDetail(
            check_name="flash_write_rate_limited",
            passed=rate_limit_present,
            expected=(
                "Flash writes rate-limited (modulo N counter, periodic timer, "
                "or uptime-based threshold) — unconstrained persist on every "
                "10ms loop would burn through flash endurance"
            ),
            actual=(
                f"mod={has_mod_pattern}, every={has_every_n}, uptime={has_uptime_limit}"
                if rate_limit_present
                else "no rate-limit mechanism — persists on every loop iteration"
            ),
            check_type="constraint",
        )
    )

    # Save is NOT inside a tight loop without condition
    # Heuristic: if settings_save_one appears inside a for/while loop with
    # no guarding if-condition nearby, flag it
    save_in_loop_unconditional = bool(
        re.search(
            r"(?:for|while)\s*\([^)]*\)\s*\{[^}]*?settings_save_one[^}]*?\}",
            generated_code,
            re.DOTALL,
        )
    )
    # But check if there's a guarding `if` before the save
    save_has_guard = bool(
        re.search(
            r"if\s*\([^)]*\)\s*\{?\s*(?:[^{}]*?)settings_save_one",
            generated_code,
            re.DOTALL,
        )
    )
    unconditional_save = save_in_loop_unconditional and not save_has_guard
    details.append(
        CheckDetail(
            check_name="save_not_unconditional_in_loop",
            passed=not unconditional_save,
            expected="settings_save_one() guarded, not called every loop iteration",
            actual="unconditional save in loop — flash wear disaster"
            if unconditional_save
            else "guarded",
            check_type="constraint",
        )
    )

    return details
