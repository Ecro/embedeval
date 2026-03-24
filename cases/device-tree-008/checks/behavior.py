"""Behavioral checks for Device Tree DMA channel assignment."""

import re

from embedeval.models import CheckDetail

_FAKE_DT_PROPERTIES = [
    "pin-config",
    "mux-config",
    "clock-speed",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree DMA assignment behavioral properties and domain invariants."""
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

    # Check 2: dma-names contains "tx" entry
    has_tx_name = '"tx"' in generated_code
    details.append(
        CheckDetail(
            check_name="dma_names_has_tx",
            passed=has_tx_name,
            expected='dma-names includes "tx" entry',
            actual="present" if has_tx_name else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: dma-names contains "rx" entry
    has_rx_name = '"rx"' in generated_code
    details.append(
        CheckDetail(
            check_name="dma_names_has_rx",
            passed=has_rx_name,
            expected='dma-names includes "rx" entry',
            actual="present" if has_rx_name else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: dmas count matches dma-names count
    dmas_entries = re.findall(r"<&\w+\s+\d+\s+\d+>", generated_code)
    dma_names_line = re.search(r"dma-names\s*=\s*([^;]+);", generated_code)
    if dma_names_line:
        dma_names_entries = re.findall(r'"[^"]+"', dma_names_line.group(1))
    else:
        dma_names_entries = []
    counts_match = len(dmas_entries) == len(dma_names_entries) and len(dmas_entries) >= 1
    details.append(
        CheckDetail(
            check_name="dmas_count_matches_names",
            passed=counts_match,
            expected="dmas entry count equals dma-names entry count",
            actual=f"dmas={len(dmas_entries)}, dma-names={len(dma_names_entries)}",
            check_type="constraint",
        )
    )

    # Check 5: DMA format uses <&controller channel slot> (3-cell format)
    has_three_cell_format = bool(re.search(r"<&\w+\s+\d+\s+\d+>", generated_code))
    details.append(
        CheckDetail(
            check_name="dma_three_cell_format",
            passed=has_three_cell_format,
            expected="DMA entries use <&controller channel slot> 3-cell format",
            actual="present" if has_three_cell_format else "wrong format or missing",
            check_type="constraint",
        )
    )

    # Check 6: status = "okay" on uart0
    has_status_okay = 'status = "okay"' in generated_code
    details.append(
        CheckDetail(
            check_name="uart0_status_okay",
            passed=has_status_okay,
            expected='status = "okay"',
            actual="present" if has_status_okay else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: uart0 node referenced (not some other peripheral)
    has_uart0 = "&uart0" in generated_code
    details.append(
        CheckDetail(
            check_name="uart0_node_referenced",
            passed=has_uart0,
            expected="&uart0 node referenced",
            actual="present" if has_uart0 else "missing — DMA assigned to wrong node",
            check_type="constraint",
        )
    )

    # Check 8: DMA channel numbers are distinct (tx channel != rx channel)
    # LLM failure: assigns same channel to both tx and rx
    all_dma_entries = re.findall(r"<&(\w+)\s+(\d+)\s+(\d+)>", generated_code)
    channels_distinct = True
    if len(all_dma_entries) >= 2:
        channels = [int(e[1]) for e in all_dma_entries]
        channels_distinct = len(set(channels)) == len(channels)
    details.append(
        CheckDetail(
            check_name="dma_channels_distinct",
            passed=channels_distinct,
            expected="TX and RX DMA channels must be different channel numbers",
            actual=(
                "distinct"
                if channels_distinct
                else f"duplicate channels: {[int(e[1]) for e in all_dma_entries]}"
            ),
            check_type="constraint",
        )
    )

    # Check 9: DMA slot values are in valid range (0-15 for STM32)
    # LLM failure: generates invalid slot numbers like 99 or 255
    slot_values = [int(s) for s in re.findall(r"<&\w+\s+\d+\s+(\d+)>", generated_code)]
    slots_valid = all(0 <= s <= 127 for s in slot_values) if slot_values else True
    details.append(
        CheckDetail(
            check_name="dma_slot_values_reasonable",
            passed=slots_valid,
            expected="All DMA slot values between 0 and 127 (valid STM32 DMA/DMAMUX request slots)",
            actual=(
                "valid" if slots_valid else f"invalid slot values found: {[s for s in slot_values if not 0 <= s <= 127]}"
            ),
            check_type="constraint",
        )
    )

    # Check 10: In dma-names, "tx" must appear before "rx"
    # LLM failure: swaps tx/rx order, causing TX/RX mismatch with dmas property
    tx_rx_order_ok = True
    if dma_names_line:
        names_str = dma_names_line.group(1)
        tx_pos = names_str.find('"tx"')
        rx_pos = names_str.find('"rx"')
        if tx_pos != -1 and rx_pos != -1:
            tx_rx_order_ok = tx_pos < rx_pos
    details.append(
        CheckDetail(
            check_name="tx_rx_ordering_in_dma_names",
            passed=tx_rx_order_ok,
            expected='"tx" appears before "rx" in dma-names (matches dmas property TX-first ordering)',
            actual="correct" if tx_rx_order_ok else 'WRONG ORDER: "rx" appears before "tx" in dma-names',
            check_type="constraint",
        )
    )

    return details
