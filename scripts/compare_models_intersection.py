"""Compare two models' n=k benchmark runs on their COMMON case set.

Motivation: the public case set grew (233 -> 267) between the stored Sonnet 4.6
n=3 run (2026-04-12) and a later run of a newer model. A raw pass@1 difference
therefore mixes *model improvement* with *case-set change*. This script isolates
the pure model delta by comparing only the cases both models actually ran
(the intersection), and reports cases unique to the newer run separately.

Per-case verdict is a **majority vote** across each model's k runs (for k=3,
>= 2 of 3 passing = pass) so a single flaky run does not flip a case.

Reads the same archive layout as `aggregate_n_runs.py`:
    results/runs/<date>_<model_slug>_<run_id>/summary.json
    results/runs/<date>_<model_slug>_<run_id>/details/*.json
    (each detail JSON carries case_id, category, passed)

Usage:
    uv run python scripts/compare_models_intersection.py \\
        --new-model claude-code://claude-sonnet-5 --new-run-ids n1,n2,n3 \\
        --base-model claude-code://sonnet --base-run-ids n1,n2,n3 \\
        --output docs/BENCHMARK-DELTA-sonnet5-vs-sonnet46.md
"""

from __future__ import annotations

import argparse
import sys
from math import ceil
from pathlib import Path
from typing import NamedTuple

# Reuse the archive-resolution + per-run loading already battle-tested in the
# aggregator, so both tools agree on what "a run" is.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate_n_runs import find_run_archive, load_run  # noqa: E402


class CaseVerdict(NamedTuple):
    """A single case's majority-vote result for one model."""

    passes: int  # number of runs (of n_runs) that passed
    n_runs: int  # number of runs this case actually appeared in
    category: str


def majority_pass(v: CaseVerdict) -> bool:
    """True if the case passed in a strict majority of the runs it appeared in.

    For n_runs=3 this needs 2; for n_runs=1 it needs 1. A case that appeared in
    zero runs is treated as a fail (never happens for loaded cases).
    """
    if v.n_runs <= 0:
        return False
    return v.passes >= ceil((v.n_runs + 1) / 2)


class ModelResult(NamedTuple):
    """All per-case verdicts for one model across its k runs."""

    model: str
    n_runs: int
    per_case: dict[str, CaseVerdict]
    per_run_pass_rate: list[float]  # each run's pass@1 over ITS OWN cases


def build_model_result(
    model: str,
    per_run_passed: list[dict[str, bool]],
    per_run_category: dict[str, str],
) -> ModelResult:
    """Fold a model's per-run pass maps into per-case majority verdicts.

    `per_run_passed` is one {case_id: passed} dict per run.
    `per_run_category` maps case_id -> category (merged across runs).
    Pure function — no I/O — so tests can drive it with literals.
    """
    n_runs = len(per_run_passed)
    all_ids: set[str] = set()
    for run in per_run_passed:
        all_ids.update(run.keys())

    per_case: dict[str, CaseVerdict] = {}
    for cid in all_ids:
        appearances = [run[cid] for run in per_run_passed if cid in run]
        per_case[cid] = CaseVerdict(
            passes=sum(1 for p in appearances if p),
            n_runs=len(appearances),
            category=per_run_category.get(cid, "unknown"),
        )

    per_run_rate = [
        (sum(1 for p in run.values() if p) / len(run)) if run else 0.0
        for run in per_run_passed
    ]
    return ModelResult(
        model=model,
        n_runs=n_runs,
        per_case=per_case,
        per_run_pass_rate=per_run_rate,
    )


class Delta(NamedTuple):
    intersection_ids: list[str]
    new_only_ids: list[str]  # in new model, absent from base
    dropped_ids: list[str]  # in base model, absent from new
    base_pass_on_common: int
    new_pass_on_common: int
    new_pass_on_new_only: int
    improved: list[str]  # base fail -> new pass (on common)
    regressed: list[str]  # base pass -> new fail (on common)


def compute_delta(new: ModelResult, base: ModelResult) -> Delta:
    """Intersection/difference delta between two models' majority verdicts.

    Pure function. `improved`/`regressed` are computed over the common set only.
    """
    new_ids = set(new.per_case)
    base_ids = set(base.per_case)
    common = sorted(new_ids & base_ids)
    new_only = sorted(new_ids - base_ids)
    dropped = sorted(base_ids - new_ids)

    base_pass = sum(1 for c in common if majority_pass(base.per_case[c]))
    new_pass = sum(1 for c in common if majority_pass(new.per_case[c]))
    new_only_pass = sum(1 for c in new_only if majority_pass(new.per_case[c]))

    improved = [
        c
        for c in common
        if majority_pass(new.per_case[c]) and not majority_pass(base.per_case[c])
    ]
    regressed = [
        c
        for c in common
        if majority_pass(base.per_case[c]) and not majority_pass(new.per_case[c])
    ]
    return Delta(
        intersection_ids=common,
        new_only_ids=new_only,
        dropped_ids=dropped,
        base_pass_on_common=base_pass,
        new_pass_on_common=new_pass,
        new_pass_on_new_only=new_only_pass,
        improved=improved,
        regressed=regressed,
    )


def _category_breakdown(ids: list[str], result: ModelResult) -> dict[str, str]:
    """Group case ids by category -> 'id (cat)' listing helper."""
    by_cat: dict[str, list[str]] = {}
    for cid in ids:
        cat = result.per_case[cid].category
        by_cat.setdefault(cat, []).append(cid)
    return {cat: ", ".join(sorted(v)) for cat, v in sorted(by_cat.items())}


