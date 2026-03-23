"""Behavioral checks for Device Tree DMA channel assignment."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree DMA assignment behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: dma-names contains "tx" entry
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

    # Check 2: dma-names contains "rx" entry
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

    # Check 3: dmas count matches dma-names count
    # Each <&dma...> phandle tuple in dmas is one entry; dma-names entries are quoted strings on that line
    dmas_entries = re.findall(r"<&\w+\s+\d+\s+\d+>", generated_code)
    # Count only the dma-names string values (not all quoted strings in the file)
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

    # Check 4: DMA format uses <&controller channel slot> (3-cell format)
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

    # Check 5: status = "okay" on uart0
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

    return details
