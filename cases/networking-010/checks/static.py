"""Static analysis checks for network interface status monitoring."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate net_mgmt event callback code structure."""
    details: list[CheckDetail] = []

    has_net_mgmt_h = "zephyr/net/net_mgmt.h" in generated_code
    details.append(
        CheckDetail(
            check_name="net_mgmt_header",
            passed=has_net_mgmt_h,
            expected="zephyr/net/net_mgmt.h included",
            actual="present" if has_net_mgmt_h else "missing",
            check_type="exact_match",
        )
    )

    has_net_if_h = "zephyr/net/net_if.h" in generated_code
    details.append(
        CheckDetail(
            check_name="net_if_header",
            passed=has_net_if_h,
            expected="zephyr/net/net_if.h included",
            actual="present" if has_net_if_h else "missing",
            check_type="exact_match",
        )
    )

    has_init_cb = "net_mgmt_init_event_callback" in generated_code
    details.append(
        CheckDetail(
            check_name="net_mgmt_init_callback",
            passed=has_init_cb,
            expected="net_mgmt_init_event_callback() called",
            actual="present" if has_init_cb else "missing",
            check_type="exact_match",
        )
    )

    has_add_cb = "net_mgmt_add_event_callback" in generated_code
    details.append(
        CheckDetail(
            check_name="net_mgmt_add_callback",
            passed=has_add_cb,
            expected="net_mgmt_add_event_callback() called to register",
            actual="present" if has_add_cb else "missing — callback never registered",
            check_type="exact_match",
        )
    )

    has_if_up_event = "NET_EVENT_IF_UP" in generated_code
    details.append(
        CheckDetail(
            check_name="net_event_if_up_used",
            passed=has_if_up_event,
            expected="NET_EVENT_IF_UP event mask used",
            actual="present" if has_if_up_event else "missing",
            check_type="exact_match",
        )
    )

    has_if_down_event = "NET_EVENT_IF_DOWN" in generated_code
    details.append(
        CheckDetail(
            check_name="net_event_if_down_used",
            passed=has_if_down_event,
            expected="NET_EVENT_IF_DOWN event mask used",
            actual="present" if has_if_down_event else "missing",
            check_type="exact_match",
        )
    )

    return details
