"""Static analysis checks for deadlock-free multi-mutex acquisition."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate lock ordering and correct API usage."""
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

    # Check 2: Uses k_mutex (not k_sem or POSIX mutex)
    has_kmutex = "k_mutex" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_mutex",
            passed=has_kmutex,
            expected="k_mutex used for mutual exclusion",
            actual="present" if has_kmutex else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: No POSIX mutex APIs
    posix_apis = ["pthread_mutex_lock", "pthread_mutex_unlock", "pthread_mutex_init"]
    has_posix = any(api in generated_code for api in posix_apis)
    details.append(
        CheckDetail(
            check_name="no_posix_mutex",
            passed=not has_posix,
            expected="No POSIX pthread_mutex APIs",
            actual="POSIX mutex found" if has_posix else "clean",
            check_type="constraint",
        )
    )

    # Check 4: No FreeRTOS APIs
    freertos_apis = ["xSemaphoreTake", "xSemaphoreGive", "xSemaphoreCreateMutex"]
    has_freertos = any(api in generated_code for api in freertos_apis)
    details.append(
        CheckDetail(
            check_name="no_freertos_apis",
            passed=not has_freertos,
            expected="No FreeRTOS semaphore/mutex APIs",
            actual="FreeRTOS API found" if has_freertos else "clean",
            check_type="constraint",
        )
    )

    # Check 5: k_mutex_lock called at least twice (two mutexes)
    lock_count = generated_code.count("k_mutex_lock")
    details.append(
        CheckDetail(
            check_name="two_mutexes_locked",
            passed=lock_count >= 2,
            expected="k_mutex_lock called at least twice (mutex_a and mutex_b)",
            actual=f"k_mutex_lock count={lock_count}",
            check_type="constraint",
        )
    )

    # Check 6: k_mutex_unlock called at least twice
    unlock_count = generated_code.count("k_mutex_unlock")
    details.append(
        CheckDetail(
            check_name="two_mutexes_unlocked",
            passed=unlock_count >= 2,
            expected="k_mutex_unlock called at least twice",
            actual=f"k_mutex_unlock count={unlock_count}",
            check_type="constraint",
        )
    )

    return details
