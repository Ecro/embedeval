"""EmbedEval LLM client interface."""

import json
import logging
import re
import subprocess
import time
from pathlib import Path

import litellm
from litellm.exceptions import (
    RateLimitError,
    ServiceUnavailableError,
)
from litellm.exceptions import (
    Timeout as LitellmTimeout,
)

from embedeval.models import LLMResponse, TokenUsage

logger = logging.getLogger(__name__)

MOCK_C_CODE = """\
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

void main(void) {
    printk("Hello from EmbedEval mock\\n");
    while (1) {
        k_sleep(K_SECONDS(1));
    }
}
"""

CLAUDE_CODE_PREFIX = "claude-code://"


def call_model(
    model: str,
    prompt: str,
    context_files: list[str] | None = None,
    timeout: float = 300.0,
    max_retries: int = 3,
    rate_limit_delay: float = 1.0,
) -> LLMResponse:
    """Call an LLM model and return generated code.

    Supports three modes:
    - "mock": Returns a mock response for testing.
    - "claude-code://MODEL": Uses `claude -p` CLI with subscription (no API key).
      e.g. "claude-code://sonnet", "claude-code://opus", "claude-code://haiku"
    - Any other string: Uses litellm (requires API keys).
    """
    if model == "mock":
        return _mock_response()

    context = _build_context(context_files or [])
    full_prompt = f"{context}\n{prompt}" if context else prompt

    if model.startswith(CLAUDE_CODE_PREFIX):
        return _call_claude_code(model, full_prompt, timeout)

    return _call_litellm(model, full_prompt, timeout, max_retries, rate_limit_delay)


def _call_claude_code(
    model: str,
    prompt: str,
    timeout: float,
    max_retries: int = 2,
) -> LLMResponse:
    """Call Claude via `claude -p` CLI (uses subscription, no API key)."""
    claude_model = model.removeprefix(CLAUDE_CODE_PREFIX)

    cmd = ["claude", "-p", "--output-format", "json"]
    if claude_model:
        cmd.extend(["--model", claude_model])

    for attempt in range(1, max_retries + 1):
        logger.info(
            "Claude Code call: model=%s (attempt %d/%d)",
            claude_model or "default",
            attempt,
            max_retries,
        )
        start = time.monotonic()

        try:
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            break  # success — exit retry loop
        except subprocess.TimeoutExpired as exc:
            if attempt < max_retries:
                logger.warning("claude -p timed out (attempt %d), retrying...", attempt)
                continue
            raise RuntimeError(
                f"claude -p timed out after {timeout}s ({max_retries} attempts)"
            ) from exc

    elapsed = time.monotonic() - start

    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (exit {result.returncode}): {result.stderr}"
        )

    # Parse JSON output — find the result entry
    text_content = ""
    input_tokens = 0
    output_tokens = 0
    cost_usd = 0.0

    try:
        events = json.loads(result.stdout)
        for event in events:
            if event.get("type") == "result":
                text_content = event.get("result", "")
                cost_usd = event.get("total_cost_usd", 0.0)
                usage = event.get("usage", {})
                input_tokens = usage.get("input_tokens", 0) + usage.get(
                    "cache_read_input_tokens", 0
                )
                output_tokens = usage.get("output_tokens", 0)
                break
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        logger.warning("Failed to parse claude -p JSON output: %s", exc)
        # Fall back to raw stdout
        text_content = result.stdout

    return LLMResponse(
        model=model,
        generated_code=_extract_code(text_content),
        token_usage=TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        ),
        cost_usd=cost_usd,
        duration_seconds=elapsed,
    )


def _call_litellm(
    model: str,
    prompt: str,
    timeout: float,
    max_retries: int,
    rate_limit_delay: float,
) -> LLMResponse:
    """Call LLM via litellm (requires API keys)."""
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                "LLM call attempt %d/%d to model %s",
                attempt,
                max_retries,
                model,
            )
            start = time.monotonic()
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )
            elapsed = time.monotonic() - start

            content: str = _extract_code(response.choices[0].message.content or "")
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = input_tokens + output_tokens

            cost = litellm.completion_cost(completion_response=response)

            return LLMResponse(
                model=model,
                generated_code=content,
                token_usage=TokenUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                ),
                cost_usd=float(cost),
                duration_seconds=elapsed,
            )
        except (KeyboardInterrupt, SystemExit):
            raise
        except (
            RateLimitError,
            ServiceUnavailableError,
            LitellmTimeout,
            ConnectionError,
        ) as exc:
            last_error = exc
            logger.warning(
                "LLM call attempt %d failed (retryable): %s",
                attempt,
                exc,
            )
            if attempt < max_retries:
                time.sleep(rate_limit_delay)
        except Exception as exc:
            logger.error("LLM call failed (non-retryable): %s", exc)
            raise RuntimeError(f"Non-retryable error for model {model}: {exc}") from exc

    msg = f"All {max_retries} retries exhausted for model {model}"
    raise RuntimeError(msg) from last_error


def _mock_response() -> LLMResponse:
    """Return a mock LLM response for testing."""
    return LLMResponse(
        model="mock",
        generated_code=MOCK_C_CODE,
        token_usage=TokenUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        ),
        cost_usd=0.0,
        duration_seconds=0.01,
    )


def _extract_code(text: str) -> str:
    """Extract code from LLM response, stripping markdown code blocks.

    LLMs typically wrap code in ```lang ... ``` blocks. This extracts
    the code content, or returns the original text if no blocks found.
    """
    # Match ```<optional-lang>\n...\n```
    blocks = re.findall(r"```\w*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return "\n".join(blocks).strip()
    return text.strip()


def _build_context(context_files: list[str]) -> str:
    """Build context string from file paths."""
    parts: list[str] = []
    for file_path in context_files:
        path = Path(file_path)
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            parts.append(f"--- {path.name} ---\n{content}")
        else:
            logger.warning("Context file not found: %s", file_path)
    return "\n".join(parts)
