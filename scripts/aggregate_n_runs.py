"""Aggregate n=k benchmark runs per model into mean / std / 95% CI.

Reads `results/runs/<date>_<model_slug>_<run_id>/summary.json` plus
each run's `details/*.json` for the named run_ids, then reports:

- per-run pass@1
- mean pass@1 across runs
- sample stdev
- Wilson 95% confidence interval over pooled trials (n_runs × cases)
- per-case stability (fraction of cases where every run agrees)
- pass-count distribution (cases passing k-of-n runs)

Usage:
    uv run python scripts/aggregate_n_runs.py \\
        --model claude-code://sonnet \\
        --run-ids n1,n2,n3

    uv run python scripts/aggregate_n_runs.py \\
        --model claude-code://sonnet \\
        --run-ids n1,n2,n3 \\
        --output docs/BENCHMARK-n3-sonnet.md
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, stdev
from typing import Any, TypedDict


class RunSummary(TypedDict):
    run_id: str
    archive: Path
    pass_at_1: float
    passed: int
    total: int
    per_case: dict[str, bool]


def wilson_ci(
    passes: int, trials: int, z: float = 1.96
) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Returns (lo, hi) bounds in [0, 1]. For trials == 0 returns (0, 0).
    """
    if trials <= 0:
        return (0.0, 0.0)
    p = passes / trials
    z2 = z * z
    denom = 1.0 + z2 / trials
    center = (p + z2 / (2 * trials)) / denom
    margin = (
        z * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials)) / denom
    )
    lo = max(0.0, center - margin)
    hi = min(1.0, center + margin)
    return (lo, hi)


def find_run_archive(
    runs_dir: Path, model_slug: str, run_id: str
) -> Path | None:
    """Find the (latest) run archive matching `*_<model_slug>_<run_id>`.

    Multiple dates match in theory — prefer the lexicographically latest,
    which for ISO dates equals the most recent.
    """
    matches = sorted(runs_dir.glob(f"*_{model_slug}_{run_id}"))
    return matches[-1] if matches else None


