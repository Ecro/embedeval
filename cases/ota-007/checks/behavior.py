"""Behavioral checks for OTA progress reporting."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA progress reporting behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Total size known before the download loop
    # (LLM failure: computing or discovering total size inside the loop)
    total_def_pos = generated_code.find("TOTAL_IMAGE_SIZE")
    if total_def_pos == -1:
        total_def_pos = generated_code.find("total_size")
    loop_pos = generated_code.find("for (") if "for (" in generated_code else generated_code.find("while (")
    details.append(
        CheckDetail(
            check_name="total_size_known_before_loop",
            passed=total_def_pos != -1 and (loop_pos == -1 or total_def_pos < loop_pos),
            expected="Total image size defined/known before the download loop",
            actual="correct" if (total_def_pos != -1 and (loop_pos == -1 or total_def_pos < loop_pos))
                   else "total size missing or defined inside loop",
            check_type="constraint",
        )
    )

    # Check 2: Progress reported inside the loop (after each chunk)
    # (LLM failure: reporting progress only at end)
    # Use rfind to find the last (call-site) occurrence, not the definition
    progress_pos = generated_code.rfind("report_progress")
    if progress_pos == -1:
        progress_pos = generated_code.lower().rfind("progress")
    details.append(
        CheckDetail(
            check_name="progress_inside_loop",
            passed=progress_pos != -1 and loop_pos != -1 and progress_pos > loop_pos,
            expected="Progress reported inside the download loop (after each chunk)",
            actual="correct" if (progress_pos != -1 and loop_pos != -1 and progress_pos > loop_pos)
                   else "progress missing or only at end of download",
            check_type="constraint",
        )
    )

    # Check 3: Division-by-zero guard before percentage
    # (LLM failure: dividing by total without checking for zero)
    has_zero_guard = (
        "total == 0" in generated_code
        or "total_size == 0" in generated_code
        or "total > 0" in generated_code
        or "!= 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="div_zero_guard_active",
            passed=has_zero_guard,
            expected="Division-by-zero guard present before percentage calculation",
            actual="present" if has_zero_guard else "missing — divide by zero possible!",
            check_type="constraint",
        )
    )

    # Check 4: bytes_received counter uses a wide type (not uint8_t)
    # (LLM failure: using uint8_t which overflows at 256 bytes)
    has_narrow_counter = (
        "uint8_t bytes_received" in generated_code
        or "uint8_t received" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="counter_not_uint8",
            passed=not has_narrow_counter,
            expected="bytes_received is NOT uint8_t (would overflow at 256 bytes)",
            actual="correct (wide type)" if not has_narrow_counter
                   else "WRONG — uint8_t overflows on images > 255 bytes!",
            check_type="constraint",
        )
    )

    # Check 5: dfu_target_done called after all chunks written
    done_pos = generated_code.find("dfu_target_done")
    details.append(
        CheckDetail(
            check_name="dfu_done_after_loop",
            passed=done_pos != -1 and loop_pos != -1 and done_pos > loop_pos,
            expected="dfu_target_done() called after download loop completes",
            actual="correct" if (done_pos != -1 and loop_pos != -1 and done_pos > loop_pos)
                   else "missing or called before loop ends",
            check_type="constraint",
        )
    )

    return details
