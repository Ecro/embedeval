"""Behavioral checks for threading-014.

This TC is L2-skipped (memory ordering cannot be reliably validated at
runtime on native_sim). Behavior file exists for framework symmetry.
"""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Flag write should come AFTER data write in the producer.
    # LLM failure: sets flag first, then writes data.
    data_pos = generated_code.find("shared_value")
    flag_set_pos = -1
    for m in [" = 1", "=1", " = true"]:
        idx = generated_code.find(f"ready_flag{m}")
        if idx != -1 and (flag_set_pos == -1 or idx < flag_set_pos):
            flag_set_pos = idx

    # Ordering check only fires when identifiable tokens are found
    correct_order = True
    if data_pos != -1 and flag_set_pos != -1:
        # Find the FIRST write to shared_value (assignment, not declaration)
        for m in ["shared_value ="]:
            first_write = generated_code.find(m)
            if first_write != -1:
                correct_order = first_write < flag_set_pos
                break

    details.append(
        CheckDetail(
            check_name="data_before_flag_ordering",
            passed=correct_order,
            expected="Data write lexically precedes flag-set (with barrier between)",
            actual="correct order"
            if correct_order
            else "flag set before or without data write",
            check_type="constraint",
        )
    )

    return details
