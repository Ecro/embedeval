# EmbedEval Leaderboard

<!-- SCHEMA_VERSION: 1 -->


## Model Comparison

| Model | pass@1 (full) | pass@1 (quality) | 95% CI | pass@5 | Passed | Quality | Total | Samples |
|-------|---------------|------------------|--------|--------|--------|---------|-------|---------|
| claude-code://claude-opus-5 | 63.0% | 74.0% | [56.4%, 69.1%] | 63.0% | 138 | 162 | 219 | n=1 |
| claude-code://claude-sonnet-5 | 68.9% | 78.5% | [62.5%, 74.7%] | 68.9% | 151 | 172 | 219 | n=1 |
| claude-code://haiku | 59.8% | 72.0% | [52.7%, 66.5%] | 59.8% | 113 | 136 | 189 | n=1 |
| claude-code://sonnet | 70.9% | 83.6% | [64.1%, 76.9%] | 70.9% | 134 | 158 | 189 | n=1 |

*pass@1 (full) = all layers must pass. pass@1 (quality) = L0+L3 only (code quality, ignoring build/runtime).*

## Tier Breakdown

| Tier | pass@1 | Passed | Total |
|------|--------|--------|-------|
| Sanity (not scored) | 66.7% | 2 | 3 |
| Core | 70.6% | 77 | 109 |
| Challenge | 55.1% | 59 | 107 |
| Sanity (not scored) | 66.7% | 2 | 3 |
| Core | 72.5% | 79 | 109 |
| Challenge | 65.4% | 70 | 107 |
| Sanity (not scored) | 33.3% | 1 | 3 |
| Core | 67.3% | 66 | 98 |
| Challenge | 52.3% | 46 | 88 |
| Sanity (not scored) | 66.7% | 2 | 3 |
| Core | 76.5% | 75 | 98 |
| Challenge | 64.8% | 57 | 88 |

## Reasoning Type Breakdown

| Reasoning Type | pass@1 | Cases | LLM Reliability |
|----------------|--------|-------|-----------------|
| L1 API Recall | 66.1% | 192 | Expert review required |
| L2 Rule Application | 68.6% | 140 | Expert review required |
| L3 Cross-Domain | 48.1% | 52 | Expert review required |
| L4 System Reasoning | 60.7% | 117 | Expert review required |
| L1 API Recall | 74.0% | 192 | Review recommended |
| L2 Rule Application | 72.1% | 140 | Review recommended |
| L3 Cross-Domain | 50.0% | 52 | Expert review required |
| L4 System Reasoning | 63.2% | 117 | Expert review required |
| L1 API Recall | 62.6% | 171 | Expert review required |
| L2 Rule Application | 66.4% | 110 | Expert review required |
| L3 Cross-Domain | 36.1% | 36 | Expert review required |
| L4 System Reasoning | 62.5% | 96 | Expert review required |
| L1 API Recall | 75.4% | 171 | Review recommended |
| L2 Rule Application | 76.4% | 110 | Review recommended |
| L3 Cross-Domain | 47.2% | 36 | Expert review required |
| L4 System Reasoning | 66.7% | 96 | Expert review required |

## SDK Breakdown

| SDK | pass@1 | Passed | Total | Notes |
|-----|--------|--------|-------|-------|
| zephyr | 63.3% | 100 | 158 |  |
| embedded-linux | 64.7% | 33 | 51 |  |
| freertos | 100.0% | 1 | 1 | thin bucket (n<8) |
| esp-idf | 60.0% | 3 | 5 | thin bucket (n<8) |
| stm32-hal | 25.0% | 1 | 4 | thin bucket (n<8) |
| zephyr | 70.9% | 112 | 158 |  |
| embedded-linux | 64.7% | 33 | 51 |  |
| freertos | 100.0% | 1 | 1 | thin bucket (n<8) |
| esp-idf | 80.0% | 4 | 5 | thin bucket (n<8) |
| stm32-hal | 25.0% | 1 | 4 | thin bucket (n<8) |
| zephyr | 58.2% | 92 | 158 |  |
| embedded-linux | 71.4% | 15 | 21 |  |
| freertos | 0.0% | 0 | 1 | thin bucket (n<8) |
| esp-idf | 80.0% | 4 | 5 | thin bucket (n<8) |
| stm32-hal | 50.0% | 2 | 4 | thin bucket (n<8) |
| zephyr | 70.9% | 112 | 158 |  |
| embedded-linux | 76.2% | 16 | 21 |  |
| freertos | 0.0% | 0 | 1 | thin bucket (n<8) |
| esp-idf | 100.0% | 5 | 5 | thin bucket (n<8) |
| stm32-hal | 25.0% | 1 | 4 | thin bucket (n<8) |

