#!/usr/bin/env python3
"""Verify benchmark results by cross-checking generated code against check scripts.

Post-benchmark verification step that detects false results:
1. Re-runs check scripts on generated code → compares with stored results
2. Runs check scripts on reference solutions → failures = check script bugs
3. Reports l1_skip cases (reference can't compile for target board)
4. Reports discrepancies and false negatives with code context

Usage:
    uv run python scripts/verify_results.py results/runs/DATE_MODEL/
    uv run python scripts/verify_results.py results/runs/DATE_MODEL/ --verbose
    uv run python scripts/verify_results.py results/runs/DATE_MODEL/ --category dma
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

# Resolve case dirs through the shared walker so this script understands the
# 2-level SDK-bucket layout (cases/<sdk>/<case-id>/) instead of assuming a flat
# cases/<case-id>/ path. Without this, every lookup misses and the script
# silently verifies 0 cases while reporting "all OK" (a false all-clear).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from embedeval.runner import iter_case_dirs  # noqa: E402


def build_case_map(roots: list[Path]) -> dict[str, Path]:
    """Map case_id -> case dir across one or more roots (public + private).

    Later roots win on a case_id collision, matching the runner's own
    last-writer-wins behavior for shadowed ids.
    """
    case_map: dict[str, Path] = {}
    for root in roots:
        for case_dir in iter_case_dirs(root):
            case_map[case_dir.name] = case_dir
    return case_map


def load_check_module(case_dir: Path, module_name: str) -> ModuleType | None:
    """Load a check module from the case's checks/ directory."""
    module_path = case_dir / "checks" / f"{module_name}.py"
    if not module_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(
        f"verify_checks.{case_dir.name}.{module_name}", module_path
    )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"  WARNING: Failed to load {module_path}: {exc}", file=sys.stderr)
        return None
    return module


def run_checks(case_dir: Path, code: str, module_name: str) -> list[dict] | None:
    """Run check module on code, return list of {check_name, passed} dicts."""
    module = load_check_module(case_dir, module_name)
    if module is None:
        return None
    run_fn = getattr(module, "run_checks", None)
    if run_fn is None:
        return None
    try:
        details = run_fn(code)
        return [
            {
                "check_name": d.check_name,
                "passed": d.passed,
                "expected": d.expected,
                "actual": d.actual,
            }
            for d in details
        ]
    except Exception as exc:
        print(
            f"  WARNING: Check raised exception for "
            f"{case_dir.name}/{module_name}: {exc}",
            file=sys.stderr,
        )
        return None


