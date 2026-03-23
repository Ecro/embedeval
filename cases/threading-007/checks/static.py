"""Static analysis checks for thread-safe singleton initialization."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate double-check locking singleton pattern."""
    details: list[CheckDetail] = []

    # Check 1: kernel header
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: k_mutex used
    has_mutex = "k_mutex" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_mutex",
            passed=has_mutex,
            expected="k_mutex used to protect initialization",
            actual="present" if has_mutex else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Static initialized flag
    has_flag = (
        "initialized" in generated_code
        and ("bool" in generated_code or "static" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="initialized_flag_present",
            passed=has_flag,
            expected="Static bool/flag tracking initialization state",
            actual="present" if has_flag else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_mutex_lock and k_mutex_unlock both present
    has_lock = "k_mutex_lock" in generated_code
    has_unlock = "k_mutex_unlock" in generated_code
    details.append(
        CheckDetail(
            check_name="mutex_lock_unlock_paired",
            passed=has_lock and has_unlock,
            expected="Both k_mutex_lock and k_mutex_unlock present",
            actual=f"lock={has_lock} unlock={has_unlock}",
            check_type="exact_match",
        )
    )

    # Check 5: No POSIX alternatives
    posix_apis = ["pthread_once", "pthread_mutex_lock", "pthread_mutex_unlock"]
    has_posix = any(api in generated_code for api in posix_apis)
    details.append(
        CheckDetail(
            check_name="no_posix_apis",
            passed=not has_posix,
            expected="No POSIX pthread APIs",
            actual="POSIX found" if has_posix else "clean",
            check_type="constraint",
        )
    )

    return details
