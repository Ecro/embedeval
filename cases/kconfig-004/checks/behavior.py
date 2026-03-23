"""Behavioral checks for Zephyr logging Kconfig fragment (metamorphic properties)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate logging Kconfig mutual exclusion and buffer invariants."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    config: dict[str, str] = {}
    for line in lines:
        if "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    log_enabled = config.get("CONFIG_LOG") == "y"
    deferred_enabled = config.get("CONFIG_LOG_MODE_DEFERRED") == "y"
    immediate_enabled = config.get("CONFIG_LOG_MODE_IMMEDIATE") == "y"
    uart_backend_enabled = config.get("CONFIG_LOG_BACKEND_UART") == "y"
    buffer_size_raw = config.get("CONFIG_LOG_BUFFER_SIZE", "0")

    # Mutual exclusion: LOG_MODE_DEFERRED and LOG_MODE_IMMEDIATE cannot both be enabled
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

    # Metamorphic: LOG_BACKEND_UART requires LOG=y
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

    # Domain invariant: LOG_BUFFER_SIZE must be > 0 when deferred mode is enabled
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

    # Check: all required configs present AND enabled (or set)
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
