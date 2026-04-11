"""Static checks for ota-009: confirm-or-rollback OTA pattern."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    has_mcuboot_h = "dfu/mcuboot.h" in generated_code
    details.append(
        CheckDetail(
            check_name="mcuboot_header",
            passed=has_mcuboot_h,
            expected="zephyr/dfu/mcuboot.h included",
            actual="present" if has_mcuboot_h else "missing",
            check_type="exact_match",
        )
    )

    checks_confirmed = "boot_is_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="checks_already_confirmed",
            passed=checks_confirmed,
            expected="boot_is_img_confirmed() called first",
            actual="present" if checks_confirmed else "missing",
            check_type="exact_match",
        )
    )

    calls_self_test = bool(re.search(r"\bself_test\s*\(", generated_code))
    details.append(
        CheckDetail(
            check_name="self_test_called",
            passed=calls_self_test,
            expected="self_test() called before confirming image",
            actual="present" if calls_self_test else "missing",
            check_type="constraint",
        )
    )

    confirms = "boot_write_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="confirm_api_called",
            passed=confirms,
            expected="boot_write_img_confirmed() called to mark image permanent",
            actual="present" if confirms else "missing",
            check_type="exact_match",
        )
    )

    # Confirm must only happen after self_test passes — i.e., confirm must
    # be inside a success branch, not unconditionally at top.
    # Heuristic: confirm call must appear AFTER self_test call lexically.
    st_pos = generated_code.find("self_test(")
    confirm_pos = generated_code.find("boot_write_img_confirmed")
    confirm_after_test = st_pos != -1 and confirm_pos != -1 and confirm_pos > st_pos
    details.append(
        CheckDetail(
            check_name="confirm_after_self_test",
            passed=confirm_after_test,
            expected="boot_write_img_confirmed() called lexically after self_test()",
            actual=(
                "correct order"
                if confirm_after_test
                else "confirm before test — image marked permanent before validation"
            ),
            check_type="constraint",
        )
    )

    return details