def _load_model(
    results_dir: Path, model: str, run_ids: list[str]
) -> tuple[list[dict[str, bool]], dict[str, str]]:
    """Load one model's n runs into per-run pass maps + a category map."""
    model_slug = model.replace("/", "_").replace(":", "_")
    runs_dir = results_dir / "runs"
    per_run_passed: list[dict[str, bool]] = []
    per_run_category: dict[str, str] = {}
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
        per_run_passed.append(loaded["per_case"])
        # Categories live in each detail JSON; harvest them once per case.
        details_dir = archive / "details"
        if details_dir.is_dir():
            import json

            for cf in details_dir.glob("*.json"):
                try:
                    d = json.loads(cf.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    continue
                cid = d.get("case_id")
                if cid and cid not in per_run_category:
                    per_run_category[cid] = d.get("category", "unknown")

    if missing:
        print(
            f"warning: {model} missing run(s): {', '.join(missing)}",
            file=sys.stderr,
        )
    return per_run_passed, per_run_category


def format_markdown(new: ModelResult, base: ModelResult, delta: Delta) -> str:
    n_common = len(delta.intersection_ids)
    n_new = len(delta.new_only_ids)
    base_rate = delta.base_pass_on_common / n_common if n_common else 0.0
    new_rate = delta.new_pass_on_common / n_common if n_common else 0.0
    new_only_rate = delta.new_pass_on_new_only / n_new if n_new else 0.0
    delta_pp = (new_rate - base_rate) * 100

    def _mean(xs: list[float]) -> float:
        return sum(xs) / len(xs) if xs else 0.0

    lines: list[str] = [
        f"# Benchmark Delta — {new.model} vs {base.model}",
        "",
        "**Pure model improvement is the INTERSECTION row.** The two models ran",
        "different case sets; only the common cases isolate model capability",
        "from case-set change. Cases unique to the newer run are reported",
        "separately (absolute performance only — no baseline to diff against).",
        "",
        "## Per-case verdict method",
        "",
        f"- {new.model}: majority vote of {new.n_runs} runs (>= "
        f"{ceil((new.n_runs + 1) / 2)} of {new.n_runs} passing = pass)",
        f"- {base.model}: majority vote of {base.n_runs} runs (>= "
        f"{ceil((base.n_runs + 1) / 2)} of {base.n_runs} passing = pass)",
        "",
        "## Case-set overlap",
        "",
        "| Set | Cases |",
        "|-----|-------|",
        f"| Intersection (both models) | {n_common} |",
        f"| New-only (in {new.model}) | {n_new} |",
        f"| Dropped (only in {base.model}) | {len(delta.dropped_ids)} |",
        "",
        "## Pure model improvement (intersection only)",
        "",
        "| Model | pass@1 (majority) | passed / total |",
        "|-------|-------------------|----------------|",
        f"| {base.model} | {base_rate:.1%} "
        f"| {delta.base_pass_on_common} / {n_common} |",
        f"| {new.model} | {new_rate:.1%} | {delta.new_pass_on_common} / {n_common} |",
        f"| **Delta** | **{delta_pp:+.1f}%p** | — |",
        "",
        "### Per-run pass@1 (each over its own full case set, for reference)",
        "",
        f"- {base.model}: "
        + ", ".join(f"{r:.1%}" for r in base.per_run_pass_rate)
        + f" (mean {_mean(base.per_run_pass_rate):.1%})",
        f"- {new.model}: "
        + ", ".join(f"{r:.1%}" for r in new.per_run_pass_rate)
        + f" (mean {_mean(new.per_run_pass_rate):.1%})",
        "",
        f"## New-only cases ({n_new}) — {new.model} absolute performance",
        "",
        f"- pass@1 (majority): **{new_only_rate:.1%}** "
        f"({delta.new_pass_on_new_only} / {n_new})",
        "- No baseline: these cases did not exist in the older run.",
        "",
        f"## Improved: {base.model} fail -> {new.model} pass ({len(delta.improved)})",
        "",
    ]
    imp = _category_breakdown(delta.improved, new)
    if imp:
        lines += ["| Category | Cases |", "|----------|-------|"]
        lines += [f"| {cat} | {ids} |" for cat, ids in imp.items()]
    else:
        lines.append("_none_")

    lines += [
        "",
        f"## Regressed: {base.model} pass -> {new.model} fail ({len(delta.regressed)})",
        "",
    ]
    reg = _category_breakdown(delta.regressed, new)
    if reg:
        lines += ["| Category | Cases |", "|----------|-------|"]
        lines += [f"| {cat} | {ids} |" for cat, ids in reg.items()]
    else:
        lines.append("_none_")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default="results", type=Path)
    ap.add_argument("--new-model", required=True)
    ap.add_argument("--new-run-ids", required=True)
    ap.add_argument("--base-model", required=True)
    ap.add_argument("--base-run-ids", required=True)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    new_ids = [r.strip() for r in args.new_run_ids.split(",") if r.strip()]
    base_ids = [r.strip() for r in args.base_run_ids.split(",") if r.strip()]

    new_passed, new_cats = _load_model(args.results, args.new_model, new_ids)
    base_passed, base_cats = _load_model(args.results, args.base_model, base_ids)
    if not new_passed or not base_passed:
        print("error: one model has no loadable runs — aborting", file=sys.stderr)
        return 1

    merged_cats = {**base_cats, **new_cats}
    new = build_model_result(args.new_model, new_passed, merged_cats)
    base = build_model_result(args.base_model, base_passed, merged_cats)
    delta = compute_delta(new, base)

    md = format_markdown(new, base, delta)
    print(md)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
        print(f"[wrote] {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
