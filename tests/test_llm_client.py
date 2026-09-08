"""Tests for EmbedEval LLM client."""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from embedeval.llm_client import (
    MOCK_C_CODE,
    _call_claude_code,
    _extract_code,
    _looks_like_prose,
    _parse_claude_code_json,
    call_model,
)


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


class TestClaudeCodeJsonParsing:
    """Tests for `claude -p --output-format json` payload parsing.

    Regression guard for the 2026-09-08 opus5 run, where the CLI's single
    result object was iterated as if it were a list of events — every case
    died with `'str' object has no attribute 'get'` and scored FAIL@L0.
    """

    @staticmethod
    def _result_event(**overrides: object) -> dict:
        event = {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "result": "```c\nint main(void) { return 0; }\n```",
            "total_cost_usd": 0.14,
            "usage": {
                "input_tokens": 2,
                "cache_read_input_tokens": 1000,
                "cache_creation_input_tokens": 22042,
                "output_tokens": 476,
            },
        }
        event.update(overrides)
        return event

    def test_single_object_form(self) -> None:
        parsed = _parse_claude_code_json(json.dumps(self._result_event()))
        assert "int main(void)" in parsed.text
        assert parsed.output_tokens == 476
        assert parsed.input_tokens == 2 + 1000 + 22042
        assert parsed.cost_usd == 0.14
        assert parsed.is_error is False

    def test_legacy_event_list_form(self) -> None:
        events = [{"type": "system", "subtype": "init"}, self._result_event()]
        parsed = _parse_claude_code_json(json.dumps(events))
        assert "int main(void)" in parsed.text
        assert parsed.output_tokens == 476

    def test_error_result_flagged(self) -> None:
        payload = self._result_event(
            is_error=True,
            subtype="error_during_execution",
            result="API Error: overloaded",
        )
        parsed = _parse_claude_code_json(json.dumps(payload))
        assert parsed.is_error is True

    def test_missing_usage_defaults_to_zero(self) -> None:
        payload = self._result_event()
        del payload["usage"]
        del payload["total_cost_usd"]
        parsed = _parse_claude_code_json(json.dumps(payload))
        assert parsed.input_tokens == 0
        assert parsed.output_tokens == 0
        assert parsed.cost_usd == 0.0

    def test_malformed_json_falls_back_to_raw_stdout(self) -> None:
        parsed = _parse_claude_code_json("not json at all")
        assert parsed.text == "not json at all"
        assert parsed.is_error is False

    def test_no_result_entry_falls_back_to_raw_stdout(self) -> None:
        raw = json.dumps([{"type": "system", "subtype": "init"}])
        parsed = _parse_claude_code_json(raw)
        assert parsed.text == raw


