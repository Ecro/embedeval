# EmbedEval Leaderboard


## Model Comparison

| Model | pass@1 (full) | pass@1 (quality) | 95% CI | pass@5 | Passed | Quality | Total | Samples |
|-------|---------------|------------------|--------|--------|--------|---------|-------|---------|
| claude-code://haiku | 57.1% | 71.7% | [50.7%, 63.3%] | 57.1% | 133 | 167 | 233 | n=1 |
| claude-code://sonnet | 73.4% | 85.8% | [67.4%, 78.7%] | 73.4% | 171 | 200 | 233 | n=1 |

*pass@1 (full) = all layers must pass. pass@1 (quality) = L0+L3 only (code quality, ignoring build/runtime).*

## Tier Breakdown

| Tier | pass@1 | Passed | Total |
|------|--------|--------|-------|
| Sanity (not scored) | 50.0% | 2 | 4 |
| Core | 63.4% | 78 | 123 |
| Challenge | 50.0% | 53 | 106 |
| Sanity (not scored) | 75.0% | 3 | 4 |
| Core | 80.5% | 99 | 123 |
| Challenge | 65.1% | 69 | 106 |

## Reasoning Type Breakdown

| Reasoning Type | pass@1 | Cases | LLM Reliability |
|----------------|--------|-------|-----------------|
| L1 API Recall | 59.0% | 217 | Expert review required |
| L2 Rule Application | 65.9% | 132 | Expert review required |
| L3 Cross-Domain | 36.8% | 38 | Expert review required |
| L4 System Reasoning | 58.3% | 115 | Expert review required |
| L1 API Recall | 77.0% | 217 | Review recommended |
| L2 Rule Application | 78.8% | 132 | Review recommended |
| L3 Cross-Domain | 50.0% | 38 | Expert review required |
| L4 System Reasoning | 69.6% | 115 | Expert review required |

## Category Results

| Category | pass@1 | Passed | Total | Status |
|----------|--------|--------|-------|--------|
| adc | 50.0% | 1 | 2 | PARTIAL |
| ble | 45.5% | 5 | 11 | FAIL |
| boot | 100.0% | 10 | 10 | PASS |
| device-tree | 100.0% | 10 | 10 | PASS |
| dma | 7.7% | 1 | 13 | FAIL |
| gpio-basic | 83.3% | 5 | 6 | PASS |
| isr-concurrency | 38.5% | 5 | 13 | FAIL |
| kconfig | 60.0% | 6 | 10 | PARTIAL |
| linux-driver | 70.0% | 7 | 10 | PARTIAL |
| memory-opt | 33.3% | 4 | 12 | FAIL |
| networking | 75.0% | 9 | 12 | PARTIAL |
| ota | 58.3% | 7 | 12 | PARTIAL |
| power-mgmt | 66.7% | 8 | 12 | PARTIAL |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 70.0% | 7 | 10 | PARTIAL |
| sensor-driver | 66.7% | 8 | 12 | PARTIAL |
| spi-i2c | 64.3% | 9 | 14 | PARTIAL |
| storage | 30.8% | 4 | 13 | FAIL |
| threading | 33.3% | 5 | 15 | FAIL |
| timer | 50.0% | 6 | 12 | PARTIAL |
| uart | 66.7% | 2 | 3 | PARTIAL |
| watchdog | 60.0% | 6 | 10 | PARTIAL |
| yocto | 70.0% | 7 | 10 | PARTIAL |
| adc | 100.0% | 2 | 2 | PASS |
| ble | 81.8% | 9 | 11 | PASS |
| boot | 100.0% | 10 | 10 | PASS |
| device-tree | 100.0% | 10 | 10 | PASS |
| dma | 46.2% | 6 | 13 | FAIL |
| gpio-basic | 66.7% | 4 | 6 | PARTIAL |
| isr-concurrency | 46.2% | 6 | 13 | FAIL |
| kconfig | 80.0% | 8 | 10 | PASS |
| linux-driver | 70.0% | 7 | 10 | PARTIAL |
| memory-opt | 58.3% | 7 | 12 | PARTIAL |
| networking | 91.7% | 11 | 12 | PASS |
| ota | 75.0% | 9 | 12 | PARTIAL |
| power-mgmt | 91.7% | 11 | 12 | PASS |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 60.0% | 6 | 10 | PARTIAL |
| sensor-driver | 75.0% | 9 | 12 | PARTIAL |
| spi-i2c | 78.6% | 11 | 14 | PARTIAL |
| storage | 53.8% | 7 | 13 | PARTIAL |
| threading | 40.0% | 6 | 15 | FAIL |
| timer | 91.7% | 11 | 12 | PASS |
| uart | 66.7% | 2 | 3 | PARTIAL |
| watchdog | 80.0% | 8 | 10 | PASS |
| yocto | 100.0% | 10 | 10 | PASS |

