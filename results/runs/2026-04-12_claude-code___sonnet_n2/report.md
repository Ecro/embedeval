# Benchmark Report: claude-code://sonnet

**Date:** 2026-04-12 19:56 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 233 |
| Passed | 164 |
| Failed | 69 |
| pass@1 | 70.4% |

## Failed Cases (69)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `device-tree-003` | device-tree | static_heuristic | pwm_polarity_specified |
| `dma-002` | dma | runtime_execution | runtime_started |
| `dma-003` | dma | static_analysis | cyclic_flag_set |
| `dma-004` | dma | compile_gate | west_build_docker |
| `dma-005` | dma | compile_gate | west_build_docker |
| `dma-007` | dma | runtime_execution | output_validation |
| `dma-008` | dma | static_heuristic | error_flag_is_volatile, callback_sets_flag_on_error_status, error_flag_causes_return, error_flag_read_after_sync |
| `dma-009` | dma | static_heuristic | dma_config_after_stop |
| `dma-010` | dma | static_analysis | dma_reload_called |
| `dma-011` | dma | static_analysis | single_dma_start |
| `dma-012` | dma | static_analysis | cache_flush_before_dma |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `esp-nvs-001` | storage | static_heuristic | nvs_set_error_checked |
| `esp-ota-001` | ota | static_heuristic | firmware_validation |
| `gpio-basic-001` | gpio-basic | static_heuristic | device_ready_check |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-002` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-005` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-006` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-012` | isr-concurrency | static_analysis | no_isr_unsafe_primitives |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `linux-driver-004` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-009` | linux-driver | static_analysis | gpio_direction_set |
| `memory-opt-001` | memory-opt | runtime_execution | output_validation |
| `memory-opt-003` | memory-opt | runtime_execution | output_validation |
| `memory-opt-005` | memory-opt | static_analysis | partition_added_to_domain |
| `memory-opt-012` | memory-opt | runtime_execution | output_validation |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-009` | power-mgmt | static_heuristic | periodic_battery_check, multiple_sleep_depths |
| `pwm-001` | pwm | static_heuristic | infinite_loop_present |
| `security-001` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-007` | security | static_heuristic | error_path_returns_early |
| `security-008` | security | runtime_execution | output_validation |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-freertos-001` | threading | static_analysis | stm32_hal_header_included |
| `stm32-i2c-001` | spi-i2c | static_analysis | hal_i2c_mem_read_used |
| `stm32-spi-001` | spi-i2c | static_heuristic | spi_clock_before_init |
| `stm32-timer-001` | timer | static_heuristic | timer_clock_before_init |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, verify_before_commit, delete_after_commit |
| `storage-009` | storage | static_analysis | offset_plus_size_boundary_check |
| `storage-012` | storage | static_heuristic | write_rate_limited |
| `storage-013` | storage | static_heuristic | handler_registered |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `uart-002` | uart | static_heuristic | callback_before_rx_enable |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `output_validation` | 17 | dma-007, isr-concurrency-002, isr-concurrency-005, isr-concurrency-008, isr-concurrency-011 (+12 more) |
| `west_build_docker` | 15 | dma-004, dma-005, isr-concurrency-001, isr-concurrency-006, threading-012 (+10 more) |
| `init_error_path_cleanup` | 2 | linux-driver-004, linux-driver-006 |
| `pwm_polarity_specified` | 1 | device-tree-003 |
| `runtime_started` | 1 | dma-002 |
| `cyclic_flag_set` | 1 | dma-003 |
| `error_flag_is_volatile` | 1 | dma-008 |
| `callback_sets_flag_on_error_status` | 1 | dma-008 |
| `error_flag_causes_return` | 1 | dma-008 |
| `error_flag_read_after_sync` | 1 | dma-008 |
| `dma_config_after_stop` | 1 | dma-009 |
| `single_dma_start` | 1 | dma-011 |
| `cache_flush_before_dma` | 1 | dma-012 |
| `device_ready_check` | 1 | gpio-basic-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `no_isr_unsafe_primitives` | 1 | isr-concurrency-012 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `partition_added_to_domain` | 1 | memory-opt-005 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `self_test_failure_branch` | 1 | ota-011 |
| `infinite_loop_present` | 1 | pwm-001 |
| `error_path_returns_early` | 1 | security-007 |
| `stm32_hal_header_included` | 1 | stm32-freertos-001 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `spi_clock_before_init` | 1 | stm32-spi-001 |
| `write_verify_commit_order` | 1 | storage-008 |
| `verify_before_commit` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `write_rate_limited` | 1 | storage-012 |
| `handler_registered` | 1 | storage-013 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `callback_before_rx_enable` | 1 | uart-002 |
| `dma_reload_called` | 1 | dma-010 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `nvs_set_error_checked` | 1 | esp-nvs-001 |
| `firmware_validation` | 1 | esp-ota-001 |
| `gpio_direction_set` | 1 | linux-driver-009 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `multiple_sleep_depths` | 1 | power-mgmt-009 |
| `timer_clock_before_init` | 1 | stm32-timer-001 |
| `offset_plus_size_boundary_check` | 1 | storage-009 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## TC Improvement Suggestions

