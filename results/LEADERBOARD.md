# EmbedEval Leaderboard


## Model Comparison

| Model | pass@1 (full) | pass@1 (quality) | 95% CI | pass@5 | Passed | Quality | Total | Samples |
|-------|---------------|------------------|--------|--------|--------|---------|-------|---------|
| claude-code://sonnet | 54.1% | 78.7% | [41.7%, 66.0%] | 54.1% | 33 | 48 | 61 | n=1 |

*pass@1 (full) = all layers must pass. pass@1 (quality) = L0+L3 only (code quality, ignoring build/runtime).*

## Tier Breakdown

| Tier | pass@1 | Passed | Total |
|------|--------|--------|-------|
| Sanity (not scored) | 100.0% | 1 | 1 |
| Core | 58.1% | 18 | 31 |
| Challenge | 48.3% | 14 | 29 |

## Reasoning Type Breakdown

| Reasoning Type | pass@1 | Cases | LLM Reliability |
|----------------|--------|-------|-----------------|
| L1 API Recall | 57.1% | 56 | Expert review required |
| L2 Rule Application | 62.5% | 32 | Expert review required |
| L3 Cross-Domain | 33.3% | 9 | Expert review required |
| L4 System Reasoning | 43.8% | 32 | Expert review required |

## Category Results

| Category | pass@1 | Passed | Total | Status |
|----------|--------|--------|-------|--------|
| ble | 33.3% | 1 | 3 | FAIL |
| boot | 100.0% | 3 | 3 | PASS |
| device-tree | 100.0% | 2 | 2 | PASS |
| dma | 50.0% | 2 | 4 | PARTIAL |
| gpio-basic | 0.0% | 0 | 1 | FAIL |
| isr-concurrency | 40.0% | 2 | 5 | FAIL |
| kconfig | 50.0% | 1 | 2 | PARTIAL |
| linux-driver | 50.0% | 1 | 2 | PARTIAL |
| memory-opt | 100.0% | 2 | 2 | PASS |
| networking | 50.0% | 1 | 2 | PARTIAL |
| ota | 50.0% | 2 | 4 | PARTIAL |
| power-mgmt | 75.0% | 3 | 4 | PARTIAL |
| security | 66.7% | 4 | 6 | PARTIAL |
| sensor-driver | 25.0% | 1 | 4 | FAIL |
| spi-i2c | 50.0% | 1 | 2 | PARTIAL |
| storage | 50.0% | 2 | 4 | PARTIAL |
| threading | 25.0% | 1 | 4 | FAIL |
| timer | 66.7% | 2 | 3 | PARTIAL |
| uart | 0.0% | 0 | 1 | FAIL |
| watchdog | 0.0% | 0 | 1 | FAIL |
| yocto | 100.0% | 2 | 2 | PASS |

## Layer Pass Rate Heatmap

| Model| L0 Static| L1 Build| L2 Runtime| L3 Heuristic| L4 Mutation| |
|-------|----------|----------|----------|----------|----------||
| claude-code://sonnet| 85%| 77%| 92%| 89%| 100%| |

## Failure Distribution

| Layer | Failures | % of Total |
|-------|----------|-----------|
| L0 Static | 0.1 | 26% |
| L1 Build | 0.2 | 41% |
| L2 Runtime | 0.1 | 13% |
| L3 Heuristic | 0.1 | 19% |
| L4 Mutation | 0.0 | 0% |

## Category Breakdown

| Category | Pass@1 | Cases |
|----------|--------|-------|
| ble | 33% | 3 |
| boot | 100% | 3 |
| device-tree | 100% | 2 |
| dma | 50% | 4 |
| gpio-basic | 0% | 1 |
| isr-concurrency | 40% | 5 |
| kconfig | 50% | 2 |
| linux-driver | 50% | 2 |
| memory-opt | 100% | 2 |
| networking | 50% | 2 |
| ota | 50% | 4 |
| power-mgmt | 75% | 4 |
| security | 67% | 6 |
| sensor-driver | 25% | 4 |
| spi-i2c | 50% | 2 |
| storage | 50% | 4 |
| threading | 25% | 4 |
| timer | 67% | 3 |
| uart | 0% | 1 |
| watchdog | 0% | 1 |
| yocto | 100% | 2 |

## Cross-Benchmark Comparison

| Model | HumanEval | SWE-bench | EmbedEval (full) | EmbedEval (quality) | Embed Gap |
|-------|-----------|-----------|------------------|---------------------|-----------|
| claude-code://sonnet | 93.7% | 72.2% | 54.1% | 78.7% | -39.6%p |

*Embed Gap = EmbedEval pass@1 - HumanEval. Negative = harder than general coding.*
