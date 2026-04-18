"""Tests for scripts/build_expert_pack.py.

These guard:
  - The factor-table parser's regex against table-format changes in
    LLM-EMBEDDED-FAILURE-FACTORS.md.
  - The drift detector (--check) actually exits non-zero on drift.
  - The generated coverage file is deterministic and stable.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "build_expert_pack.py"


def _load_module():
    """Import the script as a module without requiring package layout."""
    spec = importlib.util.spec_from_file_location("build_expert_pack", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_expert_pack"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def bep():
    return _load_module()


def test_parse_factors_extracts_all_six_categories(bep) -> None:
    """Sanity: the live FAILURE-FACTORS.md still yields A–F categories."""
    md = bep.FACTORS_DOC.read_text(encoding="utf-8")
    categories = bep.parse_factors(md)
    letters = [c.letter for c in categories]
    assert letters == ["A", "B", "C", "D", "E", "F"], letters
    # Every category has at least one factor row parsed
    for c in categories:
        assert len(c.factors) >= 1, f"category {c.letter} empty"


def test_parse_factors_preserves_row_fields(bep) -> None:
    """Row fields map to (id, name, strength, evidence, description)
    without collapsing pipes inside descriptions."""
    md = bep.FACTORS_DOC.read_text(encoding="utf-8")
    categories = bep.parse_factors(md)
    # A2 is documented as High + Empirical and well known
    a = next(c for c in categories if c.letter == "A")
    a2 = next(f for f in a.factors if f.factor_id == "A2")
    assert a2.strength == "High"
    assert a2.evidence == "Empirical"
    assert "init" in a2.name.lower()


def test_render_coverage_is_deterministic(bep) -> None:
    """Re-rendering the same parsed factors must produce byte-identical
    output; any nondeterminism breaks the drift detector."""
    md = bep.FACTORS_DOC.read_text(encoding="utf-8")
    categories = bep.parse_factors(md)
    out1 = bep.render_coverage(categories)
    out2 = bep.render_coverage(categories)
    assert out1 == out2


def test_render_coverage_flags_high_strength_per_category(bep) -> None:
    """Each category with any High factor must get the must-cover
    callout listing those factor IDs."""
    md = bep.FACTORS_DOC.read_text(encoding="utf-8")
    categories = bep.parse_factors(md)
    out = bep.render_coverage(categories)
    for c in categories:
        high_ids = [f.factor_id for f in c.factors if f.strength == "High"]
        if high_ids:
            assert ", ".join(high_ids) in out, (
                f"missing must-cover callout for {c.letter}: "
                f"expected ids {high_ids}"
            )


def test_check_mode_passes_when_file_is_in_sync(bep, tmp_path, monkeypatch) -> None:
    """--check exits 0 when the on-disk coverage matches rendered output."""
    md = bep.FACTORS_DOC.read_text(encoding="utf-8")
    rendered = bep.render_coverage(bep.parse_factors(md))

    target = tmp_path / "coverage.md"
    target.write_text(rendered, encoding="utf-8")
    monkeypatch.setattr(bep, "COVERAGE_OUT", target)

    rc = bep.main(["--check"])
    assert rc == 0


def test_check_mode_fails_when_file_drifts(bep, tmp_path, monkeypatch) -> None:
    """--check exits 1 when FAILURE-FACTORS.md was edited since the last
    coverage regenerate (simulated by a stale file on disk)."""
    target = tmp_path / "coverage.md"
    target.write_text("# stale placeholder\n", encoding="utf-8")
    monkeypatch.setattr(bep, "COVERAGE_OUT", target)

    rc = bep.main(["--check"])
    assert rc == 1


def test_default_mode_writes_and_is_idempotent(bep, tmp_path, monkeypatch) -> None:
    """Default mode (no flags) writes on first run, then reports
    "already up to date" on subsequent runs."""
    target = tmp_path / "coverage.md"
    monkeypatch.setattr(bep, "COVERAGE_OUT", target)

    rc1 = bep.main([])
    assert rc1 == 0
    assert target.is_file()
    first_written = target.read_text(encoding="utf-8")

    rc2 = bep.main([])
    assert rc2 == 0
    # No change on the idempotent second run
    assert target.read_text(encoding="utf-8") == first_written
