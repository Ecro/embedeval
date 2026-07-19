"""Tests for scripts/compare_models_intersection.py — majority-vote verdicts,
intersection/difference delta, and improved/regressed classification.

The interesting logic is pure (no I/O), so these drive it with literals."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_module() -> Any:
    script = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "compare_models_intersection.py"
    )
    spec = importlib.util.spec_from_file_location("compare_models_intersection", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["compare_models_intersection"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()


# ---------- majority_pass ----------


def test_majority_pass_n3_needs_two():
    CV = mod.CaseVerdict
    assert mod.majority_pass(CV(passes=2, n_runs=3, category="adc")) is True
    assert mod.majority_pass(CV(passes=1, n_runs=3, category="adc")) is False
    assert mod.majority_pass(CV(passes=3, n_runs=3, category="adc")) is True
    assert mod.majority_pass(CV(passes=0, n_runs=3, category="adc")) is False


def test_majority_pass_n1_needs_one():
    CV = mod.CaseVerdict
    assert mod.majority_pass(CV(passes=1, n_runs=1, category="x")) is True
    assert mod.majority_pass(CV(passes=0, n_runs=1, category="x")) is False


def test_majority_pass_zero_runs_is_fail():
    CV = mod.CaseVerdict
    assert mod.majority_pass(CV(passes=0, n_runs=0, category="x")) is False


def test_majority_pass_n2_tie_is_fail():
    """n=2 needs >= ceil(3/2)=2, so a 1-1 tie must NOT count as pass."""
    CV = mod.CaseVerdict
    assert mod.majority_pass(CV(passes=1, n_runs=2, category="x")) is False
    assert mod.majority_pass(CV(passes=2, n_runs=2, category="x")) is True


# ---------- build_model_result ----------


def test_build_model_result_folds_runs():
    runs = [
        {"a": True, "b": False, "c": True},
        {"a": True, "b": True, "c": False},
        {"a": False, "b": False, "c": True},
    ]
    cats = {"a": "adc", "b": "ble", "c": "dma"}
    res = mod.build_model_result("m", runs, cats)
    assert res.n_runs == 3
    assert res.per_case["a"].passes == 2  # T,T,F
    assert res.per_case["b"].passes == 1  # F,T,F
    assert res.per_case["c"].passes == 2  # T,F,T
    assert res.per_case["a"].category == "adc"
    # per-run pass@1 over each run's own cases: 2/3, 2/3, 1/3
    assert res.per_run_pass_rate[0] == 2 / 3
    assert res.per_run_pass_rate[2] == 1 / 3


def test_build_model_result_missing_from_some_runs():
    """A case absent from a run counts only over the runs it appeared in."""
    runs = [{"a": True}, {"a": True, "b": False}, {"b": True}]
    res = mod.build_model_result("m", runs, {})
    assert res.per_case["a"].n_runs == 2
    assert res.per_case["a"].passes == 2
    assert res.per_case["b"].n_runs == 2
    assert res.per_case["b"].passes == 1
    assert res.per_case["a"].category == "unknown"  # not in cats map


def test_build_model_result_empty_run_no_zero_division():
    res = mod.build_model_result("m", [{}], {})
    assert res.per_run_pass_rate == [0.0]
    assert res.per_case == {}


# ---------- compute_delta ----------


def _mk(mod_ref: Any, name: str, verdicts: dict[str, tuple[int, int, str]]):
    """Build a ModelResult directly from {id: (passes, n_runs, cat)}."""
    per_case = {
        cid: mod_ref.CaseVerdict(passes=p, n_runs=n, category=c)
        for cid, (p, n, c) in verdicts.items()
    }
    return mod_ref.ModelResult(
        model=name, n_runs=3, per_case=per_case, per_run_pass_rate=[]
    )


def test_compute_delta_intersection_and_new_only():
    new = _mk(
        mod,
        "new",
        {
            "common_pass": (3, 3, "adc"),
            "common_fail": (0, 3, "ble"),
            "improved": (3, 3, "dma"),
            "regressed": (0, 3, "spi-i2c"),
            "new_only_pass": (2, 3, "networking"),
            "new_only_fail": (1, 3, "networking"),
        },
    )
    base = _mk(
        mod,
        "base",
        {
            "common_pass": (3, 3, "adc"),
            "common_fail": (0, 3, "ble"),
            "improved": (0, 3, "dma"),  # base fail
            "regressed": (3, 3, "spi-i2c"),  # base pass
            "dropped": (3, 3, "timer"),  # only in base
        },
    )
    d = mod.compute_delta(new, base)

    assert set(d.intersection_ids) == {
        "common_pass",
        "common_fail",
        "improved",
        "regressed",
    }
    assert set(d.new_only_ids) == {"new_only_pass", "new_only_fail"}
    assert d.dropped_ids == ["dropped"]

    # common pass counts: base passes {common_pass, regressed} = 2
    assert d.base_pass_on_common == 2
    # new passes {common_pass, improved} = 2
    assert d.new_pass_on_common == 2
    # new-only passes: only new_only_pass (2/3) = 1
    assert d.new_pass_on_new_only == 1

    assert d.improved == ["improved"]
    assert d.regressed == ["regressed"]


def test_compute_delta_empty_intersection():
    new = _mk(mod, "new", {"x": (3, 3, "adc")})
    base = _mk(mod, "base", {"y": (3, 3, "ble")})
    d = mod.compute_delta(new, base)
    assert d.intersection_ids == []
    assert d.new_only_ids == ["x"]
    assert d.dropped_ids == ["y"]
    assert d.base_pass_on_common == 0
    assert d.new_pass_on_common == 0
    assert d.improved == []
    assert d.regressed == []


def test_compute_delta_no_new_only():
    new = _mk(mod, "new", {"x": (3, 3, "adc")})
    base = _mk(mod, "base", {"x": (0, 3, "adc"), "y": (3, 3, "ble")})
    d = mod.compute_delta(new, base)
    assert d.new_only_ids == []
    assert d.new_pass_on_new_only == 0
    assert d.improved == ["x"]


# ---------- format_markdown (smoke) ----------


def test_format_markdown_runs_and_reports_delta():
    new = mod.ModelResult(
        model="new",
        n_runs=3,
        per_case={
            "a": mod.CaseVerdict(3, 3, "adc"),
            "b": mod.CaseVerdict(3, 3, "ble"),
        },
        per_run_pass_rate=[1.0, 1.0, 1.0],
    )
    base = mod.ModelResult(
        model="base",
        n_runs=3,
        per_case={
            "a": mod.CaseVerdict(3, 3, "adc"),
            "b": mod.CaseVerdict(0, 3, "ble"),
        },
        per_run_pass_rate=[0.5, 0.5, 0.5],
    )
    delta = mod.compute_delta(new, base)
    md = mod.format_markdown(new, base, delta)
    assert "Benchmark Delta" in md
    assert "+50.0%p" in md  # base 50% -> new 100% on the 2 common cases
    assert "Intersection" in md
