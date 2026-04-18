#!/usr/bin/env python3
"""Mutation oracle gate for negatives.py files.

For each case with negatives.py:
  1. Read reference/main.c (or reference/*.c).
  2. Apply each NEGATIVE's mutation.
  3. Run L0 (static.py) + L3 (behavior.py) checks on mutated code.
  4. Assert each 'must_fail' check actually fails.

Exit code: 0 if all oracles pass; 1 if any case has a must_fail check
that didn't detect its seeded bug. Safe to run in CI.

Usage:
    uv run python scripts/verify_negatives_oracle.py
    uv run python scripts/verify_negatives_oracle.py --case dma-002
    uv run python scripts/verify_negatives_oracle.py --category dma
    uv run python scripts/verify_negatives_oracle.py --json report.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class OracleResult:
    case_id: str
    status: str  # "pass" | "fail" | "skip"
    negatives_attempted: int = 0
    missed: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


def _load_module(path: Path, alias: str) -> Any:
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_reference(case_dir: Path) -> str | None:
    ref_main = case_dir / "reference" / "main.c"
    if ref_main.is_file():
        return ref_main.read_text()
    # Fallback: any .c or .bb or .conf under reference/
    ref_dir = case_dir / "reference"
    if not ref_dir.is_dir():
        return None
    for ext in ("*.c", "*.bb", "*.conf", "*.dts", "*.overlay", "*.yaml"):
        matches = sorted(ref_dir.glob(ext))
        if matches:
            return matches[0].read_text()
    return None


def verify_case(case_dir: Path) -> OracleResult:
    case_id = case_dir.name
    checks_dir = case_dir / "checks"
    neg_path = checks_dir / "negatives.py"
    static_path = checks_dir / "static.py"
    behavior_path = checks_dir / "behavior.py"

    if not neg_path.is_file():
        return OracleResult(case_id=case_id, status="skip", error="no negatives.py")

    reference = _read_reference(case_dir)
    if reference is None:
        return OracleResult(
            case_id=case_id, status="skip", error="no reference file found"
        )

    try:
        neg_mod = _load_module(neg_path, f"neg_{case_id}")
        negatives: list[dict[str, Any]] = getattr(neg_mod, "NEGATIVES", [])
    except Exception as exc:
        return OracleResult(case_id=case_id, status="fail", error=f"load: {exc}")

    if not negatives:
        return OracleResult(
            case_id=case_id, status="skip", error="NEGATIVES list empty"
        )

    static_mod = (
        _load_module(static_path, f"st_{case_id}")
        if static_path.is_file()
        else None
    )
    behavior_mod = (
        _load_module(behavior_path, f"bh_{case_id}")
        if behavior_path.is_file()
        else None
    )

    result = OracleResult(case_id=case_id, status="pass", negatives_attempted=0)

    for neg in negatives:
        if "must_fail" not in neg:
            continue  # should_fail-only subtle negatives not gated here

        name = neg.get("name", "<unnamed>")
        try:
            mutated = neg["mutation"](reference)
        except Exception as exc:
            result.missed.append(
                {
                    "negative": name,
                    "reason": f"mutation raised: {exc}",
                    "must_fail": neg["must_fail"],
                }
            )
            result.status = "fail"
            continue

        if mutated == reference:
            result.missed.append(
                {
                    "negative": name,
                    "reason": "mutation did not change reference",
                    "must_fail": neg["must_fail"],
                }
            )
            result.status = "fail"
            continue

        # Collect all check details on mutated code
        details: list[Any] = []
        if static_mod and hasattr(static_mod, "run_checks"):
            details.extend(static_mod.run_checks(mutated))
        if behavior_mod and hasattr(behavior_mod, "run_checks"):
            details.extend(behavior_mod.run_checks(mutated))

        for check_name in neg["must_fail"]:
            matching = [d for d in details if d.check_name == check_name]
            if not matching:
                result.missed.append(
                    {
                        "negative": name,
                        "must_fail_check": check_name,
                        "reason": "check not found in static.py/behavior.py",
                    }
                )
                result.status = "fail"
                continue
            if any(d.passed for d in matching):
                result.missed.append(
                    {
                        "negative": name,
                        "must_fail_check": check_name,
                        "reason": "check PASSED on mutated code (should have failed)",
                    }
                )
                result.status = "fail"

        result.negatives_attempted += 1

    return result


def iter_cases(
    cases_root: Path,
    case_filter: str | None,
    category_filter: str | None,
) -> list[Path]:
    out: list[Path] = []
    for case_dir in sorted(cases_root.iterdir()):
        if not case_dir.is_dir():
            continue
        if case_filter and case_dir.name != case_filter:
            continue
        if category_filter and not case_dir.name.startswith(category_filter):
            continue
        out.append(case_dir)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="cases", help="cases root directory")
    parser.add_argument("--case", help="run a single case")
    parser.add_argument("--category", help="filter by category prefix")
    parser.add_argument("--json", help="write report as JSON to this path")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    cases_root = Path(args.cases).resolve()
    if not cases_root.is_dir():
        print(f"ERROR: cases dir not found: {cases_root}", file=sys.stderr)
        return 2

    results: list[OracleResult] = []
    for case_dir in iter_cases(cases_root, args.case, args.category):
        results.append(verify_case(case_dir))

    # Text report
    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    skipped = sum(1 for r in results if r.status == "skip")

    if not args.quiet:
        for r in results:
            if r.status == "fail":
                print(f"FAIL {r.case_id}")
                for m in r.missed:
                    print(f"  - {m}")
            elif r.status == "pass" and args.case:
                print(f"PASS {r.case_id} ({r.negatives_attempted} negatives)")

        print(f"\nTotal: {len(results)} | PASS={passed} FAIL={failed} SKIP={skipped}")

    if args.json:
        Path(args.json).write_text(
            json.dumps([asdict(r) for r in results], indent=2)
        )

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
