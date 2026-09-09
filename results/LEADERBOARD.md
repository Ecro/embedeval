# EmbedEval Leaderboard

<!-- SCHEMA_VERSION: 1 -->


## Model Comparison

| Model | pass@1 (full) | pass@1 (quality) | 95% CI | pass@5 | Passed | Quality | Total | Samples |
|-------|---------------|------------------|--------|--------|--------|---------|-------|---------|
| claude-code://claude-opus-5 | 70.0% | 83.5% | [64.3%, 75.2%] | 70.0% | 187 | 223 | 267 | n=1 |
| claude-code://claude-sonnet-5 | 67.3% | 79.5% | [61.4%, 72.7%] | 67.3% | 177 | 209 | 263 | n=1 |
| claude-code://haiku | 57.1% | 71.7% | [50.7%, 63.3%] | 57.1% | 133 | 167 | 233 | n=1 |
| claude-code://sonnet | 67.4% | 82.8% | [61.1%, 73.1%] | 67.4% | 157 | 193 | 233 | n=1 |

*pass@1 (full) = all layers must pass. pass@1 (quality) = L0+L3 only (code quality, ignoring build/runtime).*

## Tier Breakdown

| Tier | pass@1 | Passed | Total |
|------|--------|--------|-------|
| Sanity (not scored) | 75.0% | 3 | 4 |
| Core | 71.9% | 97 | 135 |
| Challenge | 68.0% | 87 | 128 |
| Sanity (not scored) | 75.0% | 3 | 4 |
| Core | 69.2% | 92 | 133 |
| Challenge | 65.1% | 82 | 126 |
| Sanity (not scored) | 50.0% | 2 | 4 |
| Core | 63.1% | 77 | 122 |
| Challenge | 50.5% | 54 | 107 |
| Sanity (not scored) | 75.0% | 3 | 4 |
| Core | 71.3% | 87 | 122 |
| Challenge | 62.6% | 67 | 107 |

## Reasoning Type Breakdown

| Reasoning Type | pass@1 | Cases | LLM Reliability |
|----------------|--------|-------|-----------------|
| L1 API Recall | 72.9% | 240 | Review recommended |
| L2 Rule Application | 74.7% | 166 | Review recommended |
| L3 Cross-Domain | 57.1% | 56 | Expert review required |
| L4 System Reasoning | 65.9% | 138 | Expert review required |
| L1 API Recall | 71.2% | 236 | Review recommended |
| L2 Rule Application | 71.6% | 162 | Review recommended |
| L3 Cross-Domain | 51.8% | 56 | Expert review required |
| L4 System Reasoning | 62.0% | 137 | Expert review required |
| L1 API Recall | 59.1% | 215 | Expert review required |
| L2 Rule Application | 65.9% | 132 | Expert review required |
| L3 Cross-Domain | 37.5% | 40 | Expert review required |
| L4 System Reasoning | 58.6% | 116 | Expert review required |
| L1 API Recall | 70.7% | 215 | Review recommended |
| L2 Rule Application | 73.5% | 132 | Review recommended |
| L3 Cross-Domain | 47.5% | 40 | Expert review required |
| L4 System Reasoning | 62.9% | 116 | Expert review required |

## SDK Breakdown

| SDK | pass@1 | Passed | Total | Notes |
|-----|--------|--------|-------|-------|
| zephyr | 70.3% | 135 | 192 |  |
| embedded-linux | 74.5% | 41 | 55 |  |
| freertos | 100.0% | 2 | 2 | thin bucket (n<8) |
| esp-idf | 70.0% | 7 | 10 |  |
| stm32-hal | 25.0% | 2 | 8 |  |
| zephyr | 67.7% | 130 | 192 |  |
| embedded-linux | 64.7% | 33 | 51 |  |
| freertos | 100.0% | 2 | 2 | thin bucket (n<8) |
| esp-idf | 80.0% | 8 | 10 |  |
| stm32-hal | 50.0% | 4 | 8 |  |
| zephyr | 56.8% | 109 | 192 |  |
| embedded-linux | 71.4% | 15 | 21 |  |
| freertos | 50.0% | 1 | 2 | thin bucket (n<8) |
| esp-idf | 60.0% | 6 | 10 |  |
| stm32-hal | 25.0% | 2 | 8 |  |
| zephyr | 68.2% | 131 | 192 |  |
| embedded-linux | 76.2% | 16 | 21 |  |
| freertos | 0.0% | 0 | 2 | thin bucket (n<8) |
| esp-idf | 60.0% | 6 | 10 |  |
| stm32-hal | 50.0% | 4 | 8 |  |

