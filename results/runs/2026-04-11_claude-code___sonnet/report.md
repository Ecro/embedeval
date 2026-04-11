# Benchmark Report: claude-code://sonnet

**Date:** 2026-04-11 10:32 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 61 |
| Passed | 33 |
| Failed | 28 |
| pass@1 | 54.1% |

## Failed Cases (28)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `dma-010` | dma | static_analysis | dma_reload_called |
| `dma-011` | dma | static_analysis | single_dma_start |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-012` | isr-concurrency | static_analysis | no_isr_unsafe_primitives |
| `kconfig-010` | kconfig | static_analysis | hw_cc3xx_enabled |
| `linux-driver-009` | linux-driver | static_analysis | gpio_direction_set |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-009` | power-mgmt | compile_gate | west_build_docker |
| `security-004` | security | runtime_execution | output_validation |
| `security-008` | security | runtime_execution | output_validation |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-timer-001` | timer | static_heuristic | timer_clock_before_init |
| `storage-009` | storage | static_analysis | offset_plus_size_boundary_check |
| `storage-013` | storage | static_analysis | save_not_unconditional_in_loop |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-010` | threading | compile_gate | west_build_docker |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 12 | ble-009, ble-010, gpio-basic-010, isr-concurrency-009, networking-009 (+7 more) |
| `output_validation` | 3 | security-004, security-008, threading-001 |
| `single_dma_start` | 1 | dma-011 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `no_isr_unsafe_primitives` | 1 | isr-concurrency-012 |
| `self_test_failure_branch` | 1 | ota-011 |
| `save_not_unconditional_in_loop` | 1 | storage-013 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `dma_reload_called` | 1 | dma-010 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `gpio_direction_set` | 1 | linux-driver-009 |
| `timer_clock_before_init` | 1 | stm32-timer-001 |
| `offset_plus_size_boundary_check` | 1 | storage-009 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## TC Improvement Suggestions