class TestClaudeCodeCall:
    """Tests for the `claude -p` subprocess wrapper."""

    @staticmethod
    def _completed(stdout: str, returncode: int = 0) -> MagicMock:
        proc = MagicMock()
        proc.returncode = returncode
        proc.stdout = stdout
        proc.stderr = ""
        return proc

    @staticmethod
    def _ok_stdout() -> str:
        return json.dumps(
            {
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "result": "```c\nint main(void) { return 0; }\n```",
                "total_cost_usd": 0.2,
                "usage": {"input_tokens": 10, "output_tokens": 20},
            }
        )

    @patch("embedeval.llm_client.subprocess.run")
    def test_happy_path_object_output(self, mock_run: MagicMock) -> None:
        mock_run.return_value = self._completed(self._ok_stdout())

        response = _call_claude_code(
            "claude-code://claude-opus-5", "prompt", timeout=30.0
        )
        assert response.generated_code == "int main(void) { return 0; }"
        assert response.token_usage.total_tokens == 30
        assert response.cost_usd == 0.2
        assert mock_run.call_count == 1
        assert "--model" in mock_run.call_args.args[0]
        assert "claude-opus-5" in mock_run.call_args.args[0]

    @patch("embedeval.llm_client.subprocess.run")
    def test_retries_then_succeeds_on_nonzero_exit(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = [
            self._completed("", returncode=1),
            self._completed(self._ok_stdout()),
        ]

        response = _call_claude_code("claude-code://sonnet", "prompt", timeout=30.0)
        assert "int main(void)" in response.generated_code
        assert mock_run.call_count == 2

    @patch("embedeval.llm_client.subprocess.run")
    def test_raises_after_repeated_error_results(self, mock_run: MagicMock) -> None:
        err = json.dumps(
            {
                "type": "result",
                "subtype": "error_during_execution",
                "is_error": True,
                "result": "API Error: overloaded",
            }
        )
        mock_run.return_value = self._completed(err)

        with pytest.raises(RuntimeError, match="failed after 2 attempts"):
            _call_claude_code("claude-code://sonnet", "prompt", timeout=30.0)
        assert mock_run.call_count == 2

    @patch("embedeval.llm_client.subprocess.run")
    def test_raises_after_repeated_timeouts(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=30.0)

        with pytest.raises(RuntimeError, match="timed out"):
            _call_claude_code("claude-code://sonnet", "prompt", timeout=30.0)
        assert mock_run.call_count == 2


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
        # Mock now echoes the prompt prefix into a /* PROMPT_PREFIX: */ block
        # so callers can verify what the model actually saw. The stock C body
        # (MOCK_C_CODE) is still appended verbatim.
        assert MOCK_C_CODE in response.generated_code
        assert "stdio.h" in response.generated_code

    def test_missing_context_file_handled(self) -> None:
        response = call_model(
            model="mock",
            prompt="test",
            context_files=["/nonexistent/file.c"],
        )
        assert response.model == "mock"


class TestExtractCode:
    """Tests for markdown code block extraction.

    Regression guard for bug where joining all fenced blocks concatenated
    prose/shell/directory-tree content into main.c, causing compile errors
    in memory-opt-012, threading-013, isr-concurrency-007, etc.
    """

    def test_single_c_tagged_block(self) -> None:
        text = "Here is the code:\n```c\nint main(void) { return 0; }\n```"
        assert _extract_code(text) == "int main(void) { return 0; }"

    def test_single_untagged_block(self) -> None:
        text = "```\nint x = 1;\n```"
        assert _extract_code(text) == "int x = 1;"

    def test_c_block_plus_prose_block_keeps_only_c(self) -> None:
        text = (
            "```c\n"
            "int main(void) { return 0; }\n"
            "```\n"
            "Then run:\n"
            "```\n"
            "west build -b native_sim\n"
            "./build/zephyr/zephyr.exe\n"
            "```"
        )
        result = _extract_code(text)
        assert "int main(void)" in result
        assert "west build" not in result
        assert "zephyr.exe" not in result

    def test_two_untagged_blocks_takes_first_only(self) -> None:
        text = (
            "```\n"
            "int main(void) { return 0; }\n"
            "```\n"
            "Project layout:\n"
            "```\n"
            "crc_test/\n"
            "├── src/main.c\n"
            "```"
        )
        result = _extract_code(text)
        assert "int main(void)" in result
        assert "crc_test" not in result
        assert "├──" not in result

    def test_cpp_language_tag_recognized(self) -> None:
        text = "```cpp\nclass Foo {};\n```\n```bash\necho hi\n```"
        result = _extract_code(text)
        assert "class Foo" in result
        assert "echo hi" not in result

    def test_no_code_blocks_returns_text(self) -> None:
        text = "Just plain text with no fences"
        assert _extract_code(text) == "Just plain text with no fences"

    def test_multiple_c_blocks_joined(self) -> None:
        text = (
            "```c\n#include <header.h>\n```\n"
            "And:\n"
            "```c\nint main(void) { return 0; }\n```"
        )
        result = _extract_code(text)
        assert "#include <header.h>" in result
        assert "int main(void)" in result

    def test_regression_memory_opt_012_pattern(self) -> None:
        """Exact failure pattern from memory-opt-012 Haiku run (2026-04-04)."""
        text = (
            "```c\n"
            "#include <zephyr/kernel.h>\n"
            "int main(void) { return 0; }\n"
            "```\n"
            "\n"
            "```\n"
            "crc_test/\n"
            "├── src/main.c          (above code)\n"
            "├── CMakeLists.txt      (default Zephyr template)\n"
            "└── prj.conf           (can be minimal/empty for native_sim)\n"
            "\n"
            "cd crc_test\n"
            "west build -b native_sim\n"
            "./build/zephyr/zephyr.exe\n"
            "```"
        )
        result = _extract_code(text)
        assert "#include <zephyr/kernel.h>" in result
        assert "int main(void)" in result
        assert "crc_test/" not in result
        assert "west build" not in result
        assert "├──" not in result


class TestProseDetection:
    """Tests for _looks_like_prose heuristic."""

    def test_empty_text_is_prose(self) -> None:
        assert _looks_like_prose("") is True
        assert _looks_like_prose("   \n\t ") is True

    def test_include_is_code(self) -> None:
        assert _looks_like_prose("#include <zephyr.h>\nint x;") is False

    def test_main_function_is_code(self) -> None:
        assert _looks_like_prose("int main(void) { return 0; }") is False

    def test_plain_english_is_prose(self) -> None:
        text = "I cannot write code for this task. Please provide more details."
        assert _looks_like_prose(text) is True

    def test_markdown_explanation_is_prose(self) -> None:
        text = "# Solution\n\nThe approach is to use HMAC. First, you should..."
        assert _looks_like_prose(text) is True


class TestProseRetry:
    """Integration tests: call_model retries once on prose response."""

    @patch("embedeval.llm_client.litellm")
    def test_retries_once_on_prose(self, mock_litellm: MagicMock) -> None:
        prose_resp = MagicMock()
        prose_resp.choices = [MagicMock()]
        prose_resp.choices[0].message.content = "I cannot help with that request."
        prose_resp.usage.prompt_tokens = 10
        prose_resp.usage.completion_tokens = 5

        code_resp = MagicMock()
        code_resp.choices = [MagicMock()]
        code_resp.choices[0].message.content = "```c\nint main(void) { return 0; }\n```"
        code_resp.usage.prompt_tokens = 12
        code_resp.usage.completion_tokens = 8

        mock_litellm.completion.side_effect = [prose_resp, code_resp]
        mock_litellm.completion_cost.return_value = 0.001

        response = call_model(
            model="gpt-4",
            prompt="write hello world in C",
            rate_limit_delay=0.0,
        )
        assert "int main(void)" in response.generated_code
        assert mock_litellm.completion.call_count == 2
        second_prompt = mock_litellm.completion.call_args_list[1].kwargs["messages"][0][
            "content"
        ]
        assert "code only" in second_prompt.lower() or "```c" in second_prompt

    @patch("embedeval.llm_client.litellm")
    def test_no_retry_when_first_is_code(self, mock_litellm: MagicMock) -> None:
        code_resp = MagicMock()
        code_resp.choices = [MagicMock()]
        code_resp.choices[
            0
        ].message.content = (
            "```c\n#include <stdio.h>\nint main(void) { return 0; }\n```"
        )
        code_resp.usage.prompt_tokens = 10
        code_resp.usage.completion_tokens = 5
        mock_litellm.completion.return_value = code_resp
        mock_litellm.completion_cost.return_value = 0.001

        response = call_model(model="gpt-4", prompt="test", rate_limit_delay=0.0)
        assert "#include" in response.generated_code
        assert mock_litellm.completion.call_count == 1

    @patch("embedeval.llm_client.litellm")
    def test_prose_retry_still_prose_returned_as_is(
        self, mock_litellm: MagicMock
    ) -> None:
        prose_resp = MagicMock()
        prose_resp.choices = [MagicMock()]
        prose_resp.choices[0].message.content = "Sorry, I can't help."
        prose_resp.usage.prompt_tokens = 5
        prose_resp.usage.completion_tokens = 3

        mock_litellm.completion.side_effect = [prose_resp, prose_resp]
        mock_litellm.completion_cost.return_value = 0.0

        response = call_model(model="gpt-4", prompt="test", rate_limit_delay=0.0)
        # Single retry, then whatever came back is returned (caller sees prose)
        assert mock_litellm.completion.call_count == 2
        assert "Sorry" in response.generated_code
