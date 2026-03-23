"""Behavioral checks for Yocto systemd service recipe."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate systemd BitBake recipe behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: inherit systemd present
    # (LLM failure: sets SYSTEMD_SERVICE but forgets inherit systemd)
    has_inherit_systemd = "inherit systemd" in generated_code
    details.append(
        CheckDetail(
            check_name="inherits_systemd_class",
            passed=has_inherit_systemd,
            expected="inherit systemd present (required for SYSTEMD_SERVICE to work)",
            actual="present" if has_inherit_systemd else "MISSING (service not installed!)",
            check_type="constraint",
        )
    )

    # Check 2: SYSTEMD_SERVICE uses :${PN} override syntax
    # (LLM failure: using SYSTEMD_SERVICE = "..." without :${PN} = ignored)
    has_systemd_service_pn = "SYSTEMD_SERVICE:${PN}" in generated_code
    details.append(
        CheckDetail(
            check_name="systemd_service_has_pn_suffix",
            passed=has_systemd_service_pn,
            expected="SYSTEMD_SERVICE:${PN} with override syntax",
            actual="present" if has_systemd_service_pn else "MISSING :${PN} suffix (ignored in new Yocto!)",
            check_type="constraint",
        )
    )

    # Check 3: SYSTEMD_AUTO_ENABLE set to "enable"
    # (LLM failure: omitting SYSTEMD_AUTO_ENABLE means service is installed but not enabled)
    has_auto_enable = "SYSTEMD_AUTO_ENABLE" in generated_code
    details.append(
        CheckDetail(
            check_name="systemd_auto_enable_set",
            passed=has_auto_enable,
            expected="SYSTEMD_AUTO_ENABLE set so service starts at boot",
            actual="present" if has_auto_enable else "missing (service installed but not enabled)",
            check_type="constraint",
        )
    )

    # Check 4: .service file referenced in SRC_URI
    # (LLM failure: service in SYSTEMD_SERVICE but not fetched via SRC_URI)
    has_service_in_uri = ".service" in generated_code and "SRC_URI" in generated_code
    details.append(
        CheckDetail(
            check_name="service_file_in_src_uri",
            passed=has_service_in_uri,
            expected=".service file included in SRC_URI for fetching",
            actual="present" if has_service_in_uri else "MISSING (service file not fetched!)",
            check_type="constraint",
        )
    )

    # Check 5: do_install places service file under systemd_unitdir
    has_systemd_unitdir = "${systemd_unitdir}" in generated_code
    details.append(
        CheckDetail(
            check_name="service_installed_to_systemd_unitdir",
            passed=has_systemd_unitdir,
            expected="${systemd_unitdir}/system/ used for service file install path",
            actual="present" if has_systemd_unitdir else "missing (service not at correct path)",
            check_type="constraint",
        )
    )

    # Check 6: ${D} used in do_install
    has_d_prefix = "${D}" in generated_code
    details.append(
        CheckDetail(
            check_name="install_uses_d_prefix",
            passed=has_d_prefix,
            expected="${D} used in do_install (staging directory)",
            actual="present" if has_d_prefix else "MISSING (wrong install path!)",
            check_type="constraint",
        )
    )

    return details
