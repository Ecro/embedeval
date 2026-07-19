# Benchmark Delta — claude-code://claude-sonnet-5 vs claude-code://sonnet

**Pure model improvement is the INTERSECTION row.** The two models ran
different case sets; only the common cases isolate model capability
from case-set change. Cases unique to the newer run are reported
separately (absolute performance only — no baseline to diff against).

## Per-case verdict method

- claude-code://claude-sonnet-5: majority vote of 3 runs (>= 2 of 3 passing = pass)
- claude-code://sonnet: majority vote of 3 runs (>= 2 of 3 passing = pass)

## Case-set overlap

| Set | Cases |
|-----|-------|
| Intersection (both models) | 232 |
| New-only (in claude-code://claude-sonnet-5) | 31 |
| Dropped (only in claude-code://sonnet) | 1 |

## Pure model improvement (intersection only)

| Model | pass@1 (majority) | passed / total |
|-------|-------------------|----------------|
| claude-code://sonnet | 68.1% | 158 / 232 |
| claude-code://claude-sonnet-5 | 67.2% | 156 / 232 |
| **Delta** | **-0.9%p** | — |

### Per-run pass@1 (each over its own full case set, for reference)

- claude-code://sonnet: 66.1%, 70.4%, 67.4% (mean 68.0%)
- claude-code://claude-sonnet-5: 66.9%, 66.9%, 67.3% (mean 67.0%)

## New-only cases (31) — claude-code://claude-sonnet-5 absolute performance

- pass@1 (majority): **71.0%** (22 / 31)
- No baseline: these cases did not exist in the older run.

## Improved: claude-code://sonnet fail -> claude-code://claude-sonnet-5 pass (18)

| Category | Cases |
|----------|-------|
| dma | dma-001, dma-005 |
| gpio-basic | gpio-basic-001 |
| isr-concurrency | isr-concurrency-012 |
| linux-driver | linux-driver-004 |
| memory-opt | memory-opt-005 |
| ota | esp-ota-001, ota-005 |
| power-mgmt | esp-sleep-001 |
| pwm | pwm-001 |
| security | security-002 |
| storage | esp-nvs-001 |
| threading | stm32-freertos-001, threading-006, threading-008 |
| timer | stm32-timer-001 |
| uart | uart-002 |
| yocto | yocto-001 |

## Regressed: claude-code://sonnet pass -> claude-code://claude-sonnet-5 fail (20)

| Category | Cases |
|----------|-------|
| ble | ble-008 |
| dma | stm32-dma-001 |
| kconfig | kconfig-002, kconfig-010 |
| memory-opt | memory-opt-006, memory-opt-007, memory-opt-011 |
| networking | esp-wifi-001, stm32-uart-001 |
| ota | ota-003 |
| power-mgmt | power-mgmt-010 |
| security | security-010 |
| sensor-driver | sensor-driver-003 |
| storage | storage-004 |
| threading | threading-010 |
| timer | timer-001, timer-007 |
| watchdog | watchdog-004 |
| yocto | yocto-003, yocto-005 |
