"""Static analysis checks for dual-channel watchdog application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate dual-channel watchdog code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes watchdog header
    has_wdt_h = "zephyr/drivers/watchdog.h" in generated_code
    details.append(
        CheckDetail(
            check_name="watchdog_header_included",
            passed=has_wdt_h,
            expected="zephyr/drivers/watchdog.h included",
            actual="present" if has_wdt_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Calls wdt_install_timeout twice (two channels)
    install_count = generated_code.count("wdt_install_timeout")
    has_two_installs = install_count >= 2
    details.append(
        CheckDetail(
            check_name="two_channels_installed",
            passed=has_two_installs,
            expected="wdt_install_timeout() called twice for two channels",
            actual=f"{install_count} wdt_install_timeout calls found",
            check_type="exact_match",
        )
    )

    # Check 3: Uses wdt_setup
    has_setup = "wdt_setup" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_setup_called",
            passed=has_setup,
            expected="wdt_setup() called",
            actual="present" if has_setup else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Two separate channel ID variables (AI failure: using same ID for both)
    has_two_ids = (
        "ch0_id" in generated_code or "channel_id_0" in generated_code
        or generated_code.count("wdt_channel_id") >= 2
        or (
            generated_code.count("wdt_install_timeout") >= 2
            and generated_code.count("wdt_feed") >= 2
        )
    )
    details.append(
        CheckDetail(
            check_name="separate_channel_ids",
            passed=has_two_ids,
            expected="Separate channel IDs stored for each watchdog channel",
            actual="present" if has_two_ids else "may be using same channel ID",
            check_type="constraint",
        )
    )

    # Check 5: wdt_feed called at least twice (for two channels)
    feed_count = generated_code.count("wdt_feed")
    has_two_feeds = feed_count >= 2
    details.append(
        CheckDetail(
            check_name="both_channels_fed",
            passed=has_two_feeds,
            expected="wdt_feed() called for both channels",
            actual=f"{feed_count} wdt_feed calls found",
            check_type="constraint",
        )
    )

    # Check 6: device_is_ready check
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() check before WDT operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    return details
