"""Behavioral checks for Zephyr Shell with Logging Backend Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate shell+logging Kconfig dependency chains and mutual exclusion invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    shell_enabled = config.get("CONFIG_SHELL") == "y"
    shell_log_backend_enabled = config.get("CONFIG_SHELL_LOG_BACKEND") == "y"
    log_enabled = config.get("CONFIG_LOG") == "y"
    log_minimal_enabled = config.get("CONFIG_LOG_MINIMAL") == "y"

    # Metamorphic: SHELL_LOG_BACKEND requires SHELL=y
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

    # Metamorphic: SHELL_LOG_BACKEND requires LOG=y
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

    # Mutual exclusion: LOG_MINIMAL and SHELL_LOG_BACKEND cannot coexist
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

    # Behavioral: LOG_BUFFER_SIZE should be adequately sized if set
    buf_size_val = config.get("CONFIG_LOG_BUFFER_SIZE", "")
    buf_size_ok = True
    if buf_size_val:
        try:
            buf_size_ok = int(buf_size_val) >= 1024
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

    # Summary: all required configs present
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
