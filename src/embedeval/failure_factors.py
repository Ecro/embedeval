"""Shared parser for `docs/LLM-EMBEDDED-FAILURE-FACTORS.md`.

Both `scripts/build_expert_pack.py` (drift detector) and
`src/embedeval/context_diagnose.py` (CLI diagnostic) need to read the
same factor tables and check-to-category mappings. Centralising the
parser here keeps them in lock-step — any change to the source-doc
structure is felt in one place.

The module intentionally exposes:

- `Factor` / `Category` — frozen dataclasses for the factor rows.
- `parse_factors` — list[Category] from raw markdown.
- `parse_check_category_map` — dict[check_name, category_letter] built
  from the `**EmbedEval checks mapped:**` trailer lines. When a check
  name appears under multiple categories (e.g. `counter_is_volatile`
  lives in both B and D), the first (alphabetical) category wins — this
  matches PLAN R6 ("first-alphabetical wins if ever needed") and keeps
  downstream rollups unambiguous.
- `FACTORS_DOC` — canonical path to the source markdown, reused by
  callers so they don't drift on relative-path assumptions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FACTORS_DOC = ROOT / "docs" / "LLM-EMBEDDED-FAILURE-FACTORS.md"


@dataclass(frozen=True)
class Factor:
    """One row parsed from a category factor table.

    `factor_id` is the A1/B3/... identifier. `strength` is the literal
    token ("High"/"Med"/"Low") and `evidence` is likewise verbatim — no
    normalization so a typo in the source doc surfaces as drift.
    """

    factor_id: str
    name: str
    strength: str
    evidence: str
    description: str


@dataclass(frozen=True)
class Category:
    """A. Hardware Awareness Gap / B. Temporal ... etc."""

    letter: str  # "A"
    title: str  # "Hardware Awareness Gap"
    factors: tuple[Factor, ...]


# Matches a category header like "## A. Hardware Awareness Gap"
_CATEGORY_RE = re.compile(r"^##\s+([A-F])\.\s+(.+?)\s*$")
# Matches a factor row like "| A1 | Register / MMIO access | Med | Research | ... |"
# Five fields between pipes, the first being the A1/B3/... id.
_ROW_RE = re.compile(
    r"^\|\s*([A-F]\d+)\s*\|\s*(.+?)\s*\|\s*(High|Med|Low)\s*\|"
    r"\s*(Empirical|Research|Theoretical)\s*\|\s*(.+?)\s*\|\s*$"
)
# Matches the trailing "**EmbedEval checks mapped:** `foo`, `bar`, ..." line.
# Capture group 1 is the backtick-wrapped comma-separated check list.
_CHECKS_MAPPED_RE = re.compile(r"^\*\*EmbedEval checks mapped:\*\*\s*(.+?)\s*$")
# Pulls individual check names out of the captured list — tolerates
# additional whitespace between items so reflowed lines keep parsing.
_CHECK_NAME_RE = re.compile(r"`([A-Za-z0-9_]+)`")


def parse_factors(markdown: str) -> list[Category]:
    """Walk the doc section-by-section, pulling factor rows out of each
    A–F table. Stops at the first `## ` header that is not A–F (e.g.
    "## Summary Statistics") so later markdown tables don't poison the
    output.
    """
    lines = markdown.splitlines()
    categories: list[Category] = []
    current_letter: str | None = None
    current_title: str | None = None
    current_rows: list[Factor] = []

    def _flush() -> None:
        nonlocal current_letter, current_title, current_rows
        if current_letter and current_title:
            categories.append(
                Category(
                    letter=current_letter,
                    title=current_title,
                    factors=tuple(current_rows),
                )
            )
        current_letter = None
        current_title = None
        current_rows = []

    for line in lines:
        # Any top-level section flushes the current category; the
        # factor tables are only inside A–F sections, so a "## Summary
        # Statistics" ends the scan.
        if line.startswith("## ") and not line.startswith("### "):
            cat_match = _CATEGORY_RE.match(line)
            _flush()
            if cat_match:
                current_letter = cat_match.group(1)
                current_title = cat_match.group(2).strip()
            continue
        if current_letter is None:
            continue
        row = _ROW_RE.match(line)
        if row:
            fid, name, strength, evidence, desc = row.groups()
            current_rows.append(
                Factor(
                    factor_id=fid,
                    name=name.strip(),
                    strength=strength,
                    evidence=evidence,
                    description=desc.strip(),
                )
            )
    _flush()
    return categories


def parse_check_category_map(markdown: str) -> dict[str, str]:
    """Return `{check_name: category_letter}` built from the
    `**EmbedEval checks mapped:**` trailer line in each A–F section.

    When the same check appears under more than one category (shared-use
    checks — e.g. `counter_is_volatile` is listed under both B and D),
    the FIRST category letter wins. Walk order matches the document
    order, which is alphabetical by letter, so the behaviour equals
    "earliest letter wins".
    """
    lines = markdown.splitlines()
    mapping: dict[str, str] = {}
    current_letter: str | None = None

    for line in lines:
        if line.startswith("## ") and not line.startswith("### "):
            cat_match = _CATEGORY_RE.match(line)
            current_letter = cat_match.group(1) if cat_match else None
            continue
        if current_letter is None:
            continue
        m = _CHECKS_MAPPED_RE.match(line)
        if not m:
            continue
        for check in _CHECK_NAME_RE.findall(m.group(1)):
            # First-seen letter wins — in-order traversal of A→F means
            # the earliest alphabetical letter claims the check.
            mapping.setdefault(check, current_letter)
    return mapping


def load_factors() -> list[Category]:
    """Convenience: read FACTORS_DOC from disk and parse it."""
    return parse_factors(FACTORS_DOC.read_text(encoding="utf-8"))


def load_check_category_map() -> dict[str, str]:
    """Convenience: read FACTORS_DOC from disk and parse the mapping."""
    return parse_check_category_map(FACTORS_DOC.read_text(encoding="utf-8"))
