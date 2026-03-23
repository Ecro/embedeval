"""Tests for EmbedEval LLM client."""

from unittest.mock import MagicMock, patch

import pytest

from embedeval.llm_client import MOCK_C_CODE, call_model


class TestMockMode:
    """Tests for mock mode responses."""

    def test_mock_returns_c_code(self) -> None:
        response = call_model(model="mock", prompt="generate code")
        assert MOCK_C_CODE in response.generated_code

    def test_mock_returns_zero_cost(self) -> None:
        response = call_model(model="mock", prompt="test")
        assert response.cost_usd == 0.0

    def test_mock_model_name(self) -> None:
        response = call_model(model="mock", prompt="test")
        assert response.model == "mock"

    def test_mock_token_usage(self) -> None:
        response = call_model(model="mock", prompt="test")
        assert response.token_usage.input_tokens == 100
        assert response.token_usage.output_tokens == 50
        assert response.token_usage.total_tokens == 150

    def test_mock_duration_positive(self) -> None:
        response = call_model(model="mock", prompt="test")
        assert response.duration_seconds >= 0.0


class TestRetryLogic:
    """Tests for retry behavior on real model calls."""

    @patch("embedeval.llm_client.litellm")
    def test_retries_on_failure(self, mock_litellm: MagicMock) -> None:
        mock_litellm.completion.side_effect = [
            ConnectionError("fail1"),
            ConnectionError("fail2"),
            self._make_mock_response(),
        ]
        mock_litellm.completion_cost.return_value = 0.001

        response = call_model(
            model="gpt-4",
            prompt="test",
            max_retries=3,
            rate_limit_delay=0.0,
        )
        assert response.model == "gpt-4"
        assert mock_litellm.completion.call_count == 3

    @patch("embedeval.llm_client.litellm")
    def test_raises_after_max_retries(self, mock_litellm: MagicMock) -> None:
        mock_litellm.completion.side_effect = ConnectionError("always fails")

        with pytest.raises(RuntimeError, match="All 3 retries exhausted"):
            call_model(
                model="gpt-4",
                prompt="test",
                max_retries=3,
                rate_limit_delay=0.0,
            )

    @patch("embedeval.llm_client.litellm")
    def test_successful_first_attempt(self, mock_litellm: MagicMock) -> None:
        mock_litellm.completion.return_value = self._make_mock_response()
        mock_litellm.completion_cost.return_value = 0.002

        response = call_model(
            model="gpt-4",
            prompt="test",
            rate_limit_delay=0.0,
        )
        assert response.generated_code == "int main() { return 0; }"
        assert mock_litellm.completion.call_count == 1

    @staticmethod
    def _make_mock_response() -> MagicMock:
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = "int main() { return 0; }"
        response.usage.prompt_tokens = 50
        response.usage.completion_tokens = 20
        return response


class TestContextFiles:
    """Tests for context file loading."""

    def test_context_files_included(self, tmp_path: "pytest.TempPathFactory") -> None:
        ctx_file = tmp_path / "test.c"  # type: ignore[operator]
        ctx_file.write_text("#include <stdio.h>")

        response = call_model(
            model="mock",
            prompt="test",
            context_files=[str(ctx_file)],
        )
        assert response.generated_code == MOCK_C_CODE

    def test_missing_context_file_handled(self) -> None:
        response = call_model(
            model="mock",
            prompt="test",
            context_files=["/nonexistent/file.c"],
        )
        assert response.model == "mock"