## Category Results

| Category | pass@1 | Passed | Total | Status |
|----------|--------|--------|-------|--------|
| adc | 100.0% | 2 | 2 | PASS |
| ble | 72.7% | 8 | 11 | PARTIAL |
| boot | 100.0% | 13 | 13 | PASS |
| device-tree | 100.0% | 10 | 10 | PASS |
| dma | 53.8% | 7 | 13 | PARTIAL |
| gpio-basic | 83.3% | 5 | 6 | PASS |
| isr-concurrency | 30.8% | 4 | 13 | FAIL |
| kconfig | 90.0% | 9 | 10 | PASS |
| linux-driver | 77.8% | 14 | 18 | PARTIAL |
| linux-userspace | 87.5% | 7 | 8 | PASS |
| memory-opt | 58.3% | 7 | 12 | PARTIAL |
| networking | 64.7% | 11 | 17 | PARTIAL |
| ota | 72.2% | 13 | 18 | PARTIAL |
| power-mgmt | 75.0% | 9 | 12 | PARTIAL |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 40.0% | 4 | 10 | FAIL |
| sensor-driver | 83.3% | 10 | 12 | PASS |
| spi-i2c | 71.4% | 10 | 14 | PARTIAL |
| storage | 53.8% | 7 | 13 | PARTIAL |
| threading | 40.0% | 6 | 15 | FAIL |
| timer | 75.0% | 9 | 12 | PARTIAL |
| uart | 66.7% | 2 | 3 | PARTIAL |
| watchdog | 80.0% | 8 | 10 | PASS |
| yocto | 78.6% | 11 | 14 | PARTIAL |
| adc | 100.0% | 2 | 2 | PASS |
| ble | 72.7% | 8 | 11 | PARTIAL |
| boot | 100.0% | 13 | 13 | PASS |
| device-tree | 100.0% | 10 | 10 | PASS |
| dma | 38.5% | 5 | 13 | FAIL |
| gpio-basic | 83.3% | 5 | 6 | PASS |
| isr-concurrency | 38.5% | 5 | 13 | FAIL |
| kconfig | 70.0% | 7 | 10 | PARTIAL |
| linux-driver | 68.8% | 11 | 16 | PARTIAL |
| linux-userspace | 75.0% | 6 | 8 | PARTIAL |
| memory-opt | 50.0% | 6 | 12 | PARTIAL |
| networking | 58.8% | 10 | 17 | PARTIAL |
| ota | 61.1% | 11 | 18 | PARTIAL |
| power-mgmt | 83.3% | 10 | 12 | PASS |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 60.0% | 6 | 10 | PARTIAL |
| sensor-driver | 66.7% | 8 | 12 | PARTIAL |
| spi-i2c | 78.6% | 11 | 14 | PARTIAL |
| storage | 53.8% | 7 | 13 | PARTIAL |
| threading | 53.3% | 8 | 15 | PARTIAL |
| timer | 83.3% | 10 | 12 | PASS |
| uart | 66.7% | 2 | 3 | PARTIAL |
| watchdog | 80.0% | 8 | 10 | PASS |
| yocto | 58.3% | 7 | 12 | PARTIAL |
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
| boot | 90.0% | 9 | 10 | PASS |
| device-tree | 100.0% | 10 | 10 | PASS |
| dma | 30.8% | 4 | 13 | FAIL |
| gpio-basic | 66.7% | 4 | 6 | PARTIAL |
| isr-concurrency | 23.1% | 3 | 13 | FAIL |
| kconfig | 90.0% | 9 | 10 | PASS |
| linux-driver | 70.0% | 7 | 10 | PARTIAL |
| memory-opt | 66.7% | 8 | 12 | PARTIAL |
| networking | 75.0% | 9 | 12 | PARTIAL |
| ota | 66.7% | 8 | 12 | PARTIAL |
| power-mgmt | 75.0% | 9 | 12 | PARTIAL |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 50.0% | 5 | 10 | PARTIAL |
| sensor-driver | 75.0% | 9 | 12 | PARTIAL |
| spi-i2c | 78.6% | 11 | 14 | PARTIAL |
| storage | 53.8% | 7 | 13 | PARTIAL |
| threading | 33.3% | 5 | 15 | FAIL |
| timer | 83.3% | 10 | 12 | PASS |
| uart | 33.3% | 1 | 3 | FAIL |
| watchdog | 90.0% | 9 | 10 | PASS |
| yocto | 80.0% | 8 | 10 | PASS |