## Layer Pass Rate Heatmap

| Model| L0 Static| L1 Build| L2 Runtime| L3 Heuristic| L4 Mutation| |
|-------|----------|----------|----------|----------|----------||
| claude-code://haiku| 82%| 88%| 93%| 85%| 100%| |
| claude-code://sonnet| 93%| 93%| 94%| 91%| 100%| |

## Failure Distribution

| Layer | Failures | % of Total |
|-------|----------|-----------|
| L0 Static | 0.2 | 30% |
| L1 Build | 0.2 | 24% |
| L2 Runtime | 0.1 | 16% |
| L3 Heuristic | 0.2 | 30% |
| L4 Mutation | 0.0 | 0% |

## Category Breakdown

| Category | Pass@1 | Cases |
|----------|--------|-------|
| adc | 50% | 2 |
| ble | 45% | 11 |
| boot | 100% | 10 |
| device-tree | 100% | 10 |
| dma | 8% | 13 |
| gpio-basic | 83% | 6 |
| isr-concurrency | 38% | 13 |
| kconfig | 60% | 10 |
| linux-driver | 70% | 10 |
| memory-opt | 33% | 12 |
| networking | 75% | 12 |
| ota | 58% | 12 |
| power-mgmt | 67% | 12 |
| pwm | 100% | 1 |
| security | 70% | 10 |
| sensor-driver | 67% | 12 |
| spi-i2c | 64% | 14 |
| storage | 31% | 13 |
| threading | 33% | 15 |
| timer | 50% | 12 |
| uart | 67% | 3 |
| watchdog | 60% | 10 |
| yocto | 70% | 10 |
| adc | 100% | 2 |
| ble | 82% | 11 |
| boot | 100% | 10 |
| device-tree | 100% | 10 |
| dma | 46% | 13 |
| gpio-basic | 67% | 6 |
| isr-concurrency | 46% | 13 |
| kconfig | 80% | 10 |
| linux-driver | 70% | 10 |
| memory-opt | 58% | 12 |
| networking | 92% | 12 |
| ota | 75% | 12 |
| power-mgmt | 92% | 12 |
| pwm | 100% | 1 |
| security | 60% | 10 |
| sensor-driver | 75% | 12 |
| spi-i2c | 79% | 14 |
| storage | 54% | 13 |
| threading | 40% | 15 |
| timer | 92% | 12 |
| uart | 67% | 3 |
| watchdog | 80% | 10 |
| yocto | 100% | 10 |

## Cross-Benchmark Comparison

| Model | HumanEval | SWE-bench | EmbedEval (full) | EmbedEval (quality) | Embed Gap |
|-------|-----------|-----------|------------------|---------------------|-----------|
| claude-code://haiku | 84.0% | 48.2% | 57.1% | 71.7% | -26.9%p |
| claude-code://sonnet | 93.7% | 72.2% | 73.4% | 85.8% | -20.3%p |

*Embed Gap = EmbedEval pass@1 - HumanEval. Negative = harder than general coding.*
