#!/usr/bin/env python3
"""Re-score an archived run's stored generations through the current evaluator.

When an *environment* or *check* fix invalidates layer results but leaves the
generations themselves valid, re-running the benchmark would pay for a whole
new set of samples. This replays the archived ``details/*.json`` code through
``evaluate()`` instead: same samples, corrected gates, zero API spend.

Prior incident (2026-09-08): on an aarch64 host the 32-bit ``native_sim``
target failed CMake configure, so 53 cases failed L1; remapping the board to
``native_sim/native/64`` then tripped the ``board != "native_sim"`` test in L2
and auto-passed runtime for ~60 cases. Both are environment bugs — the opus5
generations were fine and only needed re-scoring.

Usage:
    uv run python scripts/rescore_run.py --run-dir results/runs/2026-09-08_x_n1
    uv run python scripts/rescore_run.py --run-dir <dir> --run-id n1_rescored
    uv run python scripts/rescore_run.py --run-dir <dir> --dry-run

Set the same build environment the scored run should be measured in
(EMBEDEVAL_ENABLE_BUILD=docker, EMBEDEVAL_NATIVE_SIM_BOARD=..., Docker image
available) — exercising L1/L2 is the whole point.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from embedeval.evaluator import evaluate  # noqa: E402
from embedeval.models import EvalResult, TokenUsage  # noqa: E402
from embedeval.runner import discover_cases  # noqa: E402


class RescoreError(RuntimeError):
    """Raised when an archive cannot be re-scored."""


def load_archived_details(run_dir: Path) -> list[dict]:
    """Load every per-case detail record of an archived run.

    Raises RescoreError when the archive has no details/ directory (older
    archives predate it) or the directory is empty — re-scoring needs the
    stored generated_code, and silently producing an empty run would look
    like a 0-case model.
    """
    details_dir = run_dir / "details"
    if not details_dir.is_dir():
        raise RescoreError(
            f"{run_dir} has no details/ directory — nothing to re-score "
            "(archives written before per-case details cannot be replayed)"
        )
    records = []
    for path in sorted(details_dir.glob("*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    if not records:
        raise RescoreError(f"{details_dir} contains no case JSONs")
    return records


def archived_model(records: list[dict]) -> str:
    """Return the single model the archive belongs to.

    A run archive is per-model; a mixed archive means the caller pointed at
    something else, and merging it into one leaderboard row would be wrong.
    """
    models = {r.get("model", "") for r in records}
    if len(models) != 1:
        raise RescoreError(f"archive mixes models {sorted(models)} — refusing to merge")
    return models.pop()


def rescore_records(
    records: list[dict],
    cases_dir: Path,
    private_cases: Path | None = None,
    *,
    progress: bool = True,
) -> tuple[list[EvalResult], dict[str, Path], list[str]]:
    """Re-evaluate archived generations. Returns (results, case_dir_map, skipped)."""
    cases = list(discover_cases(cases_dir))
    if private_cases:
        cases.extend(discover_cases(private_cases))
    meta_by_id = {meta.id: (case_dir, meta) for case_dir, meta in cases}

    results: list[EvalResult] = []
    case_dir_map: dict[str, Path] = {}
    skipped: list[str] = []

    for index, record in enumerate(records, start=1):
        case_id = record["case_id"]
        found = meta_by_id.get(case_id)
        if found is None:
            # Case deleted or renamed since the run — carrying its stale
            # verdict forward would misreport the current case set.
            skipped.append(case_id)
            continue
        case_dir, meta = found

        if not record.get("generated_code"):
            # Nothing to re-score. Evaluating an empty submission would quietly
            # produce FAIL@L0 and look like a model collapse — which is exactly
            # what happened on 2026-09-09 when tracker-synthesised detail stubs
            # from a partial run overwrote the real ones in the input set.
            raise RescoreError(
                f"{case_id} has no stored generated_code — the archive holds a "
                "tracker-merged stub, not a submission. Re-score the run that "
                "actually generated this case, or re-generate it."
            )

        usage = record.get("token_usage") or {}
        result = evaluate(
            case_dir=case_dir,
            generated_code=record.get("generated_code", ""),
            model=record["model"],
            attempt=record.get("attempt", 1),
            token_usage=TokenUsage(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            cost_usd=record.get("cost_usd", 0.0) or 0.0,
            category=meta.category,
        )
        result.sdk = meta.sdk
        result.tier = meta.tier
        result.reasoning_types = meta.reasoning_types

        results.append(result)
        case_dir_map[case_id] = case_dir
        if progress:
            status = "PASS" if result.passed else f"FAIL@L{result.failed_at_layer}"
            print(f"[{index}/{len(records)}] {case_id}... {status}", flush=True)

    return results, case_dir_map, skipped


def _layer_summary(results: list[EvalResult]) -> str:
    counts: dict[str, int] = {}
    for r in results:
        key = "PASS" if r.passed else f"FAIL@L{r.failed_at_layer}"
        counts[key] = counts.get(key, 0) + 1
    return ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Archived run directory (results/runs/<date>_<model>[_<run-id>])",
    )
    parser.add_argument("--cases", type=Path, default=Path("cases"))
    parser.add_argument(
        "--private-cases",
        type=Path,
        default=None,
        help="Path to the private cases repo, if the run included them",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run id for the re-scored archive (default: reuse the original)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Re-score and print the summary without writing any artifact",
    )
    args = parser.parse_args()

    try:
        records = load_archived_details(args.run_dir)
        model = archived_model(records)
        print(f"Re-scoring {len(records)} cases from {args.run_dir} (model={model})")
        results, case_dir_map, skipped = rescore_records(
            records, args.cases, args.private_cases
        )
    except RescoreError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if skipped:
        print(f"\nSkipped {len(skipped)} case(s) missing from the case set: {skipped}")
    if not results:
        print("Error: no cases could be re-scored", file=sys.stderr)
        return 1

    passed = sum(1 for r in results if r.passed)
    print(f"\npass@1 = {passed}/{len(results)} = {passed / len(results) * 100:.1f}%")
    print(f"layers: {_layer_summary(results)}")

    if args.dry_run:
        print("\n--dry-run: no artifacts written")
        return 0

    run_id = args.run_id if args.run_id is not None else _run_id_of(args.run_dir, model)
    from embedeval.cli import publish_run_results

    json_path, leaderboard_path, run_dir, guide_path = publish_run_results(
        results=results,
        model=model,
        cases_dir=args.cases,
        output_dir=args.output_dir,
        case_dir_map=case_dir_map,
        private_cases=args.private_cases,
        run_id=run_id,
    )
    print(f"\nResults: {json_path}")
    print(f"Leaderboard: {leaderboard_path}")
    print(f"Detailed: {run_dir}/")
    if guide_path:
        print(f"Safe guide: {guide_path}")
    return 0


def _run_id_of(run_dir: Path, model: str) -> str | None:
    """Recover the run id from an archive directory name.

    Archive names are ``<date>_<model-slug>[_<run-id>]``, so the id is
    whatever trails the model slug. Returns None for archives without one.
    """
    slug = model.replace("/", "_").replace(":", "_")
    name = run_dir.name
    marker = f"_{slug}_"
    if marker in name:
        return name.split(marker, 1)[1] or None
    return None


if __name__ == "__main__":
    raise SystemExit(main())