## Layer Pass Rate Heatmap

| Model| L0 Static| L1 Build| L2 Runtime| L3 Heuristic| L4 Mutation| |
|-------|----------|----------|----------|----------|----------||
| claude-code://claude-opus-5| 94%| 94%| 92%| 87%| 95%| |
| claude-code://claude-sonnet-5| 92%| 94%| 92%| 84%| 100%| |
| claude-code://haiku| 82%| 88%| 93%| 85%| 100%| |
| claude-code://sonnet| 94%| 93%| 90%| 85%| 100%| |

## Failure Distribution

| Layer | Failures | % of Total |
|-------|----------|-----------|
| L0 Static | 0.4 | 22% |
| L1 Build | 0.3 | 19% |
| L2 Runtime | 0.3 | 20% |
| L3 Heuristic | 0.6 | 36% |
| L4 Mutation | 0.1 | 3% |

## Category Breakdown

| Category | Pass@1 | Cases |
|----------|--------|-------|
| adc | 100% | 2 |
| ble | 73% | 11 |
| boot | 100% | 13 |
| device-tree | 100% | 10 |
| dma | 54% | 13 |
| gpio-basic | 83% | 6 |
| isr-concurrency | 31% | 13 |
| kconfig | 90% | 10 |
| linux-driver | 78% | 18 |
| linux-userspace | 88% | 8 |
| memory-opt | 58% | 12 |
| networking | 65% | 17 |
| ota | 72% | 18 |
| power-mgmt | 75% | 12 |
| pwm | 100% | 1 |
| security | 40% | 10 |
| sensor-driver | 83% | 12 |
| spi-i2c | 71% | 14 |
| storage | 54% | 13 |
| threading | 40% | 15 |
| timer | 75% | 12 |
| uart | 67% | 3 |
| watchdog | 80% | 10 |
| yocto | 79% | 14 |
| adc | 100% | 2 |
| ble | 73% | 11 |
| boot | 100% | 13 |
| device-tree | 100% | 10 |
| dma | 38% | 13 |
| gpio-basic | 83% | 6 |
| isr-concurrency | 38% | 13 |
| kconfig | 70% | 10 |
| linux-driver | 69% | 16 |
| linux-userspace | 75% | 8 |
| memory-opt | 50% | 12 |
| networking | 59% | 17 |
| ota | 61% | 18 |
| power-mgmt | 83% | 12 |
| pwm | 100% | 1 |
| security | 60% | 10 |
| sensor-driver | 67% | 12 |
| spi-i2c | 79% | 14 |
| storage | 54% | 13 |
| threading | 53% | 15 |
| timer | 83% | 12 |
| uart | 67% | 3 |
| watchdog | 80% | 10 |
| yocto | 58% | 12 |
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
| boot | 90% | 10 |
| device-tree | 100% | 10 |
| dma | 31% | 13 |
| gpio-basic | 67% | 6 |
| isr-concurrency | 23% | 13 |
| kconfig | 90% | 10 |
| linux-driver | 70% | 10 |
| memory-opt | 67% | 12 |
| networking | 75% | 12 |
| ota | 67% | 12 |
| power-mgmt | 75% | 12 |
| pwm | 100% | 1 |
| security | 50% | 10 |
| sensor-driver | 75% | 12 |
| spi-i2c | 79% | 14 |
| storage | 54% | 13 |
| threading | 33% | 15 |
| timer | 83% | 12 |
| uart | 33% | 3 |
| watchdog | 90% | 10 |
| yocto | 80% | 10 |

## Cross-Benchmark Comparison

| Model | HumanEval | SWE-bench | EmbedEval (full) | EmbedEval (quality) | Embed Gap |
|-------|-----------|-----------|------------------|---------------------|-----------|
| claude-code://claude-opus-5 | 96.3% | 77.1% | 70.0% | 83.5% | -26.3%p |
| claude-code://claude-sonnet-5 | 93.7% | 72.2% | 67.3% | 79.5% | -26.4%p |
| claude-code://haiku | 84.0% | 48.2% | 57.1% | 71.7% | -26.9%p |
| claude-code://sonnet | 93.7% | 72.2% | 67.4% | 82.8% | -26.3%p |

*Embed Gap = EmbedEval pass@1 - HumanEval. Negative = harder than general coding.*