## Category Results

| Category | pass@1 | Passed | Total | Status |
|----------|--------|--------|-------|--------|
| adc | 50.0% | 1 | 2 | PARTIAL |
| ble | 75.0% | 6 | 8 | PARTIAL |
| boot | 100.0% | 11 | 11 | PASS |
| device-tree | 100.0% | 8 | 8 | PASS |
| dma | 45.5% | 5 | 11 | FAIL |
| gpio-basic | 100.0% | 5 | 5 | PASS |
| isr-concurrency | 20.0% | 2 | 10 | FAIL |
| kconfig | 87.5% | 7 | 8 | PASS |
| linux-driver | 68.8% | 11 | 16 | PARTIAL |
| linux-userspace | 50.0% | 4 | 8 | PARTIAL |
| memory-opt | 50.0% | 5 | 10 | PARTIAL |
| networking | 53.3% | 8 | 15 | PARTIAL |
| ota | 40.0% | 6 | 15 | FAIL |
| power-mgmt | 75.0% | 6 | 8 | PARTIAL |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 37.5% | 3 | 8 | FAIL |
| sensor-driver | 100.0% | 8 | 8 | PASS |
| spi-i2c | 75.0% | 9 | 12 | PARTIAL |
| storage | 40.0% | 4 | 10 | FAIL |
| threading | 38.5% | 5 | 13 | FAIL |
| timer | 66.7% | 6 | 9 | PARTIAL |
| uart | 50.0% | 1 | 2 | PARTIAL |
| watchdog | 77.8% | 7 | 9 | PARTIAL |
| yocto | 75.0% | 9 | 12 | PARTIAL |
| adc | 100.0% | 2 | 2 | PASS |
| ble | 87.5% | 7 | 8 | PASS |
| boot | 100.0% | 11 | 11 | PASS |
| device-tree | 100.0% | 8 | 8 | PASS |
| dma | 36.4% | 4 | 11 | FAIL |
| gpio-basic | 100.0% | 5 | 5 | PASS |
| isr-concurrency | 30.0% | 3 | 10 | FAIL |
| kconfig | 75.0% | 6 | 8 | PARTIAL |
| linux-driver | 68.8% | 11 | 16 | PARTIAL |
| linux-userspace | 75.0% | 6 | 8 | PARTIAL |
| memory-opt | 40.0% | 4 | 10 | FAIL |
| networking | 60.0% | 9 | 15 | PARTIAL |
| ota | 60.0% | 9 | 15 | PARTIAL |
| power-mgmt | 100.0% | 8 | 8 | PASS |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 50.0% | 4 | 8 | PARTIAL |
| sensor-driver | 87.5% | 7 | 8 | PASS |
| spi-i2c | 83.3% | 10 | 12 | PASS |
| storage | 50.0% | 5 | 10 | PARTIAL |
| threading | 53.8% | 7 | 13 | PARTIAL |
| timer | 77.8% | 7 | 9 | PARTIAL |
| uart | 100.0% | 2 | 2 | PASS |
| watchdog | 88.9% | 8 | 9 | PASS |
| yocto | 58.3% | 7 | 12 | PARTIAL |
| adc | 50.0% | 1 | 2 | PARTIAL |
| ble | 50.0% | 4 | 8 | PARTIAL |
| boot | 100.0% | 8 | 8 | PASS |
| device-tree | 100.0% | 8 | 8 | PASS |
| dma | 9.1% | 1 | 11 | FAIL |
| gpio-basic | 100.0% | 5 | 5 | PASS |
| isr-concurrency | 30.0% | 3 | 10 | FAIL |
| kconfig | 62.5% | 5 | 8 | PARTIAL |
| linux-driver | 70.0% | 7 | 10 | PARTIAL |
| memory-opt | 20.0% | 2 | 10 | FAIL |
| networking | 80.0% | 8 | 10 | PASS |
| ota | 77.8% | 7 | 9 | PARTIAL |
| power-mgmt | 87.5% | 7 | 8 | PASS |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 62.5% | 5 | 8 | PARTIAL |
| sensor-driver | 100.0% | 8 | 8 | PASS |
| spi-i2c | 66.7% | 8 | 12 | PARTIAL |
| storage | 20.0% | 2 | 10 | FAIL |
| threading | 30.8% | 4 | 13 | FAIL |
| timer | 44.4% | 4 | 9 | FAIL |
| uart | 100.0% | 2 | 2 | PASS |
| watchdog | 66.7% | 6 | 9 | PARTIAL |
| yocto | 70.0% | 7 | 10 | PARTIAL |
| adc | 100.0% | 2 | 2 | PASS |
| ble | 100.0% | 8 | 8 | PASS |
| boot | 87.5% | 7 | 8 | PASS |
| device-tree | 100.0% | 8 | 8 | PASS |
| dma | 27.3% | 3 | 11 | FAIL |
| gpio-basic | 80.0% | 4 | 5 | PASS |
| isr-concurrency | 20.0% | 2 | 10 | FAIL |
| kconfig | 87.5% | 7 | 8 | PASS |
| linux-driver | 70.0% | 7 | 10 | PARTIAL |
| memory-opt | 60.0% | 6 | 10 | PARTIAL |
| networking | 80.0% | 8 | 10 | PASS |
| ota | 77.8% | 7 | 9 | PARTIAL |
| power-mgmt | 87.5% | 7 | 8 | PASS |
| pwm | 100.0% | 1 | 1 | PASS |
| security | 37.5% | 3 | 8 | FAIL |
| sensor-driver | 100.0% | 8 | 8 | PASS |
| spi-i2c | 83.3% | 10 | 12 | PASS |
| storage | 60.0% | 6 | 10 | PARTIAL |
| threading | 30.8% | 4 | 13 | FAIL |
| timer | 88.9% | 8 | 9 | PASS |
| uart | 50.0% | 1 | 2 | PARTIAL |
| watchdog | 100.0% | 9 | 9 | PASS |
| yocto | 80.0% | 8 | 10 | PASS |

