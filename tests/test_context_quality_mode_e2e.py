"""End-to-end tests for Context Quality Mode.

Drives the real CLI (`embedeval run` × 3 + `embedeval context-compare`)
with the mock model and a tiny subset of cases, then validates the
tracker files and the comparison JSON schema. Closes the last outstanding
gap in PLAN-context-quality-mode ("별도 e2e test 파일 미생성").

Why mock + 2 cases:
  - Mock is context-independent, so Lift/Gap will be ~0 — we are NOT
    validating that packs actually help, only that the plumbing flows
    (hash → tracker → compare → JSON) works end-to-end.
  - uart category has only 2 TCs, which keeps the test under a second.
  - No build dependency: EMBEDEVAL_ENABLE_BUILD is not set, so L1/L2
    skip cleanly on CI.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from embedeval.cli import app
from embedeval.test_tracker import TRACKER_FILENAME, load_tracker

cli = CliRunner()

CASES_DIR = Path(__file__).parent.parent / "cases"
UART_CASE_COUNT = 2  # uart-001, uart-002 — keep assertion with test intent


@pytest.fixture()
def team_pack(tmp_path: Path) -> Path:
    """Minimal team-pack content — short, distinct from expert.md, stable
    bytes so hash comparisons are reproducible."""
    p = tmp_path / "team-pack.md"
    p.write_text(
        "# Team context (e2e test)\n\n"
        "- Always check return values of init functions.\n"
        "- Prefer static allocation.\n",
        encoding="utf-8",
    )
    return p


@patch("embedeval.evaluator._build_env_available", return_value=False)
class TestContextQualityModeE2E:
    """Full pipeline: 3x run → 3 trackers → context-compare → JSON schema."""

    def _invoke_run(
        self,
        out: Path,
        pack: str | None,
    ) -> None:
        args = [
            "run",
            "--cases",
            str(CASES_DIR),
            "--model",
            "mock",
            "--category",
            "uart",
            "--output-dir",
            str(out),
        ]
        if pack is not None:
            args.extend(["--context-pack", pack])
        result = cli.invoke(app, args)
        assert result.exit_code == 0, (
            f"run failed (pack={pack!r}):\n{result.output}\n{result.exception}"
        )

    def _run_all_three(
        self,
        tmp_path: Path,
        team_pack_path: Path,
    ) -> tuple[Path, Path, Path]:
        bare = tmp_path / "bare"
        team = tmp_path / "team"
        expert = tmp_path / "expert"
        self._invoke_run(bare, pack=None)
        self._invoke_run(team, pack=str(team_pack_path))
        self._invoke_run(expert, pack="expert")
        return bare, team, expert

    def test_three_runs_write_distinct_tracker_hashes(
        self, _mock_docker: object, tmp_path: Path, team_pack: Path
    ) -> None:
        """Each of bare/team/expert produces a tracker whose
        `context_pack_hash` identifies the run uniquely (None for bare,
        two distinct 16-char hashes for team/expert)."""
        bare, team, expert = self._run_all_three(tmp_path, team_pack)

        bare_t = load_tracker(bare)
        team_t = load_tracker(team)
        expert_t = load_tracker(expert)

        assert (bare / TRACKER_FILENAME).is_file()
        assert (team / TRACKER_FILENAME).is_file()
        assert (expert / TRACKER_FILENAME).is_file()

        assert bare_t.context_pack_hash is None
        assert team_t.context_pack_hash is not None
        assert expert_t.context_pack_hash is not None
        assert team_t.context_pack_hash != expert_t.context_pack_hash
        assert len(team_t.context_pack_hash) == 16  # 16-char SHA256 prefix

    def test_three_runs_cover_same_case_set(
        self, _mock_docker: object, tmp_path: Path, team_pack: Path
    ) -> None:
        """All three trackers must cover the same case ids for the
        comparison to be meaningful (micro-average denominator stable).
        CategoryComparison's case-count-mismatch warning should NOT fire."""
        bare, team, expert = self._run_all_three(tmp_path, team_pack)
        bare_ids = set(load_tracker(bare).results["mock"])
        team_ids = set(load_tracker(team).results["mock"])
        expert_ids = set(load_tracker(expert).results["mock"])
        assert bare_ids == team_ids == expert_ids
        assert len(bare_ids) == UART_CASE_COUNT

    def test_context_compare_cli_produces_json_with_full_schema(
        self,
        _mock_docker: object,
        tmp_path: Path,
        team_pack: Path,
    ) -> None:
        """The full JSON payload from `context-compare --output-json`
        must carry every field downstream consumers rely on:
        per_category (with lift/gap/effect_counts), overall, per_case,
        RunSummary with max_attempts + token fields."""
        bare, team, expert = self._run_all_three(tmp_path, team_pack)
        out_json = tmp_path / "compare.json"
        result = cli.invoke(
            app,
            [
                "context-compare",
                "--bare",
                str(bare),
                "--team",
                str(team),
                "--expert",
                str(expert),
                "--output-json",
                str(out_json),
            ],
        )
        assert result.exit_code == 0, result.output
        assert out_json.is_file()

        payload = json.loads(out_json.read_text(encoding="utf-8"))

        # Top-level shape
        assert set(payload.keys()) >= {
            "model",
            "runs",
            "per_category",
            "overall",
            "per_case",
        }
        assert payload["model"] == "mock"

        # runs: 3 entries with label bare/team/expert, all new fields present
        labels = [r["label"] for r in payload["runs"]]
        assert labels == ["bare", "team", "expert"]
        for r in payload["runs"]:
            assert {
                "label",
                "pack_hash",
                "model",
                "n_cases",
                "pass_rate",
                "max_attempts",
                "input_tokens",
                "output_tokens",
                "cost_usd",
            } <= set(r.keys())
            assert r["n_cases"] == UART_CASE_COUNT
            assert r["max_attempts"] == 1  # default single-attempt run

        # per_category: one entry (uart), with effect_counts keys
        assert len(payload["per_category"]) == 1
        uart_cat = payload["per_category"][0]
        assert uart_cat["category"] == "uart"
        assert "effect_counts" in uart_cat
        assert set(uart_cat["effect_counts"].keys()) == {
            "helpful",
            "harmful",
            "no-effect-fail",
            "no-effect-pass",
        }
        assert "lift" in uart_cat and "gap" in uart_cat

        # per_case: one entry per case in the union across trackers
        case_ids = {pc["case_id"] for pc in payload["per_case"]}
        assert len(case_ids) == UART_CASE_COUNT
        for pc in payload["per_case"]:
            assert set(pc.keys()) >= {
                "case_id",
                "category",
                "bare_passed",
                "team_passed",
                "expert_passed",
                "bare_to_expert_effect",
                "bare_to_team_effect",
            }
            # Default opt-out: bare_to_team_effect is None even when
            # team tracker is present
            assert pc["bare_to_team_effect"] is None

    def test_context_compare_rejects_cross_pack_mixing(
        self,
        _mock_docker: object,
        tmp_path: Path,
        team_pack: Path,
    ) -> None:
        """Running into the same output_dir with a different pack must
        raise ContextPackMismatchError (tracker D3 enforcement)."""
        shared = tmp_path / "shared"
        self._invoke_run(shared, pack=None)

        # Second run into the same dir with a different pack → CLI exits
        # non-zero with a helpful error.
        result = cli.invoke(
            app,
            [
                "run",
                "--cases",
                str(CASES_DIR),
                "--model",
                "mock",
                "--category",
                "uart",
                "--output-dir",
                str(shared),
                "--context-pack",
                str(team_pack),
            ],
        )
        assert result.exit_code != 0
        assert "Context pack mismatch" in result.output or "mismatch" in result.output

    def test_include_team_effect_opt_in_roundtrip(
        self,
        _mock_docker: object,
        tmp_path: Path,
        team_pack: Path,
    ) -> None:
        """With --include-team-effect, every per_case entry gets a
        non-None bare_to_team_effect when team tracker has the case."""
        bare, team, expert = self._run_all_three(tmp_path, team_pack)
        out_json = tmp_path / "compare.json"
        result = cli.invoke(
            app,
            [
                "context-compare",
                "--bare",
                str(bare),
                "--team",
                str(team),
                "--expert",
                str(expert),
                "--include-team-effect",
                "--output-json",
                str(out_json),
            ],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(out_json.read_text(encoding="utf-8"))
        for pc in payload["per_case"]:
            assert pc["bare_to_team_effect"] is not None, (
                f"include_team_effect set but case {pc['case_id']} "
                f"has bare_to_team_effect=None"
            )
