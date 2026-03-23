"""Static analysis checks for reader-writer lock pattern."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate reader-writer lock structural requirements."""
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

    # Check 2: k_mutex used (for reader count protection)
    has_mutex = "k_mutex" in generated_code
    details.append(
        CheckDetail(
            check_name="k_mutex_for_reader_count",
            passed=has_mutex,
            expected="k_mutex used to protect reader_count",
            actual="present" if has_mutex else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: k_sem used (for write exclusion)
    has_sem = "k_sem" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sem_for_write_exclusion",
            passed=has_sem,
            expected="k_sem used for writer exclusion",
            actual="present" if has_sem else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: reader_count variable present
    has_reader_count = "reader_count" in generated_code or "readers" in generated_code
    details.append(
        CheckDetail(
            check_name="reader_count_variable",
            passed=has_reader_count,
            expected="reader_count (or readers) variable tracking active readers",
            actual="present" if has_reader_count else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: read_lock and write_lock (or equivalent) functions present
    has_read_lock = "read_lock" in generated_code or "rwlock_read" in generated_code
    has_write_lock = "write_lock" in generated_code or "rwlock_write" in generated_code
    details.append(
        CheckDetail(
            check_name="lock_functions_defined",
            passed=has_read_lock and has_write_lock,
            expected="Read lock and write lock functions defined",
            actual=f"read_lock={has_read_lock} write_lock={has_write_lock}",
            check_type="exact_match",
        )
    )

    # Check 6: No POSIX rwlock APIs
    posix_apis = ["pthread_rwlock_rdlock", "pthread_rwlock_wrlock", "pthread_rwlock_t"]
    has_posix = any(api in generated_code for api in posix_apis)
    details.append(
        CheckDetail(
            check_name="no_posix_rwlock",
            passed=not has_posix,
            expected="No POSIX pthread_rwlock APIs",
            actual="POSIX rwlock found" if has_posix else "clean",
            check_type="constraint",
        )
    )

    return details
