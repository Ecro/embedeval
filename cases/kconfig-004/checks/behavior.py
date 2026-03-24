"""Behavioral checks for Zephyr logging Kconfig fragment (metamorphic properties)."""

from embedeval.models import CheckDetail

_HALLUCINATED_CONFIGS = [
    "CONFIG_SECURE_MODE",
    "CONFIG_WIFI_BLE_COEX",
    "CONFIG_DEBUG_ENABLE",
    "CONFIG_NETWORK_STACK",
    "CONFIG_AUTO_INIT",
]


def _parse_config(generated_code: str) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate logging Kconfig mutual exclusion and buffer invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    log_enabled = config.get("CONFIG_LOG") == "y"
    deferred_enabled = config.get("CONFIG_LOG_MODE_DEFERRED") == "y"
    immediate_enabled = config.get("CONFIG_LOG_MODE_IMMEDIATE") == "y"
    uart_backend_enabled = config.get("CONFIG_LOG_BACKEND_UART") == "y"
    buffer_size_raw = config.get("CONFIG_LOG_BUFFER_SIZE", "0")

    # Check 1: No hallucinated CONFIG options
    found_hallucinated = [opt for opt in _HALLUCINATED_CONFIGS if opt in generated_code]
    details.append(
        CheckDetail(
            check_name="no_hallucinated_config_options",
            passed=not found_hallucinated,
            expected="No hallucinated Zephyr CONFIG options",
            actual="clean" if not found_hallucinated else f"hallucinated: {found_hallucinated}",
            check_type="hallucination",
        )
    )

    # Check 2: Deprecated option conflict check
    has_newlib = config.get("CONFIG_NEWLIB_LIBC") == "y"
    has_minimal = config.get("CONFIG_MINIMAL_LIBC") == "y"
    no_deprecated_conflict = not (has_newlib and has_minimal)
    details.append(
        CheckDetail(
            check_name="no_newlib_minimal_libc_conflict",
            passed=no_deprecated_conflict,
            expected="CONFIG_NEWLIB_LIBC and CONFIG_MINIMAL_LIBC are mutually exclusive",
            actual=(
                "no conflict"
                if no_deprecated_conflict
                else "both CONFIG_NEWLIB_LIBC=y and CONFIG_MINIMAL_LIBC=y present (conflict)"
            ),
            check_type="constraint",
        )
    )

    # Check 3: Mutual exclusion: LOG_MODE_DEFERRED and LOG_MODE_IMMEDIATE cannot both be enabled
    no_mode_conflict = not (deferred_enabled and immediate_enabled)
    details.append(
        CheckDetail(
            check_name="log_mode_mutual_exclusion",
            passed=no_mode_conflict,
            expected="LOG_MODE_DEFERRED and LOG_MODE_IMMEDIATE are mutually exclusive",
            actual=(
                f"DEFERRED={config.get('CONFIG_LOG_MODE_DEFERRED', 'n')}, "
                f"IMMEDIATE={config.get('CONFIG_LOG_MODE_IMMEDIATE', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 4: Metamorphic: LOG_BACKEND_UART requires LOG=y
    backend_requires_log = not (uart_backend_enabled and not log_enabled)
    details.append(
        CheckDetail(
            check_name="log_backend_requires_log",
            passed=backend_requires_log,
            expected="LOG_BACKEND_UART requires LOG=y",
            actual=(
                f"LOG={config.get('CONFIG_LOG', 'n')}, "
                f"LOG_BACKEND_UART={config.get('CONFIG_LOG_BACKEND_UART', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 5: LOG_BUFFER_SIZE must be > 0 when deferred mode is enabled
    try:
        buffer_size = int(buffer_size_raw)
    except ValueError:
        buffer_size = 0

    buffer_valid = not deferred_enabled or buffer_size > 0
    details.append(
        CheckDetail(
            check_name="log_buffer_size_positive",
            passed=buffer_valid,
            expected="LOG_BUFFER_SIZE > 0 when LOG_MODE_DEFERRED=y",
            actual=f"LOG_BUFFER_SIZE={buffer_size_raw}, DEFERRED={config.get('CONFIG_LOG_MODE_DEFERRED', 'n')}",
            check_type="constraint",
        )
    )

    # Check 6: LOG_BUFFER_SIZE is a power of 2 (Zephyr requirement when set)
    # LLM failure: uses arbitrary values like 1000 instead of 1024, 2048, etc.
    is_power_of_2 = True
    if buffer_size > 0:
        is_power_of_2 = (buffer_size & (buffer_size - 1)) == 0
    details.append(
        CheckDetail(
            check_name="log_buffer_size_power_of_2",
            passed=is_power_of_2,
            expected="CONFIG_LOG_BUFFER_SIZE must be a power of 2 (e.g. 1024, 2048, 4096)",
            actual=f"LOG_BUFFER_SIZE={buffer_size_raw} ({'power of 2' if is_power_of_2 else 'NOT power of 2'})",
            check_type="constraint",
        )
    )

    # Check 7: All required configs present AND enabled (or set)
    required_y = ["CONFIG_LOG", "CONFIG_LOG_BACKEND_UART", "CONFIG_LOG_MODE_DEFERRED"]
    all_present = all(config.get(k) == "y" for k in required_y) and buffer_size > 0
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="LOG, LOG_BACKEND_UART, LOG_MODE_DEFERRED all =y and LOG_BUFFER_SIZE > 0",
            actual=str(
                {k: config.get(k, "missing") for k in required_y}
                | {"CONFIG_LOG_BUFFER_SIZE": buffer_size_raw}
            ),
            check_type="exact_match",
        )
    )

    return details
