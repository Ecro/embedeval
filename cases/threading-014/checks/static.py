"""Static checks for threading-014: memory ordering between threads."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    has_two_threads = (
        generated_code.count("K_THREAD_DEFINE") >= 2
        or generated_code.count("k_thread_create") >= 2
    )
    details.append(
        CheckDetail(
            check_name="two_threads_defined",
            passed=has_two_threads,
            expected="Two threads (producer and consumer) created",
            actual="present" if has_two_threads else "missing (<2 threads)",
            check_type="constraint",
        )
    )

    has_barrier = bool(
        re.search(
            r"\bcompiler_barrier\s*\(|"
            r"\batomic_thread_fence\s*\(|"
            r"\b__sync_synchronize\s*\(|"
            r"\bbarrier_dsync_fence_full\s*\(",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="explicit_memory_barrier",
            passed=has_barrier,
            expected="compiler_barrier() / atomic_thread_fence() between data+flag",
            actual="present"
            if has_barrier
            else "missing — compiler may reorder data and flag writes",
            check_type="constraint",
        )
    )

    flag_is_volatile = bool(
        re.search(
            r"\bvolatile\s+\w+\s+\w*(?:flag|ready|done|signal)\w*",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="shared_flag_volatile",
            passed=flag_is_volatile,
            expected="Shared flag declared volatile so compiler reloads on each read",
            actual="volatile flag"
            if flag_is_volatile
            else "missing — compiler may hoist flag read out of loop",
            check_type="constraint",
        )
    )

    has_wait_loop = bool(
        re.search(
            r"while\s*\(\s*\w*(?:flag|ready)\w*\s*==?\s*0",
            generated_code,
            re.IGNORECASE,
        )
    ) or bool(
        re.search(
            r"while\s*\(\s*!\s*\w*(?:flag|ready)\w*",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="consumer_waits_for_flag",
            passed=has_wait_loop,
            expected="Consumer waits (while/poll) for flag to be set",
            actual="wait loop present" if has_wait_loop else "missing",
            check_type="constraint",
        )
    )

    return details
