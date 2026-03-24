"""Behavioral checks for CAN bus controller Device Tree overlay."""

from embedeval.models import CheckDetail

_FAKE_DT_PROPERTIES = [
    "pin-config",
    "mux-config",
    "clock-speed",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CAN bus controller overlay behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: No fake DT properties
    found_fake = [prop for prop in _FAKE_DT_PROPERTIES if prop in generated_code]
    details.append(
        CheckDetail(
            check_name="no_fake_dt_properties",
            passed=not found_fake,
            expected="No hallucinated DT properties (pin-config, mux-config, clock-speed)",
            actual="clean" if not found_fake else f"fake properties found: {found_fake}",
            check_type="hallucination",
        )
    )

    # Check 2: can0 node enabled with status okay
    has_can0 = "&can0" in generated_code
    details.append(
        CheckDetail(
            check_name="can0_node_present",
            passed=has_can0,
            expected="&can0 node reference",
            actual="present" if has_can0 else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: status = "okay" on can0
    has_status_okay = 'status = "okay"' in generated_code
    details.append(
        CheckDetail(
            check_name="status_okay",
            passed=has_status_okay,
            expected='status = "okay"',
            actual="present" if has_status_okay else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: bus-speed = <125000> (AI failure: omits bus-speed entirely)
    has_bus_speed = "bus-speed = <125000>" in generated_code
    details.append(
        CheckDetail(
            check_name="bus_speed_125kbps",
            passed=has_bus_speed,
            expected="bus-speed = <125000>",
            actual="present" if has_bus_speed else "missing or wrong bus speed",
            check_type="exact_match",
        )
    )

    # Check 5: sample-point = <875> in permille (AI failure: uses 87 or 87.5 thinking it's percent)
    has_sample_point = "sample-point = <875>" in generated_code
    details.append(
        CheckDetail(
            check_name="sample_point_875_permille",
            passed=has_sample_point,
            expected="sample-point = <875> (permille, i.e. 87.5%)",
            actual="present" if has_sample_point else "missing or wrong value (check units: permille not percent)",
            check_type="exact_match",
        )
    )

    # Check 6: Transceiver child node with compatible string
    has_transceiver_compatible = 'compatible = "microchip,mcp2562fd"' in generated_code
    details.append(
        CheckDetail(
            check_name="transceiver_compatible",
            passed=has_transceiver_compatible,
            expected='compatible = "microchip,mcp2562fd"',
            actual="present" if has_transceiver_compatible else "missing or wrong transceiver compatible",
            check_type="exact_match",
        )
    )

    # Check 7: Transceiver child node is nested inside can0 (not at root level)
    lines = generated_code.splitlines()
    in_can0 = False
    transceiver_inside_can0 = False
    depth = 0
    can0_depth = -1
    for line in lines:
        depth += line.count("{") - line.count("}")
        if "can0" in line and "{" in line:
            in_can0 = True
            can0_depth = depth
        if in_can0 and "mcp2562fd" in line:
            transceiver_inside_can0 = True
        if in_can0 and depth < can0_depth:
            in_can0 = False
    details.append(
        CheckDetail(
            check_name="transceiver_nested_in_can0",
            passed=transceiver_inside_can0,
            expected="Transceiver child node nested inside can0 block",
            actual="nested correctly" if transceiver_inside_can0 else "not nested inside can0",
            check_type="constraint",
        )
    )

    # Check 8: No fake interrupt-map without parent node
    # LLM failure: adds interrupt-map property to CAN node (wrong — CAN doesn't use interrupt-map)
    has_interrupt_map = "interrupt-map" in generated_code
    details.append(
        CheckDetail(
            check_name="no_spurious_interrupt_map",
            passed=not has_interrupt_map,
            expected="interrupt-map should not be present in simple CAN controller overlay",
            actual=(
                "clean"
                if not has_interrupt_map
                else "interrupt-map found (hallucinated for simple CAN node)"
            ),
            check_type="hallucination",
        )
    )

    return details