## Layer Pass Rate Heatmap

| Model| L0 Static| L1 Build| L2 Runtime| L3 Heuristic| L4 Mutation| |
|-------|----------|----------|----------|----------|----------||
| claude-code://claude-opus-5| 95%| 98%| 90%| 75%| 96%| |
| claude-code://claude-sonnet-5| 92%| 99%| 91%| 83%| 100%| |
| claude-code://haiku| 83%| 92%| 92%| 84%| 100%| |
| claude-code://sonnet| 95%| 98%| 89%| 86%| 100%| |

## Failure Distribution

| Layer | Failures | % of Total |
|-------|----------|-----------|
| L0 Static | 0.4 | 22% |
| L1 Build | 0.1 | 8% |
| L2 Runtime | 0.4 | 23% |
| L3 Heuristic | 0.7 | 44% |
| L4 Mutation | 0.0 | 3% |

## Category Breakdown

| Category | Pass@1 | Cases |
|----------|--------|-------|
| adc | 50% | 2 |
| ble | 75% | 8 |
| boot | 100% | 11 |
| device-tree | 100% | 8 |
| dma | 45% | 11 |
| gpio-basic | 100% | 5 |
| isr-concurrency | 20% | 10 |
| kconfig | 88% | 8 |
| linux-driver | 69% | 16 |
| linux-userspace | 50% | 8 |
| memory-opt | 50% | 10 |
| networking | 53% | 15 |
| ota | 40% | 15 |
| power-mgmt | 75% | 8 |
| pwm | 100% | 1 |
| security | 38% | 8 |
| sensor-driver | 100% | 8 |
| spi-i2c | 75% | 12 |
| storage | 40% | 10 |
| threading | 38% | 13 |
| timer | 67% | 9 |
| uart | 50% | 2 |
| watchdog | 78% | 9 |
| yocto | 75% | 12 |
| adc | 100% | 2 |
| ble | 88% | 8 |
| boot | 100% | 11 |
| device-tree | 100% | 8 |
| dma | 36% | 11 |
| gpio-basic | 100% | 5 |
| isr-concurrency | 30% | 10 |
| kconfig | 75% | 8 |
| linux-driver | 69% | 16 |
| linux-userspace | 75% | 8 |
| memory-opt | 40% | 10 |
| networking | 60% | 15 |
| ota | 60% | 15 |
| power-mgmt | 100% | 8 |
| pwm | 100% | 1 |
| security | 50% | 8 |
| sensor-driver | 88% | 8 |
| spi-i2c | 83% | 12 |
| storage | 50% | 10 |
| threading | 54% | 13 |
| timer | 78% | 9 |
| uart | 100% | 2 |
| watchdog | 89% | 9 |
| yocto | 58% | 12 |
| adc | 50% | 2 |
| ble | 50% | 8 |
| boot | 100% | 8 |
| device-tree | 100% | 8 |
| dma | 9% | 11 |
| gpio-basic | 100% | 5 |
| isr-concurrency | 30% | 10 |
| kconfig | 62% | 8 |
| linux-driver | 70% | 10 |
| memory-opt | 20% | 10 |
| networking | 80% | 10 |
| ota | 78% | 9 |
| power-mgmt | 88% | 8 |
| pwm | 100% | 1 |
| security | 62% | 8 |
| sensor-driver | 100% | 8 |
| spi-i2c | 67% | 12 |
| storage | 20% | 10 |
| threading | 31% | 13 |
| timer | 44% | 9 |
| uart | 100% | 2 |
| watchdog | 67% | 9 |
| yocto | 70% | 10 |
| adc | 100% | 2 |
| ble | 100% | 8 |
| boot | 88% | 8 |
| device-tree | 100% | 8 |
| dma | 27% | 11 |
| gpio-basic | 80% | 5 |
| isr-concurrency | 20% | 10 |
| kconfig | 88% | 8 |
| linux-driver | 70% | 10 |
| memory-opt | 60% | 10 |
| networking | 80% | 10 |
| ota | 78% | 9 |
| power-mgmt | 88% | 8 |
| pwm | 100% | 1 |
| security | 38% | 8 |
| sensor-driver | 100% | 8 |
| spi-i2c | 83% | 12 |
| storage | 60% | 10 |
| threading | 31% | 13 |
| timer | 89% | 9 |
| uart | 50% | 2 |
| watchdog | 100% | 9 |
| yocto | 80% | 10 |

## Cross-Benchmark Comparison

| Model | HumanEval | SWE-bench | EmbedEval (full) | EmbedEval (quality) | Embed Gap |
|-------|-----------|-----------|------------------|---------------------|-----------|
| claude-code://claude-opus-5 | 96.3% | 77.1% | 63.0% | 74.0% | -33.3%p |
| claude-code://claude-sonnet-5 | 93.7% | 72.2% | 68.9% | 78.5% | -24.8%p |
| claude-code://haiku | 84.0% | 48.2% | 59.8% | 72.0% | -24.2%p |
| claude-code://sonnet | 93.7% | 72.2% | 70.9% | 83.6% | -22.8%p |

*Embed Gap = EmbedEval pass@1 - HumanEval. Negative = harder than general coding.*
