#!/usr/bin/env python3
"""Audit static.py / behavior.py files for unscoped substring matches.

P2 of PLAN-hiloop-transpile-readiness: many existing checks use bare
`"needle" in generated_code` which also matches inside comments and
string literals. This script parses every case's check files via AST
and flags those patterns.

Usage:
    uv run python scripts/audit_check_scope.py
    uv run python scripts/audit_check_scope.py --category isr-concurrency
    uv run python scripts/audit_check_scope.py --json audit.json
    uv run python scripts/audit_check_scope.py --strict   # exit 1 if findings

Output: one line per flagged finding with file:lineno + the suspicious
substring and suggested replacement.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    needle: str
    source: str  # raw code snippet
    suggestion: str


class _UnscopedMatchFinder(ast.NodeVisitor):
    """Finds `<str_literal> in <name>` expressions where <name> looks like raw code."""

    _RAW_CODE_NAMES = frozenset({"generated_code", "code"})

    def __init__(self, filename: str, source_lines: list[str]) -> None:
        self.filename = filename
        self.source_lines = source_lines
        self.findings: list[Finding] = []

    def visit_Compare(self, node: ast.Compare) -> None:  # noqa: N802
        # Pattern: Compare with a single In op and a Constant(str) left-side
        if (
            len(node.ops) == 1
            and isinstance(node.ops[0], ast.In)
            and isinstance(node.left, ast.Constant)
            and isinstance(node.left.value, str)
            and len(node.comparators) == 1
        ):
            right = node.comparators[0]
            target_name = self._name_of(right)
            if target_name in self._RAW_CODE_NAMES:
                self._record(node, node.left.value, target_name)
        self.generic_visit(node)

    @staticmethod
    def _name_of(expr: ast.expr) -> str | None:
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, ast.Attribute):
            return expr.attr
        return None

    def _record(self, node: ast.AST, needle: str, target: str) -> None:
        lineno = getattr(node, "lineno", 0)
        src = self.source_lines[lineno - 1].strip() if lineno else ""
        suggestion = f'scoped_contains({target}, {needle!r})'
        self.findings.append(
            Finding(
                file=self.filename,
                line=lineno,
                needle=needle,
                source=src,
                suggestion=suggestion,
            )
        )


def audit_file(path: Path) -> list[Finding]:
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    finder = _UnscopedMatchFinder(str(path), source.splitlines())
    finder.visit(tree)
    return finder.findings


def iter_check_files(cases_root: Path, category: str | None) -> list[Path]:
    files: list[Path] = []
    for case_dir in sorted(cases_root.iterdir()):
        if not case_dir.is_dir():
            continue
        if category and not case_dir.name.startswith(category):
            continue
        for name in ("static.py", "behavior.py"):
            p = case_dir / "checks" / name
            if p.is_file():
                files.append(p)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="cases", help="cases root directory")
    parser.add_argument("--category", help="filter to one category prefix (e.g. 'dma')")
    parser.add_argument("--json", help="write findings as JSON to this path")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any findings")
    args = parser.parse_args()

    cases_root = Path(args.cases).resolve()
    if not cases_root.is_dir():
        print(f"ERROR: cases dir not found: {cases_root}", file=sys.stderr)
        return 2

    all_findings: list[Finding] = []
    for f in iter_check_files(cases_root, args.category):
        try:
            all_findings.extend(audit_file(f))
        except SyntaxError as exc:
            print(f"WARN: could not parse {f}: {exc}", file=sys.stderr)

    if args.json:
        Path(args.json).write_text(
            json.dumps([asdict(f) for f in all_findings], indent=2)
        )

    # Human-readable report
    by_file: dict[str, list[Finding]] = {}
    for f in all_findings:
        by_file.setdefault(f.file, []).append(f)

    for fname in sorted(by_file.keys()):
        print(f"\n{fname}")
        for finding in by_file[fname]:
            print(f"  line {finding.line}: {finding.needle!r}")
            print(f"    src:  {finding.source}")
            print(f"    hint: {finding.suggestion}")

    total = len(all_findings)
    file_count = len(by_file)
    print(f"\n{'=' * 60}")
    print(f"Total unscoped substring checks: {total} across {file_count} files")

    if args.strict and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
