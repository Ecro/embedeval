# Benchmark Report: claude-code://sonnet

**Date:** 2026-03-25 02:41 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 210 |
| Passed | 188 |
| Failed | 22 |
| pass@1 | 89.5% |

## Failed Cases (22)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `device-tree-003` | device-tree | static_heuristic | pwm_polarity_specified |
| `dma-003` | dma | static_heuristic | cyclic_enabled |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `esp-nvs-001` | storage | static_heuristic | nvs_set_error_checked |
| `gpio-basic-001` | gpio-basic | static_heuristic | device_ready_check |
| `isr-concurrency-003` | isr-concurrency | static_analysis | shared_variable_declared |
| `isr-concurrency-008` | isr-concurrency | static_heuristic | memory_barrier_present, barrier_between_data_and_index_update |
| `linux-driver-001` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `memory-opt-001` | memory-opt | static_heuristic | block_size_defined |
| `networking-001` | networking | static_heuristic | connect_error_handling |
| `networking-008` | networking | static_heuristic | will_configured_before_connect, connect_error_handling |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error |
| `power-mgmt-001` | power-mgmt | static_heuristic | pm_error_handling |
| `power-mgmt-009` | power-mgmt | static_heuristic | periodic_battery_check |
| `sensor-driver-003` | sensor-driver | static_heuristic | periodic_loop |
| `spi-i2c-004` | spi-i2c | static_heuristic | write_enable_before_write, poll_loop_bounded |
| `storage-004` | storage | static_heuristic | error_handling |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `timer-006` | timer | static_heuristic | counter_stopped_after_use |
| `watchdog-007` | watchdog | static_heuristic | device_ready_check |
| `watchdog-010` | watchdog | static_heuristic | error_handling_present |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `device_ready_check` | 2 | gpio-basic-001, watchdog-007 |
| `init_error_path_cleanup` | 2 | linux-driver-001, linux-driver-006 |
| `connect_error_handling` | 2 | networking-001, networking-008 |
| `pwm_polarity_specified` | 1 | device-tree-003 |
| `cyclic_enabled` | 1 | dma-003 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `nvs_set_error_checked` | 1 | esp-nvs-001 |
| `shared_variable_declared` | 1 | isr-concurrency-003 |
| `memory_barrier_present` | 1 | isr-concurrency-008 |
| `barrier_between_data_and_index_update` | 1 | isr-concurrency-008 |
| `block_size_defined` | 1 | memory-opt-001 |
| `will_configured_before_connect` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `pm_error_handling` | 1 | power-mgmt-001 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `periodic_loop` | 1 | sensor-driver-003 |
| `write_enable_before_write` | 1 | spi-i2c-004 |
| `poll_loop_bounded` | 1 | spi-i2c-004 |
| `error_handling` | 1 | storage-004 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `counter_stopped_after_use` | 1 | timer-006 |
| `error_handling_present` | 1 | watchdog-010 |

## TC Improvement Suggestions

