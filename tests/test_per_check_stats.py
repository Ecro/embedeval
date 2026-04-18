"""Tests for per-check statistics aggregation (P3 of PLAN-hiloop-transpile-readiness).

Ensures summary.json contains the authoritative per-check pass/fail signal
for downstream consumers (dashboards, Hiloop transpile evidence injection).
"""

from embedeval.models import (
    CaseCategory,
    CheckDetail,
    EvalResult,
    LayerResult,
    TokenUsage,
)
from embedeval.scorer import _calculate_per_check_stats, score


def _detail(name: str, passed: bool, check_type: str = "exact_match") -> CheckDetail:
    return CheckDetail(
        check_name=name,
        passed=passed,
        expected="e",
        actual="a",
        check_type=check_type,
    )


def _result(
    case_id: str,
    model: str,
    details: list[CheckDetail],
    category: CaseCategory | None = None,
    passed: bool = True,
) -> EvalResult:
    layer = LayerResult(
        layer=0,
        name="static_analysis",
        passed=passed,
        details=details,
        error=None,
        duration_seconds=0.1,
    )
    return EvalResult(
        case_id=case_id,
        category=category,
        model=model,
        attempt=1,
        generated_code="int main(){}",
        layers=[layer],
        passed=passed,
        duration_seconds=0.1,
        token_usage=TokenUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        cost_usd=0.0,
    )


class TestPerCheckStatsAggregation:
    def test_single_check_single_result(self) -> None:
        results = [_result("tc-1", "m1", [_detail("volatile_flag", True)])]
        stats = _calculate_per_check_stats(results)
        assert len(stats) == 1
        assert stats[0].check_name == "volatile_flag"
        assert stats[0].total_runs == 1
        assert stats[0].fail_count == 0
        assert stats[0].pass_rate == 1.0
        assert stats[0].failing_tc_ids == []

    def test_one_failing_tc_among_three(self) -> None:
        results = [
            _result("tc-1", "m1", [_detail("check_a", True)]),
            _result("tc-2", "m1", [_detail("check_a", True)]),
            _result("tc-3", "m1", [_detail("check_a", False)]),
        ]
        stats = _calculate_per_check_stats(results)
        assert len(stats) == 1
        s = stats[0]
        assert s.check_name == "check_a"
        assert s.total_runs == 3
        assert s.fail_count == 1
        assert s.pass_rate == 2 / 3
        assert s.failing_tc_ids == ["tc-3"]

    def test_failing_tc_ids_are_deduped(self) -> None:
        """Same TC running multiple times but failing same check → one entry."""
        results = [
            _result("tc-1", "m1", [_detail("check_x", False)]),
            _result("tc-1", "m1", [_detail("check_x", False)]),  # re-run
            _result("tc-2", "m1", [_detail("check_x", True)]),
        ]
        stats = _calculate_per_check_stats(results)
        s = next(x for x in stats if x.check_name == "check_x")
        assert s.fail_count == 2
        assert s.total_runs == 3
        assert s.failing_tc_ids == ["tc-1"]  # deduped

    def test_same_check_in_multiple_categories_split(self) -> None:
        """Check X in ISR and DMA categories must produce two entries."""
        results = [
            _result(
                "isr-1",
                "m1",
                [_detail("uses_atomic", True)],
                category=CaseCategory.ISR_CONCURRENCY,
            ),
            _result(
                "dma-1",
                "m1",
                [_detail("uses_atomic", False)],
                category=CaseCategory.DMA,
            ),
        ]
        stats = _calculate_per_check_stats(results)
        cats = {s.category for s in stats if s.check_name == "uses_atomic"}
        assert cats == {"isr-concurrency", "dma"}

    def test_l4_mutation_checks_excluded(self) -> None:
        """L4 mutation checks measure benchmark quality, not LLM behavior."""
        results = [
            _result(
                "tc-1",
                "m1",
                [
                    _detail("real_check", True),
                    _detail("mutation_missing_barrier", False, check_type="mutation"),
                ],
            )
        ]
        stats = _calculate_per_check_stats(results)
        names = {s.check_name for s in stats}
        assert "real_check" in names
        assert "mutation_missing_barrier" not in names

    def test_multiple_models_yield_separate_stats(self) -> None:
        """_calculate_per_check_stats is called per-model, but verify via score()."""
        results = [
            _result("tc-1", "haiku", [_detail("check_z", False)]),
            _result("tc-1", "sonnet", [_detail("check_z", True)]),
        ]
        report = score(results)
        haiku = next(m for m in report.models if m.model == "haiku")
        sonnet = next(m for m in report.models if m.model == "sonnet")
        haiku_z = next(s for s in haiku.per_check_stats if s.check_name == "check_z")
        sonnet_z = next(s for s in sonnet.per_check_stats if s.check_name == "check_z")
        assert haiku_z.fail_count == 1
        assert sonnet_z.fail_count == 0


class TestSummaryIntegration:
    def test_per_check_stats_present_in_summary(self) -> None:
        """End-to-end: score() output serializes per_check_stats in ModelScore."""
        results = [
            _result(
                "tc-1",
                "m1",
                [_detail("a", True), _detail("b", False)],
                category=CaseCategory.GPIO_BASIC,
            ),
        ]
        report = score(results)
        ms = report.models[0]
        assert len(ms.per_check_stats) == 2
        names = sorted(s.check_name for s in ms.per_check_stats)
        assert names == ["a", "b"]

    def test_per_check_stats_json_roundtrip(self) -> None:
        """model_dump_json must include per_check_stats (not silently drop)."""
        import json

        results = [_result("tc-1", "m1", [_detail("foo", False)])]
        report = score(results)
        payload = json.loads(report.model_dump_json())
        model_entry = payload["models"][0]
        assert "per_check_stats" in model_entry
        assert len(model_entry["per_check_stats"]) == 1
        assert model_entry["per_check_stats"][0]["check_name"] == "foo"
        assert model_entry["per_check_stats"][0]["fail_count"] == 1

    def test_empty_results_yields_empty_stats(self) -> None:
        stats = _calculate_per_check_stats([])
        assert stats == []
