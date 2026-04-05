# Benchmark Report: claude-code://haiku

**Date:** 2026-04-04 12:48 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 6 |
| Passed | 4 |
| Failed | 2 |
| pass@1 | 66.7% |

## Failed Cases (2)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `memory-opt-007` | memory-opt | static_analysis | null_returned_on_exhaustion |
| `timer-005` | timer | compile_gate | west_build_docker |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `null_returned_on_exhaustion` | 1 | memory-opt-007 |
| `west_build_docker` | 1 | timer-005 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 1 | timer-005 |
| LLM format failure (prose) | 1 | memory-opt-007 |

*Adjusted pass@1 (excluding format failures): 80.0% (4/5)*


## TC Improvement Suggestions

