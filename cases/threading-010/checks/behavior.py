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

    # Check 6: Writer priority must be <= reader priority (lower number = higher priority in Zephyr)
    # LLM failure: giving writer a higher numeric priority (lower real priority) causes writer starvation
    thread_priority_ok = True  # default pass if we can't extract values
    thread_defines = re.findall(
        r"K_THREAD_DEFINE\s*\(\s*(\w+)\s*,\s*\w+\s*,\s*(\w+)\s*,\s*[^,]*,\s*[^,]*,\s*(\d+)\s*,",
        generated_code,
    )
    # Also try #define WRITER_PRIO / READER_PRIO approach
    writer_prio_define = re.search(
        r"#define\s+WRITER_PRIO\w*\s+(\d+)", generated_code, re.IGNORECASE
    )
    reader_prio_define = re.search(
        r"#define\s+READER_PRIO\w*\s+(\d+)", generated_code, re.IGNORECASE
    )
    if writer_prio_define and reader_prio_define:
        writer_prio = int(writer_prio_define.group(1))
        reader_prio = int(reader_prio_define.group(1))
        thread_priority_ok = writer_prio <= reader_prio
    elif thread_defines:
        writer_entries = [
            (name, fn, int(prio))
            for name, fn, prio in thread_defines
            if "write" in name.lower() or "write" in fn.lower()
        ]
        reader_entries = [
            (name, fn, int(prio))
            for name, fn, prio in thread_defines
            if "read" in name.lower() or "read" in fn.lower()
        ]
        if writer_entries and reader_entries:
            min_writer_prio = min(p for _, _, p in writer_entries)
            max_reader_prio = max(p for _, _, p in reader_entries)
            thread_priority_ok = min_writer_prio <= max_reader_prio
    details.append(
        CheckDetail(
            check_name="writer_priority_not_lower_than_reader",
            passed=thread_priority_ok,
            expected="Writer priority number <= reader priority number (writer has equal/higher priority)",
            actual="ok" if thread_priority_ok else "writer has lower priority - writer starvation risk",
            check_type="constraint",
        )
    )

    # Check 7: At least 2 reader threads needed to demonstrate concurrent reading
    # Count K_THREAD_DEFINE or k_thread_create where function name contains "read"
    reader_thread_defs = re.findall(
        r"K_THREAD_DEFINE\s*\(\s*\w+\s*,\s*\w+\s*,\s*(\w*read\w*)\s*,",
        generated_code,
        re.IGNORECASE,
    )
    reader_thread_creates = re.findall(
        r"k_thread_create\s*\([^,]*,[^,]*,[^,]*,\s*(\w*read\w*)\s*,",
        generated_code,
        re.IGNORECASE,
    )
    total_reader_threads = len(reader_thread_defs) + len(reader_thread_creates)
    details.append(
        CheckDetail(
            check_name="multiple_reader_threads",
            passed=total_reader_threads >= 2,
            expected="At least 2 reader threads to demonstrate concurrent reading",
            actual=f"{total_reader_threads} reader thread(s) found",
            check_type="constraint",
        )
    )

    return details
