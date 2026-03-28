"""Behavioral checks for network interface status monitoring."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate net_mgmt callback ordering and completeness."""
    details: list[CheckDetail] = []

    # Check 1: Callback registered BEFORE checking initial state
    add_cb_pos = generated_code.find("net_mgmt_add_event_callback")
    is_up_pos = generated_code.find("net_if_is_up")
    get_default_pos = generated_code.find("net_if_get_default")
    # Callback registration must happen before initial state check
    cb_before_state = (
        add_cb_pos != -1
        and (is_up_pos == -1 or add_cb_pos < is_up_pos)
        and (get_default_pos == -1 or add_cb_pos < get_default_pos or is_up_pos == -1)
    )
    details.append(
        CheckDetail(
            check_name="callback_registered_before_state_check",
            passed=cb_before_state,
            expected="net_mgmt_add_event_callback() called before initial state check",
            actual="correct" if cb_before_state else "wrong order — events may be missed",
            check_type="constraint",
        )
    )

    # Check 2: Both UP and DOWN handled in callback
    has_up = "NET_EVENT_IF_UP" in generated_code
    has_down = "NET_EVENT_IF_DOWN" in generated_code
    details.append(
        CheckDetail(
            check_name="both_up_and_down_handled",
            passed=has_up and has_down,
            expected="Both NET_EVENT_IF_UP and NET_EVENT_IF_DOWN handled",
            actual=f"up={has_up}, down={has_down}",
            check_type="constraint",
        )
    )

    # Check 3: net_if_get_default used to get interface
    has_get_default = "net_if_get_default" in generated_code
    details.append(
        CheckDetail(
            check_name="get_default_interface",
            passed=has_get_default,
            expected="net_if_get_default() used to obtain interface",
            actual="present" if has_get_default else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: net_if_is_up used for initial state check
    has_is_up = "net_if_is_up" in generated_code
    details.append(
        CheckDetail(
            check_name="initial_state_checked",
            passed=has_is_up,
            expected="net_if_is_up() used to check initial interface state",
            actual="present" if has_is_up else "missing — initial state not checked",
            check_type="exact_match",
        )
    )

    # Check 5: Event mask in init_event_callback includes both events
    has_combined_mask = (
        "NET_EVENT_IF_UP | NET_EVENT_IF_DOWN" in generated_code
        or "NET_EVENT_IF_DOWN | NET_EVENT_IF_UP" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="event_mask_includes_both",
            passed=has_combined_mask,
            expected="Event mask includes both NET_EVENT_IF_UP and NET_EVENT_IF_DOWN",
            actual="present" if has_combined_mask else "missing — incomplete event mask",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
