#!/usr/bin/env python3
"""Verify that reference solutions compile for their target build_board.

Detects structurally broken test cases where the reference solution itself
cannot pass L1 (compile gate). Such cases are unfair — no LLM can pass them.

Usage:
    uv run python scripts/verify_references_build.py
    uv run python scripts/verify_references_build.py --category sensor-driver
    uv run python scripts/verify_references_build.py --dry-run   # just list, don't build
    uv run python scripts/verify_references_build.py --verbose

Requires: EMBEDEVAL_ENABLE_BUILD=docker (Docker must be running)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def get_build_board(case_dir: Path) -> str:
    """Read build_board from metadata.yaml, default to native_sim."""
    metadata_path = case_dir / "metadata.yaml"
    if metadata_path.is_file():
        for line in metadata_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("build_board:"):
                board = line.split(":", 1)[1].strip()
                if board:
                    return board
    return "native_sim"


def get_docker_image() -> str:
    return os.environ.get("EMBEDEVAL_DOCKER_IMAGE", "embedeval-zephyr:latest")


def is_esp_idf_case(case_dir: Path) -> bool:
    metadata_path = case_dir / "metadata.yaml"
    if metadata_path.is_file():
        content = metadata_path.read_text(encoding="utf-8")
        if "platform: esp_idf" in content:
            return True
    return (case_dir / "sdkconfig.defaults").is_file()


def is_stm32_case(case_dir: Path) -> bool:
    metadata_path = case_dir / "metadata.yaml"
    if metadata_path.is_file():
        content = metadata_path.read_text(encoding="utf-8")
        if "platform: stm32" in content:
            return True
    return False


def is_compilable(case_dir: Path) -> bool:
    """Check if this case has a CMakeLists.txt (Zephyr compilable)."""
    return (case_dir / "CMakeLists.txt").is_file()


def find_reference_code(case_dir: Path) -> str | None:
    """Find and read reference solution code."""
    # Check reference/main.c first, then reference.c
    for path in [
        case_dir / "reference" / "main.c",
        case_dir / "reference.c",
        case_dir / "main.c",  # some cases use this
    ]:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return None


def prepare_build_dir(case_dir: Path, code: str) -> Path:
    """Prepare a temporary build directory (mirrors evaluator._prepare_build_dir)."""
    tmpdir = Path(tempfile.mkdtemp(prefix="embedeval_refbuild_"))

    for name in ("CMakeLists.txt", "prj.conf"):
        src = case_dir / name
        if src.is_file():
            shutil.copy2(src, tmpdir / name)

    for pattern in ("*.overlay", "*.conf"):
        for f in case_dir.glob(pattern):
            if f.name not in ("prj.conf",):
                shutil.copy2(f, tmpdir / f.name)
    boards_dir = case_dir / "boards"
    if boards_dir.is_dir():
        shutil.copytree(boards_dir, tmpdir / "boards")

    src_dir = tmpdir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "main.c").write_text(code, encoding="utf-8")

    return tmpdir


def build_reference_docker(
    case_dir: Path,
    code: str,
    board: str,
    timeout: float = 120.0,
) -> dict:
    """Build reference solution in Docker. Returns result dict."""
    tmpdir = prepare_build_dir(case_dir, code)
    try:
        start = time.monotonic()
        cmd = [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "",
            "-v",
            f"{tmpdir}:/workspace",
            "-w",
            "/workspace",
            get_docker_image(),
            "west",
            "build",
            "-b",
            board,
            "/workspace",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - start

        error_lines = ""
        if result.returncode != 0:
            # Extract error lines
            output = (result.stdout or "") + "\n" + (result.stderr or "")
            errors = [
                line
                for line in output.splitlines()
                if "error:" in line.lower() and "note:" not in line.lower()
            ]
            if errors:
                error_lines = "\n".join(errors[:10])
            else:
                error_lines = output[-500:] if len(output) > 500 else output

        return {
            "passed": result.returncode == 0,
            "exit_code": result.returncode,
            "duration": round(elapsed, 1),
            "error": error_lines if result.returncode != 0 else None,
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "exit_code": -1,
            "duration": timeout,
            "error": f"Build timed out after {timeout}s",
        }
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Verify reference solutions compile for their target board"
    )
    parser.add_argument(
        "--cases",
        default="cases/",
        help="Path to cases directory (default: cases/)",
    )
    parser.add_argument(
        "--category",
        "-c",
        help="Only check specific category (e.g., sensor-driver)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List cases to check without building",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Build timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save results to JSON file",
    )
    args = parser.parse_args()

    cases_dir = Path(args.cases)
    if not cases_dir.is_dir():
        print(f"Error: cases directory not found: {cases_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect compilable cases with reference solutions
    cases_to_check = []
    for case_dir in sorted(cases_dir.iterdir()):
        if not case_dir.is_dir():
            continue

        case_id = case_dir.name

        # Filter by category if specified
        if args.category:
            cats = [c.strip() for c in args.category.split(",")]
            if not any(case_id.startswith(c + "-") or case_id == c for c in cats):
                continue

        # Skip non-Zephyr cases
        if is_esp_idf_case(case_dir) or is_stm32_case(case_dir):
            continue

        # Skip non-compilable cases
        if not is_compilable(case_dir):
            continue

        # Find reference code
        ref_code = find_reference_code(case_dir)
        if ref_code is None:
            continue

        board = get_build_board(case_dir)
        cases_to_check.append(
            {
                "case_id": case_id,
                "case_dir": case_dir,
                "board": board,
                "ref_code": ref_code,
            }
        )

    print(f"Found {len(cases_to_check)} compilable cases with reference solutions")
    print()

    # Group by board
    by_board: dict[str, list] = {}
    for c in cases_to_check:
        by_board.setdefault(c["board"], []).append(c)
    for board, cases in sorted(by_board.items()):
        print(f"  {board}: {len(cases)} cases")
    print()

    if args.dry_run:
        print("=== DRY RUN — cases to check ===")
        for c in cases_to_check:
            print(f"  {c['case_id']:30s} board={c['board']}")
        return

    # Check Docker
    build_mode = os.environ.get("EMBEDEVAL_ENABLE_BUILD", "")
    if build_mode != "docker":
        print(
            "Error: EMBEDEVAL_ENABLE_BUILD=docker required. Set it before running.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Build each reference
    results = []
    passed_count = 0
    failed_count = 0

    for i, c in enumerate(cases_to_check, 1):
        case_id = c["case_id"]
        board = c["board"]
        print(
            f"[{i}/{len(cases_to_check)}] {case_id} (board={board})...",
            end=" ",
            flush=True,
        )

        result = build_reference_docker(
            c["case_dir"],
            c["ref_code"],
            board,
            args.timeout,
        )
        result["case_id"] = case_id
        result["board"] = board
        results.append(result)

        if result["passed"]:
            passed_count += 1
            print(f"OK ({result['duration']}s)")
        else:
            failed_count += 1
            print(f"FAIL (exit={result['exit_code']}, {result['duration']}s)")
            if args.verbose and result.get("error"):
                for line in result["error"].splitlines()[:5]:
                    print(f"    {line}")

    # Summary
    total = len(results)
    print()
    print("=" * 60)
    print("REFERENCE BUILD VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total compilable cases:   {total}")
    print(f"Reference builds OK:      {passed_count}")
    print(f"Reference builds FAILED:  {failed_count}")
    print()

    if failed_count > 0:
        print("FAILED REFERENCES (= structurally broken test cases):")
        print()
        # Group by board
        fails_by_board: dict[str, list] = {}
        for r in results:
            if not r["passed"]:
                fails_by_board.setdefault(r["board"], []).append(r)

        for board, fails in sorted(fails_by_board.items()):
            print(f"  Board: {board} ({len(fails)} failures)")
            for r in fails:
                print(f"    {r['case_id']}")
                if r.get("error"):
                    first_line = r["error"].splitlines()[0][:100]
                    print(f"      → {first_line}")
            print()

        print("ACTION REQUIRED:")
        print("  These cases need DT overlays or l1_skip markers.")
        print("  No LLM can pass L1 for these cases as-is.")
    else:
        print("All reference solutions compile successfully.")

    # Save results
    if args.output:
        output_data = {
            "total": total,
            "passed": passed_count,
            "failed": failed_count,
            "results": [
                {k: v for k, v in r.items() if k != "ref_code"} for r in results
            ],
        }
        Path(args.output).write_text(
            json.dumps(output_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
