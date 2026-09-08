# Benchmark Report: claude-code://claude-opus-5

**Date:** 2026-09-08 15:13 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://claude-opus-5 |
| Total Cases | 48 |
| Passed | 27 |
| Failed | 21 |
| pass@1 | 56.2% |

## Failed Cases (21)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `dma-010` | dma | runtime_execution | runtime_started |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `esp-sleep-001` | power-mgmt | static_heuristic | ext0_wakeup_level_low |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `kconfig-010` | kconfig | static_analysis | hw_cc3xx_enabled |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-010` | ota | compile_gate | west_build_docker |
| `power-mgmt-009` | power-mgmt | static_heuristic | periodic_battery_check |
| `security-010` | security | static_analysis | key_bits_256 |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-dma-001` | dma | static_heuristic | data_verified_after_transfer |
| `stm32-timer-001` | timer | static_heuristic | prescaler_arr_gives_1khz, duty_cycle_approximately_50pct, timer_clock_before_init |
| `storage-009` | storage | compile_gate | west_build_docker |
| `threading-010` | threading | static_analysis | k_sem_for_write_exclusion |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 11 | ble-009, ble-010, gpio-basic-010, isr-concurrency-009, networking-009 (+6 more) |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `ext0_wakeup_level_low` | 1 | esp-sleep-001 |
| `data_verified_after_transfer` | 1 | stm32-dma-001 |
| `prescaler_arr_gives_1khz` | 1 | stm32-timer-001 |
| `duty_cycle_approximately_50pct` | 1 | stm32-timer-001 |
| `timer_clock_before_init` | 1 | stm32-timer-001 |
| `runtime_started` | 1 | dma-010 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `key_bits_256` | 1 | security-010 |
| `k_sem_for_write_exclusion` | 1 | threading-010 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## TC Improvement Suggestions

