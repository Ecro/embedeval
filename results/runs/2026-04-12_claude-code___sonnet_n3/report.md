# Benchmark Report: claude-code://sonnet

**Date:** 2026-04-12 22:09 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 233 |
| Passed | 157 |
| Failed | 76 |
| pass@1 | 67.4% |

## Failed Cases (76)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `boot-001` | boot | static_heuristic | img_manager_dependency |
| `dma-001` | dma | compile_gate | west_build_docker |
| `dma-002` | dma | compile_gate | west_build_docker |
| `dma-003` | dma | static_analysis | cyclic_flag_set |
| `dma-004` | dma | runtime_execution | output_validation |
| `dma-007` | dma | runtime_execution | output_validation |
| `dma-009` | dma | static_heuristic | dma_config_after_stop |
| `dma-010` | dma | static_analysis | dma_reload_called |
| `dma-011` | dma | static_analysis | single_dma_start |
| `dma-012` | dma | static_analysis | cache_flush_before_dma |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `esp-nvs-001` | storage | static_heuristic | nvs_set_error_checked |
| `esp-ota-001` | ota | static_heuristic | firmware_validation |
| `esp-sleep-001` | power-mgmt | static_heuristic | gpio_pull_configured |
| `gpio-basic-001` | gpio-basic | static_heuristic | device_ready_check |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | static_analysis | no_printk |
| `isr-concurrency-002` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-005` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-006` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-008` | isr-concurrency | static_heuristic | memory_barrier_present, barrier_between_data_and_index_update |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-012` | isr-concurrency | compile_gate | west_build_docker |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `linux-driver-004` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-009` | linux-driver | static_analysis | gpio_direction_set |
| `memory-opt-001` | memory-opt | runtime_execution | output_validation |
| `memory-opt-003` | memory-opt | runtime_execution | output_validation |
| `memory-opt-005` | memory-opt | static_analysis | partition_added_to_domain |
| `memory-opt-012` | memory-opt | static_heuristic | no_large_string_literals |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-005` | power-mgmt | static_heuristic | all_three_devices_suspended |
| `power-mgmt-009` | power-mgmt | static_heuristic | periodic_battery_check |
| `security-001` | security | runtime_execution | output_validation |
| `security-002` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-007` | security | static_heuristic | error_path_returns_early |
| `security-008` | security | runtime_execution | output_validation |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-freertos-001` | threading | static_heuristic | different_task_priorities |
| `stm32-freertos-002` | isr-concurrency | static_analysis | stm32_hal_header_included |
| `stm32-i2c-001` | spi-i2c | static_analysis | hal_i2c_mem_read_used |
| `stm32-spi-001` | spi-i2c | static_heuristic | cs_deasserted_after_transfer |
| `stm32-timer-001` | timer | static_heuristic | timer_clock_before_init |
| `stm32-uart-001` | networking | static_heuristic | receive_it_rearmed_in_callback |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, verify_before_commit, delete_after_commit |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-012` | storage | static_heuristic | write_rate_limited |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-006` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `threading-010` | threading | compile_gate | west_build_docker |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `timer-001` | timer | runtime_execution | output_validation |
| `uart-002` | uart | static_heuristic | callback_before_rx_enable |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `yocto-001` | yocto | static_analysis | summary_defined, license_defined, lic_files_chksum, src_uri_defined, do_install_defined |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `output_validation` | 20 | dma-004, dma-007, isr-concurrency-002, isr-concurrency-005, isr-concurrency-006 (+15 more) |
| `west_build_docker` | 16 | dma-001, dma-002, isr-concurrency-012, threading-012, ble-009 (+11 more) |
| `init_error_path_cleanup` | 2 | linux-driver-004, linux-driver-006 |
| `img_manager_dependency` | 1 | boot-001 |
| `cyclic_flag_set` | 1 | dma-003 |
| `dma_config_after_stop` | 1 | dma-009 |
| `single_dma_start` | 1 | dma-011 |
| `cache_flush_before_dma` | 1 | dma-012 |
| `device_ready_check` | 1 | gpio-basic-001 |
| `no_printk` | 1 | isr-concurrency-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `memory_barrier_present` | 1 | isr-concurrency-008 |
| `barrier_between_data_and_index_update` | 1 | isr-concurrency-008 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `partition_added_to_domain` | 1 | memory-opt-005 |
| `no_large_string_literals` | 1 | memory-opt-012 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `self_test_failure_branch` | 1 | ota-011 |
| `all_three_devices_suspended` | 1 | power-mgmt-005 |
| `error_path_returns_early` | 1 | security-007 |
| `different_task_priorities` | 1 | stm32-freertos-001 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `cs_deasserted_after_transfer` | 1 | stm32-spi-001 |
| `receive_it_rearmed_in_callback` | 1 | stm32-uart-001 |
| `write_verify_commit_order` | 1 | storage-008 |
| `verify_before_commit` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `write_rate_limited` | 1 | storage-012 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `callback_before_rx_enable` | 1 | uart-002 |
| `summary_defined` | 1 | yocto-001 |
| `license_defined` | 1 | yocto-001 |
| `lic_files_chksum` | 1 | yocto-001 |
| `src_uri_defined` | 1 | yocto-001 |
| `do_install_defined` | 1 | yocto-001 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |
| `dma_reload_called` | 1 | dma-010 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `nvs_set_error_checked` | 1 | esp-nvs-001 |
| `firmware_validation` | 1 | esp-ota-001 |
| `gpio_pull_configured` | 1 | esp-sleep-001 |
| `gpio_direction_set` | 1 | linux-driver-009 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `stm32_hal_header_included` | 1 | stm32-freertos-002 |
| `timer_clock_before_init` | 1 | stm32-timer-001 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 75 | boot-001, dma-001, dma-002, dma-003, dma-004 (+70 more) |
| LLM format failure (prose) | 1 | yocto-007 |

*Adjusted pass@1 (excluding format failures): 67.7% (157/232)*


## TC Improvement Suggestions

