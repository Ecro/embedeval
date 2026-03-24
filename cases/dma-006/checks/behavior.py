"""Behavioral checks for DMA with buffer alignment requirements."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA aligned buffer behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Alignment value >= 4 bytes (meaningful hardware alignment)
    # Match both __aligned(32) and __aligned(ALIGN_SIZE) or similar
    align_numeric = re.findall(r"__aligned\s*\(\s*(\d+)\s*\)", generated_code)
    align_named = re.findall(r"__aligned\s*\(\s*[A-Z_][A-Z0-9_]*\s*\)", generated_code)
    if align_numeric:
        max_align = max(int(v) for v in align_numeric)
        align_sufficient = max_align >= 4
    elif align_named:
        # Named constant for alignment — assume it is valid
        align_sufficient = True
        max_align = -1  # Unknown numeric value
    else:
        max_align = 0
        align_sufficient = False
    details.append(
        CheckDetail(
            check_name="alignment_value_sufficient",
            passed=align_sufficient,
            expected="__aligned(N) with N >= 4, or __aligned(NAMED_CONSTANT)",
            actual=f"alignment: {align_numeric or align_named}" if (align_numeric or align_named) else "no __aligned() found",
            check_type="constraint",
        )
    )

    # Check 2: Both source and destination buffers declared as static arrays
    has_src = "src_buf" in generated_code or "src" in generated_code
    has_dst = "dst_buf" in generated_code or "dst" in generated_code
    both_buffers = has_src and has_dst
    details.append(
        CheckDetail(
            check_name="both_src_dst_buffers_present",
            passed=both_buffers,
            expected="Both source and destination buffers declared",
            actual=f"src={has_src}, dst={has_dst}",
            check_type="constraint",
        )
    )

    # Check 3: dma_config before dma_start
    config_pos = generated_code.find("dma_config(")
    start_pos = generated_code.find("dma_start(")
    order_ok = config_pos != -1 and start_pos != -1 and config_pos < start_pos
    details.append(
        CheckDetail(
            check_name="config_before_start",
            passed=order_ok,
            expected="dma_config() called before dma_start()",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: Semaphore used for completion synchronization
    has_sem = "k_sem_take" in generated_code or "K_SEM_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="semaphore_synchronization",
            passed=has_sem,
            expected="Semaphore used to wait for DMA completion",
            actual="present" if has_sem else "missing — busy-wait or no sync",
            check_type="constraint",
        )
    )

    # Check 5: memcmp verification or success message
    has_verify = "memcmp" in generated_code or "Aligned DMA OK" in generated_code
    details.append(
        CheckDetail(
            check_name="buffer_verified_after_dma",
            passed=has_verify,
            expected="memcmp or success message verifies transfer",
            actual="present" if has_verify else "missing verification",
            check_type="constraint",
        )
    )

    # Check 6: All __aligned(N) values must be >= 32 (cache-line alignment for DMA)
    # LLM failure: using __aligned(4) or __aligned(8) which is insufficient for DMA/cache coherency
    numeric_aligns = [int(v) for v in align_numeric]  # reuse align_numeric from Check 1
    if numeric_aligns:
        all_cache_aligned = all(v >= 32 for v in numeric_aligns)
        actual_cache_msg = (
            f"all >= 32: {numeric_aligns}"
            if all_cache_aligned
            else f"INSUFFICIENT: {[v for v in numeric_aligns if v < 32]} < 32 (DMA needs cache-line alignment)"
        )
    elif align_named:
        # Named constant — assume adequate (same as Check 1 rationale)
        all_cache_aligned = True
        actual_cache_msg = f"named constant used: {align_named} — assumed adequate"
    else:
        all_cache_aligned = False
        actual_cache_msg = "no __aligned() found"
    details.append(
        CheckDetail(
            check_name="alignment_at_least_cache_line",
            passed=all_cache_aligned,
            expected="__aligned(N) with N >= 32 for DMA cache-line safety",
            actual=actual_cache_msg,
            check_type="constraint",
        )
    )

    # Check 7: Both src and dst buffers must have __aligned attribute
    # LLM failure: aligning only dst, leaving src unaligned
    aligned_buf_lines = [
        line for line in generated_code.splitlines()
        if "__aligned" in line and re.search(r'(?:buf|buffer|src|dst)', line, re.IGNORECASE)
    ]
    aligned_buf_count = len(aligned_buf_lines)
    both_buffers_aligned = aligned_buf_count >= 2
    details.append(
        CheckDetail(
            check_name="both_buffers_aligned",
            passed=both_buffers_aligned,
            expected="Both src and dst buffer declarations include __aligned",
            actual=(
                f"{aligned_buf_count} buffer(s) with __aligned found — both present"
                if both_buffers_aligned
                else f"only {aligned_buf_count} buffer(s) with __aligned (need >= 2; likely missing src alignment)"
            ),
            check_type="constraint",
        )
    )

    return details