def load_run(archive: Path, run_id: str) -> RunSummary | None:
    """Load one run's aggregated summary + per-case pass/fail map."""
    summary_file = archive / "summary.json"
    if not summary_file.is_file():
        return None

    try:
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    if not summary.get("models"):
        return None
    ms = summary["models"][0]

    per_case: dict[str, bool] = {}
    details_dir = archive / "details"
    if details_dir.is_dir():
        for case_file in sorted(details_dir.glob("*.json")):
            try:
                data = json.loads(case_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            cid = data.get("case_id")
            if cid:
                per_case[cid] = bool(data.get("passed", False))

    return RunSummary(
        run_id=run_id,
        archive=archive,
        pass_at_1=float(ms.get("pass_at_1", 0.0)),
        passed=int(ms.get("passed_cases", 0)),
        total=int(ms.get("total_cases", 0)),
        per_case=per_case,
    )


def aggregate(runs: list[RunSummary], model: str) -> dict[str, Any]:
    """Compute aggregate statistics from a list of loaded runs."""
    n = len(runs)
    pass_rates = [r["pass_at_1"] for r in runs]

    # Pool trials for the Wilson CI: one trial per case per run
    total_passes = sum(r["passed"] for r in runs)
    total_trials = sum(r["total"] for r in runs)
    lo, hi = wilson_ci(total_passes, total_trials)

    mean_rate = mean(pass_rates) if pass_rates else 0.0
    std_rate = stdev(pass_rates) if n > 1 else 0.0

    # Per-case stability: case_id appearing in all runs with the same result
    all_case_ids: set[str] = set()
    for r in runs:
        all_case_ids.update(r["per_case"].keys())

    pass_count_per_case: dict[str, int] = {}
    stable_count = 0
    full_coverage_count = 0
    for cid in all_case_ids:
        appearances = [r["per_case"][cid] for r in runs if cid in r["per_case"]]
        if len(appearances) != n:
            # case missing from some runs — skip stability calc for this one
            continue
        full_coverage_count += 1
        if len(set(appearances)) == 1:
            stable_count += 1
        pass_count_per_case[cid] = sum(1 for a in appearances if a)

    stability = (
        stable_count / full_coverage_count if full_coverage_count else 0.0
    )
    pass_dist: Counter[int] = Counter(pass_count_per_case.values())

    return {
        "model": model,
        "n_runs": n,
        "pass_rates": pass_rates,
        "mean_pass_at_1": mean_rate,
        "std_pass_at_1": std_rate,
        "ci95_wilson": (lo, hi),
        "pooled_passes": total_passes,
        "pooled_trials": total_trials,
        "stability": stability,
        "stable_cases": stable_count,
        "full_coverage_cases": full_coverage_count,
        "pass_count_distribution": dict(sorted(pass_dist.items())),
    }


def format_markdown(agg: dict[str, Any], runs: list[RunSummary]) -> str:
    lines: list[str] = [
        f"# n={agg['n_runs']} aggregate — {agg['model']}",
        "",
        "## Per-run pass@1",
        "",
        "| Run | pass@1 | passed | total |",
        "|-----|--------|--------|-------|",
    ]
    for r in runs:
        lines.append(
            f"| {r['run_id']} | {r['pass_at_1']:.1%} "
            f"| {r['passed']} | {r['total']} |"
        )

    lo, hi = agg["ci95_wilson"]
    lines += [
        "",
        "## Aggregate",
        "",
        f"- Mean pass@1: **{agg['mean_pass_at_1']:.1%}**",
        f"- Sample stdev: {agg['std_pass_at_1']:.2%}",
        (
            f"- 95% CI (Wilson, pooled n×cases="
            f"{agg['pooled_trials']}): [{lo:.1%}, {hi:.1%}]"
        ),
        (
            f"- Case stability: {agg['stability']:.1%} "
            f"({agg['stable_cases']}/{agg['full_coverage_cases']}"
            f" stable across all runs)"
        ),
        "",
        "## Pass-count distribution",
        "",
        f"| Passed in k of {agg['n_runs']} runs | Cases |",
        "|------------------------|-------|",
    ]
    for k, count in agg["pass_count_distribution"].items():
        lines.append(f"| {k} | {count} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default="results", type=Path)
    ap.add_argument(
        "--model",
        required=True,
        help="Model name, e.g. 'claude-code://sonnet'",
    )
    ap.add_argument(
        "--run-ids",
        required=True,
        help="Comma-separated run ids, e.g. 'n1,n2,n3'",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional Markdown output path (stdout always prints the report)",
    )
    args = ap.parse_args()

    model_slug = args.model.replace("/", "_").replace(":", "_")
    run_ids = [r.strip() for r in args.run_ids.split(",") if r.strip()]
    if not run_ids:
        print("error: --run-ids was empty after parsing", file=sys.stderr)
        return 2

    runs_dir = args.results / "runs"
    if not runs_dir.is_dir():
        print(f"error: {runs_dir} is not a directory", file=sys.stderr)
        return 2

    runs: list[RunSummary] = []
    missing: list[str] = []
    for rid in run_ids:
        archive = find_run_archive(runs_dir, model_slug, rid)
        if archive is None:
            missing.append(rid)
            continue
        loaded = load_run(archive, rid)
        if loaded is None:
            missing.append(rid)
            continue
        runs.append(loaded)

    if missing:
        print(
            f"warning: {len(missing)} run archive(s) missing or unreadable: "
            f"{', '.join(missing)}",
            file=sys.stderr,
        )
    if not runs:
        print("error: no run archives loaded — aborting", file=sys.stderr)
        return 1

    agg = aggregate(runs, args.model)
    md = format_markdown(agg, runs)
    print(md)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print(f"[wrote] {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
