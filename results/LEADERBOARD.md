# EmbedEval Leaderboard


## Model Comparison

| Model | pass@1 (full) | pass@1 (quality) | 95% CI | pass@5 | Passed | Quality | Total | Samples |
|-------|---------------|------------------|--------|--------|--------|---------|-------|---------|
| claude-code://sonnet | 81.7% | 87.2% | [73.4%, 87.8%] | 81.7% | 89 | 95 | 109 | n=1 |

*pass@1 (full) = all layers must pass. pass@1 (quality) = L0+L3 only (code quality, ignoring build/runtime).*

## Tier Breakdown

| Tier | pass@1 | Passed | Total |
|------|--------|--------|-------|
| Sanity (not scored) | 0.0% | 0 | 1 |
| Core | 88.5% | 54 | 61 |
| Challenge | 74.5% | 35 | 47 |

## Reasoning Type Breakdown

| Reasoning Type | pass@1 | Cases | LLM Reliability |
|----------------|--------|-------|-----------------|
| L1 API Recall | 85.1% | 101 | Review recommended |
| L2 Rule Application | 80.4% | 56 | Review recommended |
| L3 Cross-Domain | 61.9% | 21 | Expert review required |
| L4 System Reasoning | 81.7% | 60 | Review recommended |

## Category Results

| Category | pass@1 | Passed | Total | Status |
|----------|--------|--------|-------|--------|
| adc | 100.0% | 2 | 2 | PASS |
| ble | 100.0% | 8 | 8 | PASS |
| boot | 0.0% | 0 | 1 | FAIL |
| device-tree | 100.0% | 1 | 1 | PASS |
| dma | 50.0% | 2 | 4 | PARTIAL |
| gpio-basic | 75.0% | 3 | 4 | PARTIAL |
| isr-concurrency | 50.0% | 2 | 4 | PARTIAL |
| kconfig | 0.0% | 0 | 1 | FAIL |
| linux-driver | 100.0% | 2 | 2 | PASS |
| memory-opt | 55.6% | 5 | 9 | PARTIAL |
| networking | 100.0% | 8 | 8 | PASS |
| ota | 87.5% | 7 | 8 | PASS |
| power-mgmt | 100.0% | 8 | 8 | PASS |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 33.3% | 1 | 3 | FAIL |
| sensor-driver | 100.0% | 8 | 8 | PASS |
| spi-i2c | 87.5% | 7 | 8 | PASS |
| storage | 80.0% | 4 | 5 | PASS |
| threading | 40.0% | 2 | 5 | FAIL |
| timer | 100.0% | 6 | 6 | PASS |
| uart | 100.0% | 2 | 2 | PASS |
| watchdog | 88.9% | 8 | 9 | PASS |
| yocto | 100.0% | 2 | 2 | PASS |

## Layer Pass Rate Heatmap

| Model| L0 Static| L1 Build| L2 Runtime| L3 Heuristic| L4 Mutation| |
|-------|----------|----------|----------|----------|----------||
| claude-code://sonnet| 94%| 98%| 96%| 92%| 99%| |

## Failure Distribution

| Layer | Failures | % of Total |
|-------|----------|-----------|
| L0 Static | 0.1 | 26% |
| L1 Build | 0.0 | 9% |
| L2 Runtime | 0.0 | 19% |
| L3 Heuristic | 0.1 | 40% |
| L4 Mutation | 0.0 | 5% |

## Category Breakdown

| Category | Pass@1 | Cases |
|----------|--------|-------|
| adc | 100% | 2 |
| ble | 100% | 8 |
| boot | 0% | 1 |
| device-tree | 100% | 1 |
| dma | 50% | 4 |
| gpio-basic | 75% | 4 |
| isr-concurrency | 50% | 4 |
| kconfig | 0% | 1 |
| linux-driver | 100% | 2 |
| memory-opt | 56% | 9 |
| networking | 100% | 8 |
| ota | 88% | 8 |
| power-mgmt | 100% | 8 |
| pwm | 100% | 1 |
| security | 33% | 3 |
| sensor-driver | 100% | 8 |
| spi-i2c | 88% | 8 |
| storage | 80% | 5 |
| threading | 40% | 5 |
| timer | 100% | 6 |
| uart | 100% | 2 |
| watchdog | 89% | 9 |
| yocto | 100% | 2 |

## Cross-Benchmark Comparison

| Model | HumanEval | SWE-bench | EmbedEval (full) | EmbedEval (quality) | Embed Gap |
|-------|-----------|-----------|------------------|---------------------|-----------|
| claude-code://sonnet | 93.7% | 72.2% | 81.7% | 87.2% | -12.0%p |

*Embed Gap = EmbedEval pass@1 - HumanEval. Negative = harder than general coding.*
