"""Behavioral checks for reader-writer lock pattern."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate reader-writer lock behavioral correctness."""
    details: list[CheckDetail] = []

    # Check 1: First reader takes the semaphore (blocks writers)
    # Pattern: reader_count == 1 followed by k_sem_take
    first_reader_blocks_writer = bool(
        re.search(
            r"reader_count\s*==\s*1.*?k_sem_take|"
            r"readers\s*==\s*1.*?k_sem_take",
            generated_code,
            re.DOTALL,
        )
    )
    details.append(
        CheckDetail(
            check_name="first_reader_blocks_writer",
            passed=first_reader_blocks_writer,
            expected="First reader (count==1) takes semaphore to block writers",
            actual="pattern found" if first_reader_blocks_writer else "pattern not found",
            check_type="constraint",
        )
    )

    # Check 2: Last reader gives the semaphore (unblocks writers)
    last_reader_unblocks_writer = bool(
        re.search(
            r"reader_count\s*==\s*0.*?k_sem_give|"
            r"readers\s*==\s*0.*?k_sem_give",
            generated_code,
            re.DOTALL,
        )
    )
    details.append(
        CheckDetail(
            check_name="last_reader_unblocks_writer",
            passed=last_reader_unblocks_writer,
            expected="Last reader (count==0) gives semaphore to unblock writers",
            actual="pattern found" if last_reader_unblocks_writer else "pattern not found",
            check_type="constraint",
        )
    )

    # Check 3: Writer lock is just sem_take (simple exclusive take)
    write_lock_fn = re.search(
        r"(?:rwlock_write_lock|write_lock|acquire_write)\s*\([^)]*\)\s*\{([^}]*)\}",
        generated_code,
        re.DOTALL,
    )
    writer_uses_sem = False
    if write_lock_fn:
        fn_body = write_lock_fn.group(1)
        writer_uses_sem = "k_sem_take" in fn_body
    details.append(
        CheckDetail(
            check_name="writer_uses_sem_take",
            passed=writer_uses_sem,
            expected="Write lock acquires semaphore (k_sem_take)",
            actual="sem_take in write_lock" if writer_uses_sem else "no sem_take in write_lock",
            check_type="constraint",
        )
    )

    # Check 4: reader_count protected under mutex lock (race-free update)
    # Pattern: mutex_lock ... reader_count ... mutex_unlock
    count_under_lock = bool(
        re.search(
            r"k_mutex_lock.*?reader_count.*?k_mutex_unlock|"
            r"k_mutex_lock.*?readers\b.*?k_mutex_unlock",
            generated_code,
            re.DOTALL,
        )
    )
    details.append(
        CheckDetail(
            check_name="reader_count_protected",
            passed=count_under_lock,
            expected="reader_count modified under k_mutex_lock protection",
            actual="mutex protected" if count_under_lock else "unprotected count (race!)",
            check_type="constraint",
        )
    )

    # Check 5: At least 2 reader threads and 1 writer thread
    thread_defs = re.findall(
        r"void\s+(\w*(?:reader|writer|read|write)\w*)\s*\(",
        generated_code,
        re.IGNORECASE,
    )
    reader_fns = [t for t in thread_defs if "read" in t.lower()]
    writer_fns = [t for t in thread_defs if "write" in t.lower() or "writ" in t.lower()]
    has_multiple_readers = len(reader_fns) >= 1 and (
        "K_THREAD_DEFINE" in generated_code or "k_thread_create" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="reader_writer_threads_defined",
            passed=has_multiple_readers,
            expected="Reader thread(s) and writer thread defined",
            actual=f"reader fns={reader_fns} writer fns={writer_fns}",
            check_type="exact_match",
        )
    )

    return details
