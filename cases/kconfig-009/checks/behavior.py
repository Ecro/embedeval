"""Behavioral checks for Zephyr Shell with Logging Backend Kconfig fragment."""

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
    """Validate shell+logging Kconfig dependency chains and mutual exclusion invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    shell_enabled = config.get("CONFIG_SHELL") == "y"
    shell_log_backend_enabled = config.get("CONFIG_SHELL_LOG_BACKEND") == "y"
    log_enabled = config.get("CONFIG_LOG") == "y"
    log_minimal_enabled = config.get("CONFIG_LOG_MINIMAL") == "y"

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

    # Check 3: SHELL_LOG_BACKEND requires SHELL=y
    shell_log_needs_shell = not (shell_log_backend_enabled and not shell_enabled)
    details.append(
        CheckDetail(
            check_name="shell_log_backend_requires_shell",
            passed=shell_log_needs_shell,
            expected="SHELL_LOG_BACKEND requires SHELL=y",
            actual=(
                f"SHELL={config.get('CONFIG_SHELL', 'n')}, "
                f"SHELL_LOG_BACKEND={config.get('CONFIG_SHELL_LOG_BACKEND', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 4: SHELL_LOG_BACKEND requires LOG=y
    shell_log_needs_log = not (shell_log_backend_enabled and not log_enabled)
    details.append(
        CheckDetail(
            check_name="shell_log_backend_requires_log",
            passed=shell_log_needs_log,
            expected="SHELL_LOG_BACKEND requires LOG=y",
            actual=(
                f"LOG={config.get('CONFIG_LOG', 'n')}, "
                f"SHELL_LOG_BACKEND={config.get('CONFIG_SHELL_LOG_BACKEND', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 5: Mutual exclusion: LOG_MINIMAL and SHELL_LOG_BACKEND cannot coexist
    no_minimal_conflict = not (log_minimal_enabled and shell_log_backend_enabled)
    details.append(
        CheckDetail(
            check_name="log_minimal_shell_log_backend_mutual_exclusion",
            passed=no_minimal_conflict,
            expected="LOG_MINIMAL and SHELL_LOG_BACKEND are mutually exclusive",
            actual=(
                "no conflict"
                if no_minimal_conflict
                else "both LOG_MINIMAL=y and SHELL_LOG_BACKEND=y set (incompatible)"
            ),
            check_type="constraint",
        )
    )

    # Check 6: LOG_BUFFER_SIZE should be adequately sized if set
    buf_size_val = config.get("CONFIG_LOG_BUFFER_SIZE", "")
    buf_size_ok = True
    buf_size_int = 0
    if buf_size_val:
        try:
            buf_size_int = int(buf_size_val)
            buf_size_ok = buf_size_int >= 1024
        except ValueError:
            buf_size_ok = False
    details.append(
        CheckDetail(
            check_name="log_buffer_size_adequate",
            passed=buf_size_ok,
            expected="CONFIG_LOG_BUFFER_SIZE >= 1024 for shell log backend",
            actual=f"LOG_BUFFER_SIZE={buf_size_val!r}",
            check_type="constraint",
        )
    )

    # Check 7: LOG_BUFFER_SIZE is a power of 2 when set
    is_power_of_2 = True
    if buf_size_int > 0:
        is_power_of_2 = (buf_size_int & (buf_size_int - 1)) == 0
    details.append(
        CheckDetail(
            check_name="log_buffer_size_power_of_2",
            passed=is_power_of_2,
            expected="CONFIG_LOG_BUFFER_SIZE must be a power of 2 (e.g. 1024, 2048, 4096)",
            actual=f"LOG_BUFFER_SIZE={buf_size_val!r} ({'power of 2' if is_power_of_2 else 'NOT power of 2'})",
            check_type="constraint",
        )
    )

    # Check 8: All required configs present
    required = ["CONFIG_SHELL", "CONFIG_SHELL_LOG_BACKEND", "CONFIG_LOG"]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="SHELL, SHELL_LOG_BACKEND, LOG all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
