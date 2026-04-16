---
name: Model evaluation request
about: Request EmbedEval to be run against a new LLM
title: "[model] Evaluate <model-id>"
labels: ["evaluation", "model-coverage"]
assignees: []
---

## Model

<!-- Provider name + model id, e.g. anthropic/claude-3-5-sonnet, openai/gpt-4o, deepseek/deepseek-coder, qwen/qwen3-coder -->
- **Provider:**
- **Model ID:**
- **Context length:**
- **Cost (per 1M input tokens):**

## Why this model

<!-- 1-2 sentences. Is it production-relevant? Open weights? A new release? -->

## Access

How to invoke this model:

- [ ] LiteLLM-compatible (provide env var name)
- [ ] Ollama / local
- [ ] Other (please describe)

## Willing to contribute the run?

EmbedEval is community-driven. Each `n=3` run takes a few hours on the public 185-case set.

- [ ] I can run the n=3 baseline myself and submit results via PR
- [ ] I can fund API costs but need help running it
- [ ] Just suggesting — please consider

## Acceptance criteria

A model is added to the leaderboard when:
- [ ] n=3 reproducible run on the **public** 185-case set
- [ ] Results JSON committed under `results/runs/<date>_<model>/`
- [ ] LEADERBOARD.md regenerated via `scripts/aggregate_n_runs.py`
- [ ] Brief notes on platform-specific failures (if any)
