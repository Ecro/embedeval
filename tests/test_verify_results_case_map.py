"""Tests for scripts/verify_results.py case-dir resolution.

Regression guard for the bug where verify_results.py assumed a flat
cases/<id>/ layout and silently resolved 0 cases under the 2-level
SDK-bucket layout (cases/<sdk>/<id>/), reporting a false all-clear."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_module() -> Any:
    script = Path(__file__).resolve().parent.parent / "scripts" / "verify_results.py"
    spec = importlib.util.spec_from_file_location("verify_results", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["verify_results"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()


def _mk_case(root: Path, sdk: str, case_id: str) -> Path:
    d = root / sdk / case_id
    d.mkdir(parents=True)
    (d / "metadata.yaml").write_text(f"sdk: {sdk}\n", encoding="utf-8")
    return d


def test_build_case_map_resolves_2level_layout(tmp_path: Path):
    """The core regression: 2-level cases/<sdk>/<id>/ must resolve."""
    cases = tmp_path / "cases"
    _mk_case(cases, "zephyr", "gpio-basic-001")
    _mk_case(cases, "embedded-linux", "linux-driver-004")

    case_map = mod.build_case_map([cases])

    assert set(case_map) == {"gpio-basic-001", "linux-driver-004"}
    assert case_map["gpio-basic-001"].name == "gpio-basic-001"
    assert case_map["gpio-basic-001"].parent.name == "zephyr"


def test_build_case_map_merges_public_and_private(tmp_path: Path):
    pub = tmp_path / "cases"
    priv = tmp_path / "private"
    _mk_case(pub, "zephyr", "ble-001")
    _mk_case(priv, "zephyr", "ble-900")

    case_map = mod.build_case_map([pub, priv])

    assert set(case_map) == {"ble-001", "ble-900"}


def test_build_case_map_later_root_wins_on_collision(tmp_path: Path):
    """On a colliding id, the later root (private) shadows the earlier."""
    pub = tmp_path / "cases"
    priv = tmp_path / "private"
    _mk_case(pub, "embedded-linux", "yocto-009")
    _mk_case(priv, "embedded-linux", "yocto-009")

    case_map = mod.build_case_map([pub, priv])

    assert set(case_map) == {"yocto-009"}
    # Private (last root) wins.
    assert case_map["yocto-009"].is_relative_to(priv)


def test_build_case_map_empty_for_missing_root(tmp_path: Path):
    case_map = mod.build_case_map([tmp_path / "does-not-exist"])
    assert case_map == {}
