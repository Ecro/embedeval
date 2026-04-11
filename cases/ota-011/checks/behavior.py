"""Behavioral checks for ota-009."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Rollback path exists: self_test failure path leaves image unconfirmed
    # (no confirm call in that branch)
    has_rollback_branch = bool(
        re.search(
            r"self_test\s*\(\s*\)\s*!=\s*0|"
            r"!\s*self_test\s*\(\s*\)|"
            r"if\s*\(\s*\w*\s*=\s*self_test",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="self_test_failure_branch",
            passed=has_rollback_branch,
            expected="Branch on self_test() result so failure path skips confirm",
            actual="branch present"
            if has_rollback_branch
            else "no failure branch — confirm always runs",
            check_type="constraint",
        )
    )

    # Rollback-related output keyword present (any of)
    has_rollback_msg = "rollback" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="rollback_reported",
            passed=has_rollback_msg,
            expected="Rollback path prints a status message (e.g. 'rollback pending')",
            actual="present" if has_rollback_msg else "missing",
            check_type="constraint",
        )
    )

    return details