def verify_run(
    run_dir: Path,
    case_map: dict[str, Path],
    category: str | None = None,
    verbose: bool = False,
) -> dict:
    """Verify all results in a benchmark run directory.

    ``case_map`` maps case_id -> case dir (built via :func:`build_case_map`).
    Returns summary dict with counts and issue lists.
    """
    details_dir = run_dir / "details"
    if not details_dir.is_dir():
        print(f"ERROR: No details/ directory in {run_dir}", file=sys.stderr)
        sys.exit(1)

    issues = {
        "reference_failures": [],  # Check script bugs (reference solution fails)
        "discrepancies": [],  # Stored vs re-run mismatch
        "false_negatives": [],  # LLM code failed but might be correct
        "false_positives": [],  # LLM code passed but reference also fails
        "l1_skip_cases": [],  # Cases where reference can't compile
    }
    stats = {"total": 0, "verified_ok": 0, "issues_found": 0, "l1_skipped": 0}

    json_files = sorted(details_dir.glob("*.json"))
    for json_file in json_files:
        case_id = json_file.stem
        if category and not case_id.startswith(category):
            continue

        case_dir = case_map.get(case_id)
        if case_dir is None or not case_dir.is_dir():
            if verbose:
                print(f"  SKIP {case_id}: case dir not found")
            continue

        stats["total"] += 1
        data = json.loads(json_file.read_text(encoding="utf-8"))
        generated_code = data.get("generated_code", "")
        stored_layers = data.get("layers", [])

        # Check l1_skip status
        meta_path = case_dir / "metadata.yaml"
        if meta_path.is_file():
            meta_content = meta_path.read_text(encoding="utf-8")
            if "l1_skip: true" in meta_content:
                stats["l1_skipped"] += 1
                # Extract reason from comment
                for line in meta_content.splitlines():
                    if line.strip().startswith("l1_skip:"):
                        reason = (
                            line.split("#", 1)[1].strip() if "#" in line else "unknown"
                        )
                        issues["l1_skip_cases"].append(
                            {
                                "case_id": case_id,
                                "reason": reason,
                            }
                        )
                        break

        # Load reference solution
        ref_file = case_dir / "reference" / "main.c"
        ref_code = ref_file.read_text(encoding="utf-8") if ref_file.is_file() else None

        case_has_issue = False

        for module_name, layer_idx in [("static", 0), ("behavior", 3), ("mutants", 4)]:
            # Find stored results for this layer
            stored_layer = None
            for sl in stored_layers:
                if sl.get("layer") == layer_idx:
                    stored_layer = sl
                    break

            if stored_layer is None:
                continue

            # Skip layers that were skipped due to earlier failure
            error_val = stored_layer.get("error") or ""
            if error_val.startswith("Skipped:"):
                continue

            stored_details = stored_layer.get("details", [])
            if not stored_details:
                continue

            # Re-run checks on generated code
            rerun = run_checks(case_dir, generated_code, module_name)
            if rerun is None:
                continue

            # Compare stored vs re-run
            stored_map = {d["check_name"]: d["passed"] for d in stored_details}
            rerun_map = {d["check_name"]: d["passed"] for d in rerun}

            for check_name in rerun_map:
                stored_pass = stored_map.get(check_name)
                rerun_pass = rerun_map[check_name]

                if stored_pass is not None and stored_pass != rerun_pass:
                    issue = {
                        "case_id": case_id,
                        "layer": layer_idx,
                        "module": module_name,
                        "check_name": check_name,
                        "stored": stored_pass,
                        "rerun": rerun_pass,
                    }
                    issues["discrepancies"].append(issue)
                    case_has_issue = True
                    print(
                        f"  DISCREPANCY {case_id} L{layer_idx}/{check_name}: "
                        f"stored={stored_pass} vs rerun={rerun_pass}"
                    )

            # Run reference solution through same checks
            if ref_code is not None:
                ref_results = run_checks(case_dir, ref_code, module_name)
                if ref_results is not None:
                    for rd in ref_results:
                        if not rd["passed"]:
                            issue = {
                                "case_id": case_id,
                                "layer": layer_idx,
                                "module": module_name,
                                "check_name": rd["check_name"],
                                "expected": rd["expected"],
                                "actual": rd["actual"],
                            }
                            issues["reference_failures"].append(issue)
                            case_has_issue = True
                            print(
                                f"  FALSE NEGATIVE {case_id} "
                                f"L{layer_idx}/{rd['check_name']}: "
                                f"reference solution FAILS — check script bug!"
                            )
                            if verbose:
                                print(f"    expected: {rd['expected']}")
                                print(f"    actual:   {rd['actual']}")

            # For failed LLM checks — check if LLM code actually has the pattern
            # (helps detect overly strict checks)
            if verbose:
                for rd in rerun or []:
                    if not rd["passed"]:
                        print(
                            f"  FAIL {case_id} L{layer_idx}/{rd['check_name']}: "
                            f"expected={rd['expected']} actual={rd['actual']}"
                        )

        if case_has_issue:
            stats["issues_found"] += 1
        else:
            stats["verified_ok"] += 1
            if verbose:
                print(f"  OK {case_id}")

    return {"stats": stats, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description="Verify benchmark results")
    parser.add_argument("run_dir", type=Path, help="Path to run directory")
    parser.add_argument(
        "--cases", type=Path, default=Path("cases"), help="Path to cases directory"
    )
    parser.add_argument(
        "--private-cases",
        type=Path,
        default=None,
        help="Path to private cases directory (held-out set), if the run "
        "included --include-private",
    )
    parser.add_argument(
        "--category",
        "-c",
        type=str,
        default=None,
        help="Filter by category prefix (e.g., 'dma')",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all check results, not just issues",
    )
    args = parser.parse_args()

    roots = [args.cases]
    if args.private_cases is not None:
        roots.append(args.private_cases)
    case_map = build_case_map(roots)

    print(f"Verifying results in: {args.run_dir}")
    print(f"Cases directories: {', '.join(str(r) for r in roots)}")
    print(f"Resolved {len(case_map)} case dirs")
    if args.category:
        print(f"Category filter: {args.category}")
    if not case_map:
        print(
            "ERROR: 0 case dirs resolved — check --cases/--private-cases paths",
            file=sys.stderr,
        )
        return 2
    print()

    result = verify_run(args.run_dir, case_map, args.category, args.verbose)

    stats = result["stats"]
    issues = result["issues"]

    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total cases verified: {stats['total']}")
    print(f"Verified OK: {stats['verified_ok']}")
    print(f"Issues found: {stats['issues_found']}")
    print()

    if issues["reference_failures"]:
        print(
            f"FALSE NEGATIVES (check script bugs): {len(issues['reference_failures'])}"
        )
        for i in issues["reference_failures"]:
            print(f"  - {i['case_id']} L{i['layer']}/{i['check_name']}")
            print(f"    expected: {i['expected']}")
            print(f"    actual:   {i['actual']}")
        print()

    if issues["discrepancies"]:
        print(f"DISCREPANCIES (stored vs re-run): {len(issues['discrepancies'])}")
        for i in issues["discrepancies"]:
            print(
                f"  - {i['case_id']} L{i['layer']}/{i['check_name']}: "
                f"stored={i['stored']} rerun={i['rerun']}"
            )
        print()

    if issues["l1_skip_cases"]:
        print(
            f"L1_SKIP CASES (reference can't compile): {len(issues['l1_skip_cases'])}"
        )
        for i in issues["l1_skip_cases"]:
            print(f"  - {i['case_id']}: {i['reason']}")
        print()
        covered = stats["total"] - stats["l1_skipped"]
        pct = covered / max(stats["total"], 1) * 100
        print(f"L1/L2 evaluation coverage: {covered}/{stats['total']} ({pct:.0f}%)")
        print()

    if stats["total"] == 0:
        print(
            "WARNING: 0 cases were actually verified — case dirs did not match "
            "any run detail. This is NOT a clean result; check the layout/paths.",
            file=sys.stderr,
        )
        return 2

    if not issues["reference_failures"] and not issues["discrepancies"]:
        print("All results verified — no false results detected.")

    return 1 if issues["reference_failures"] or issues["discrepancies"] else 0


if __name__ == "__main__":
    sys.exit(main())
