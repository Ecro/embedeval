"""Smoke test: verify that --context-pack content actually reaches claude -p.

D1 risk from PLAN-context-quality-mode.md: the `claude-code://` mode shells
out to `claude -p` with stdin. We need to confirm that prepending text via
_build_full_prompt() is observed by the model in its output.

Strategy: put a unique sentinel string + a behavior instruction inside the
context pack. If the response contains the sentinel that the bare prompt
would never produce, the context made it through.

Usage:
    uv run python scripts/smoke_test_context_pack.py [--model haiku]

Exits 0 on success, non-zero on failure. Costs ~$0.01 with haiku.
"""

from __future__ import annotations

import argparse
import sys

from embedeval.llm_client import call_model

SENTINEL = "EMBEDEVAL_CONTEXT_SMOKE_42"

CONTEXT_PACK = f"""\
You are reviewing code for an embedded firmware team.

PROJECT CONVENTION: Whenever you generate any C function, you MUST include
the literal comment `// {SENTINEL}` on the line immediately after the
opening brace. This is non-negotiable team policy enforced in code review.

Apply this convention to every code response in this session.
"""

BARE_PROMPT = (
    "Write a tiny C function `int add(int a, int b)` that returns a + b. "
    "Output only the function, no explanations."
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="haiku",
        help="Claude model name (haiku/sonnet/opus). Default: haiku (cheapest).",
    )
    args = parser.parse_args()
    model_id = f"claude-code://{args.model}"

    print(f"[1/2] Bare prompt (no context pack) → {model_id}")
    bare = call_model(model=model_id, prompt=BARE_PROMPT, timeout=120)
    bare_has_sentinel = SENTINEL in bare.generated_code
    print(
        f"      sentinel present in bare output: {bare_has_sentinel} "
        f"(should be False)"
    )
    print(f"      tokens: in={bare.token_usage.input_tokens} "
          f"out={bare.token_usage.output_tokens}")

    print(f"\n[2/2] With context pack → {model_id}")
    with_pack = call_model(
        model=model_id,
        prompt=BARE_PROMPT,
        context_pack=CONTEXT_PACK,
        timeout=120,
    )
    pack_has_sentinel = SENTINEL in with_pack.generated_code
    print(
        f"      sentinel present in pack output: {pack_has_sentinel} "
        f"(should be True)"
    )
    print(f"      tokens: in={with_pack.token_usage.input_tokens} "
          f"out={with_pack.token_usage.output_tokens}")
    print(
        f"      input token delta: "
        f"+{with_pack.token_usage.input_tokens - bare.token_usage.input_tokens} "
        f"(should be > {len(CONTEXT_PACK) // 8})"
    )

    print("\n--- Result ---")
    if bare_has_sentinel:
        print(
            "FAIL: sentinel appeared in BARE output — sentinel is not unique "
            "enough or the model guessed it. Pick a different sentinel."
        )
        return 2

    if not pack_has_sentinel:
        print("FAIL: context pack did NOT influence the model.")
        print("Possible causes:")
        print("  - claude -p stripped the prepended text")
        print("  - The instruction was too subtle for haiku")
        print("  - _build_full_prompt() is not being called")
        print("\nGenerated code from pack run (first 500 chars):")
        print(with_pack.generated_code[:500])
        return 1

    token_delta = with_pack.token_usage.input_tokens - bare.token_usage.input_tokens
    expected_min_delta = len(CONTEXT_PACK) // 8  # ~chars-per-token lower bound
    if token_delta < expected_min_delta:
        print(
            f"WARN: input token delta ({token_delta}) suspiciously small. "
            f"Pack may have been truncated. Continuing anyway."
        )

    print("PASS: context pack reached the model and influenced its output.")
    print(f"      sentinel '{SENTINEL}' found in pack-augmented response.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
