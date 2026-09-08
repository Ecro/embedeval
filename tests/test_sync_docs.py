"""Tests for scripts/sync_docs.py — specifically the guard that stops a
missing private-cases repo from silently rewriting published case counts."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest


def _load_module() -> Any:
    """Load the doc sync script as a module (scripts/ isn't on sys.path)."""
    script = Path(__file__).resolve().parent.parent / "scripts" / "sync_docs.py"
    spec = importlib.util.spec_from_file_location("sync_docs", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sync_docs"] = mod
    spec.loader.exec_module(mod)
    return mod


sync_docs = _load_module()


class TestPrivateCasesGuard:
    """The mandated pre-commit sync must not downgrade counts by accident.

    Prior incident (2026-09-08): running sync_docs.py on a machine without
    ../embedeval-private rewrote METHODOLOGY.md to "Total cases 219" and
    "Private held-out 0 cases (0%)".
    """

    def test_missing_private_repo_aborts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sync_docs, "PRIVATE_CASES_DIR", tmp_path / "absent")
        monkeypatch.setattr(sys, "argv", ["sync_docs.py"])

        with pytest.raises(SystemExit) as exc:
            sync_docs.main()
        assert exc.value.code == 1

    def test_missing_private_repo_error_names_the_path(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        absent = tmp_path / "absent"
        monkeypatch.setattr(sync_docs, "PRIVATE_CASES_DIR", absent)
        monkeypatch.setattr(sys, "argv", ["sync_docs.py"])

        with pytest.raises(SystemExit):
            sync_docs.main()
        assert str(absent) in capsys.readouterr().err

    def test_opt_in_flag_proceeds(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sync_docs, "PRIVATE_CASES_DIR", tmp_path / "absent")
        monkeypatch.setattr(sys, "argv", ["sync_docs.py", "--allow-missing-private"])
        # Counting tests shells out to pytest; the guard is what's under test.
        monkeypatch.setattr(sync_docs, "count_tests", lambda: 0)
        # Redirect the doc targets so the test never touches the real files.
        monkeypatch.setattr(sync_docs, "METHODOLOGY", tmp_path / "METHODOLOGY.md")
        monkeypatch.setattr(sync_docs, "README", tmp_path / "README.md")
        (tmp_path / "METHODOLOGY.md").write_text("# Methodology\n", encoding="utf-8")
        (tmp_path / "README.md").write_text("# README\n", encoding="utf-8")

        sync_docs.main()  # must not raise

    def test_present_private_repo_proceeds(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        private = tmp_path / "cases"
        private.mkdir()
        monkeypatch.setattr(sync_docs, "PRIVATE_CASES_DIR", private)
        monkeypatch.setattr(sys, "argv", ["sync_docs.py"])
        monkeypatch.setattr(sync_docs, "count_tests", lambda: 0)
        monkeypatch.setattr(sync_docs, "METHODOLOGY", tmp_path / "METHODOLOGY.md")
        monkeypatch.setattr(sync_docs, "README", tmp_path / "README.md")
        (tmp_path / "METHODOLOGY.md").write_text("# Methodology\n", encoding="utf-8")
        (tmp_path / "README.md").write_text("# README\n", encoding="utf-8")

        sync_docs.main()  # must not raise
