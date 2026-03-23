"""EmbedEval LLM client interface."""

import logging
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


def call_model(
    model: str,
    prompt: str,
    context_files: list[str] | None = None,
    timeout: float = 120.0,
    max_retries: int = 3,
    rate_limit_delay: float = 1.0,
) -> LLMResponse:
    """Call an LLM model and return generated code.

    Args:
        model: Model identifier (e.g., "gpt-4", "mock" for testing).
        prompt: The prompt to send to the model.
        context_files: Optional list of file paths to include as context.
        timeout: Timeout in seconds for the API call.
        max_retries: Maximum number of retry attempts.
        rate_limit_delay: Delay in seconds between retries for rate limiting.

    Returns:
        LLMResponse with generated code, token usage, and cost.

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    if model == "mock":
        return _mock_response()

    context = _build_context(context_files or [])
    full_prompt = f"{context}\n{prompt}" if context else prompt

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
                messages=[{"role": "user", "content": full_prompt}],
                timeout=timeout,
            )
            elapsed = time.monotonic() - start

            content: str = response.choices[0].message.content or ""
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
