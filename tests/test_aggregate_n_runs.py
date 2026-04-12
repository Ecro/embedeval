"""Tests for scripts/aggregate_n_runs.py — Wilson CI math, archive
discovery, and end-to-end aggregation across fake run archives."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_module() -> Any:
    """Load the aggregator script as a module (it lives under scripts/
    which isn't on sys.path)."""
    script = (
        Path(__file__).resolve().parent.parent / "scripts" / "aggregate_n_runs.py"
    )
    spec = importlib.util.spec_from_file_location("aggregate_n_runs", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["aggregate_n_runs"] = mod
    spec.loader.exec_module(mod)
    return mod


agg_mod = _load_module()


# ---------- Wilson CI ----------


def test_wilson_ci_zero_trials():
    assert agg_mod.wilson_ci(0, 0) == (0.0, 0.0)


def test_wilson_ci_all_pass_narrows_with_n():
    """All-passes over small n should give a wide interval; over large n
    should give a tight one anchored near 1."""
    lo_small, hi_small = agg_mod.wilson_ci(5, 5)
    lo_big, hi_big = agg_mod.wilson_ci(500, 500)
    # Small n: interval is wide, upper bound clamped to 1
    assert hi_small == 1.0
    assert lo_small < 0.6
    # Large n: lower bound pushed up, upper bound still at (or very near) 1
    assert lo_big > lo_small
    assert hi_big >= 0.999


def test_wilson_ci_half_pass_centered_near_half():
    lo, hi = agg_mod.wilson_ci(50, 100)
    assert lo < 0.5 < hi
    # 95% CI for 50/100 should be approximately [0.40, 0.60] — allow slack
    assert 0.39 < lo < 0.42
    assert 0.58 < hi < 0.61


def test_wilson_ci_bounds_stay_in_unit_interval():
    # Edge case: 1 pass out of 1 → lo > 0, hi == 1
    lo, hi = agg_mod.wilson_ci(1, 1)
    assert 0.0 <= lo <= 1.0
    assert hi == 1.0
    # 0 pass out of 10
    lo, hi = agg_mod.wilson_ci(0, 10)
    assert lo == 0.0
    assert 0.0 < hi < 1.0


# ---------- Archive discovery / loading ----------


def _make_archive(
    runs_dir: Path,
    date: str,
    model_slug: str,
    run_id: str,
    *,
    case_results: dict[str, bool],
) -> Path:
    """Create a minimal fake run archive mirroring what
    reporter.generate_run_archive writes."""
    name = f"{date}_{model_slug}_{run_id}"
    arch = runs_dir / name
    details = arch / "details"
    details.mkdir(parents=True)

    passed = sum(1 for v in case_results.values() if v)
    total = len(case_results)
    summary = {
        "version": "0.1.0",
        "date": date,
        "models": [
            {
                "model": f"claude-code://{model_slug.split('_')[-1]}",
                "pass_at_1": passed / total if total else 0.0,
                "pass_at_5": passed / total if total else 0.0,
                "passed_cases": passed,
                "total_cases": total,
                "layer_pass_rates": {},
                "pass_at_1_ci": [0.0, 1.0],
                "n_samples": 1,
            }
        ],
        "categories": [],
        "overall": {
            "total_cases": total,
            "total_models": 1,
            "best_model": "claude-code://sonnet",
            "best_pass_at_1": passed / total if total else 0.0,
        },
        "run_id": run_id,
    }
    (arch / "summary.json").write_text(json.dumps(summary))

    for cid, ok in case_results.items():
        (details / f"{cid}.json").write_text(
            json.dumps({"case_id": cid, "passed": ok})
        )

    return arch


def test_find_run_archive_returns_latest_date(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    (runs_dir / "2026-04-10_model_n1").mkdir()
    (runs_dir / "2026-04-11_model_n1").mkdir()

    found = agg_mod.find_run_archive(runs_dir, "model", "n1")
    assert found is not None
    assert found.name.startswith("2026-04-11")


def test_find_run_archive_returns_none_when_missing(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    assert agg_mod.find_run_archive(runs_dir, "model", "nX") is None


def test_load_run_reads_summary_and_details(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    arch = _make_archive(
        runs_dir,
        "2026-04-11",
        "claude-code_sonnet",
        "n1",
        case_results={"kconfig-001": True, "kconfig-002": False},
    )

    run = agg_mod.load_run(arch, "n1")
    assert run is not None
    assert run["run_id"] == "n1"
    assert run["passed"] == 1
    assert run["total"] == 2
    assert run["per_case"] == {"kconfig-001": True, "kconfig-002": False}


def test_load_run_returns_none_for_missing_summary(tmp_path: Path):
    empty = tmp_path / "empty_arch"
    empty.mkdir()
    assert agg_mod.load_run(empty, "n1") is None


# ---------- aggregate() ----------


def test_aggregate_single_run():
    runs = [
        {
            "run_id": "n1",
            "archive": Path("."),
            "pass_at_1": 0.6,
            "passed": 6,
            "total": 10,
            "per_case": {f"c-{i:02d}": i < 6 for i in range(10)},
        }
    ]
    result = agg_mod.aggregate(runs, "test-model")
    assert result["n_runs"] == 1
    assert result["mean_pass_at_1"] == 0.6
    assert result["std_pass_at_1"] == 0.0  # single run → no stdev
    assert result["pooled_passes"] == 6
    assert result["pooled_trials"] == 10
    # Every case is "stable" trivially when n=1
    assert result["stability"] == 1.0


def test_aggregate_three_runs_mean_and_std():
    # Same case set, results that differ across runs
    cases = [f"c-{i:02d}" for i in range(10)]
    runs = [
        {
            "run_id": "n1",
            "archive": Path("."),
            "pass_at_1": 0.6,
            "passed": 6,
            "total": 10,
            "per_case": {c: i < 6 for i, c in enumerate(cases)},
        },
        {
            "run_id": "n2",
            "archive": Path("."),
            "pass_at_1": 0.7,
            "passed": 7,
            "total": 10,
            "per_case": {c: i < 7 for i, c in enumerate(cases)},
        },
        {
            "run_id": "n3",
            "archive": Path("."),
            "pass_at_1": 0.5,
            "passed": 5,
            "total": 10,
            "per_case": {c: i < 5 for i, c in enumerate(cases)},
        },
    ]
    result = agg_mod.aggregate(runs, "test-model")

    assert result["n_runs"] == 3
    assert abs(result["mean_pass_at_1"] - 0.6) < 1e-9
    assert result["std_pass_at_1"] > 0  # non-zero across n=3
    assert result["pooled_passes"] == 18  # 6+7+5
    assert result["pooled_trials"] == 30  # 3×10

    # Cases c-00..c-04 passed in all 3 runs → stable.
    # Cases c-05, c-06 flip across runs → unstable.
    # Cases c-07..c-09 failed in all 3 runs → stable.
    # So stable = 5 + 3 = 8 of 10 full-coverage cases
    assert result["full_coverage_cases"] == 10
    assert abs(result["stability"] - 0.8) < 1e-9

    # Pass-count distribution:
    # c-00..c-04 → 3
    # c-05 → 2 (passed in n2, failed in n3)
    # c-06 → 1 (passed only in n2)
    # c-07..c-09 → 0
    dist = result["pass_count_distribution"]
    assert dist == {0: 3, 1: 1, 2: 1, 3: 5}


def test_aggregate_partial_coverage_skips_case_in_stability():
    """A case missing from some runs shouldn't skew stability calc."""
    runs = [
        {
            "run_id": "n1",
            "archive": Path("."),
            "pass_at_1": 1.0,
            "passed": 1,
            "total": 1,
            "per_case": {"always": True},
        },
        {
            "run_id": "n2",
            "archive": Path("."),
            "pass_at_1": 0.5,
            "passed": 1,
            "total": 2,
            "per_case": {"always": True, "sometimes": False},
        },
    ]
    result = agg_mod.aggregate(runs, "test-model")
    # Only "always" appears in both runs → 1 full-coverage case
    assert result["full_coverage_cases"] == 1
    assert result["stability"] == 1.0
    assert result["pass_count_distribution"] == {2: 1}


# ---------- End-to-end integration ----------


def test_end_to_end_load_and_aggregate(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()

    _make_archive(
        runs_dir,
        "2026-04-11",
        "claude-code_sonnet",
        "n1",
        case_results={"a": True, "b": False},
    )
    _make_archive(
        runs_dir,
        "2026-04-11",
        "claude-code_sonnet",
        "n2",
        case_results={"a": True, "b": True},
    )
    _make_archive(
        runs_dir,
        "2026-04-11",
        "claude-code_sonnet",
        "n3",
        case_results={"a": True, "b": False},
    )

    loaded = []
    for rid in ("n1", "n2", "n3"):
        arch = agg_mod.find_run_archive(runs_dir, "claude-code_sonnet", rid)
        assert arch is not None
        run = agg_mod.load_run(arch, rid)
        assert run is not None
        loaded.append(run)

    agg = agg_mod.aggregate(loaded, "claude-code://sonnet")
    assert agg["n_runs"] == 3
    # a: 3/3 pass, b: 1/3 pass → mean = (0.5 + 1.0 + 0.5) / 3 = 0.666..
    assert abs(agg["mean_pass_at_1"] - (2 / 3)) < 1e-9
    assert agg["pooled_passes"] == 4
    assert agg["pooled_trials"] == 6
    # a is stable, b is unstable → 1/2 = 50%
    assert agg["stability"] == 0.5


def test_format_markdown_smoke(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    _make_archive(
        runs_dir,
        "2026-04-11",
        "claude-code_sonnet",
        "n1",
        case_results={"a": True, "b": False},
    )
    arch = agg_mod.find_run_archive(runs_dir, "claude-code_sonnet", "n1")
    assert arch is not None
    run = agg_mod.load_run(arch, "n1")
    assert run is not None
    md = agg_mod.format_markdown(
        agg_mod.aggregate([run], "claude-code://sonnet"), [run]
    )
    assert "claude-code://sonnet" in md
    assert "Mean pass@1" in md
    assert "Wilson" in md
    assert "Pass-count distribution" in md
