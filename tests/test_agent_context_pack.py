"""Tests for agent mode context_pack plumbing (F8 regression)."""

from pathlib import Path
from unittest.mock import patch

from embedeval.agent import evaluate_agent
from embedeval.models import LLMResponse, TokenUsage


def _stub_response() -> LLMResponse:
    return LLMResponse(
        model="mock",
        generated_code="int main(void) { return 0; }",
        token_usage=TokenUsage(input_tokens=1, output_tokens=1, total_tokens=2),
        cost_usd=0.0,
        duration_seconds=0.0,
    )


def test_evaluate_agent_forwards_context_pack(tmp_path: Path) -> None:
    """F8 regression: evaluate_agent must pass context_pack down to
    call_model on every turn. Otherwise --context-pack on the agent
    CLI would silently no-op."""
    case_dir = tmp_path / "fake-case-001"
    case_dir.mkdir()

    with patch("embedeval.agent.call_model") as mock_call:
        mock_call.return_value = _stub_response()
        with patch("embedeval.agent.evaluate") as mock_eval:
            # Make the case "pass" on first turn to keep the test simple
            from embedeval.models import (
                CaseCategory,
                EvalResult,
                LayerResult,
            )

            mock_eval.return_value = EvalResult(
                case_id="fake-case-001",
                category=CaseCategory.ISR_CONCURRENCY,
                model="mock",
                attempt=1,
                generated_code="int main(void) { return 0; }",
                layers=[
                    LayerResult(
                        layer=0,
                        name="static_analysis",
                        passed=True,
                        details=[],
                        duration_seconds=0.0,
                    )
                ],
                failed_at_layer=None,
                passed=True,
                total_score=1.0,
                duration_seconds=0.0,
                token_usage=TokenUsage(
                    input_tokens=1, output_tokens=1, total_tokens=2
                ),
                cost_usd=0.0,
            )

            evaluate_agent(
                case_dir=case_dir,
                model="mock",
                prompt="task body",
                max_turns=1,
                context_pack="MY_TEAM_RULE_X",
            )

    # Verify call_model was invoked with our context_pack
    mock_call.assert_called_once()
    kwargs = mock_call.call_args.kwargs
    assert kwargs.get("context_pack") == "MY_TEAM_RULE_X"


def test_evaluate_agent_without_context_pack_passes_none(tmp_path: Path) -> None:
    """Backward compat: omitting context_pack must pass None to call_model
    (not a silent default), so existing agent runs are unchanged."""
    case_dir = tmp_path / "fake-case-002"
    case_dir.mkdir()

    with patch("embedeval.agent.call_model") as mock_call:
        mock_call.return_value = _stub_response()
        with patch("embedeval.agent.evaluate") as mock_eval:
            from embedeval.models import (
                CaseCategory,
                EvalResult,
                LayerResult,
            )

            mock_eval.return_value = EvalResult(
                case_id="fake-case-002",
                category=CaseCategory.ISR_CONCURRENCY,
                model="mock",
                attempt=1,
                generated_code="int main(void) { return 0; }",
                layers=[
                    LayerResult(
                        layer=0,
                        name="static_analysis",
                        passed=True,
                        details=[],
                        duration_seconds=0.0,
                    )
                ],
                failed_at_layer=None,
                passed=True,
                total_score=1.0,
                duration_seconds=0.0,
                token_usage=TokenUsage(
                    input_tokens=1, output_tokens=1, total_tokens=2
                ),
                cost_usd=0.0,
            )

            evaluate_agent(
                case_dir=case_dir,
                model="mock",
                prompt="task body",
                max_turns=1,
            )

    mock_call.assert_called_once()
    kwargs = mock_call.call_args.kwargs
    assert kwargs.get("context_pack") is None
