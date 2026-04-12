# Benchmark Report: claude-code://sonnet

**Date:** 2026-04-12 17:52 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 233 |
| Passed | 154 |
| Failed | 79 |
| pass@1 | 66.1% |

## Failed Cases (79)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `dma-001` | dma | compile_gate | west_build_docker |
| `dma-002` | dma | runtime_execution | runtime_started |
| `dma-003` | dma | static_analysis | cyclic_flag_set, dma_reload_called |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-005` | dma | static_heuristic | pre_invalidate_dst_before_dma |
| `dma-007` | dma | runtime_execution | output_validation |
| `dma-008` | dma | compile_gate | west_build_docker |
| `dma-009` | dma | static_heuristic | dma_config_after_stop, timeout_mechanism_present |
| `dma-010` | dma | static_analysis | dma_reload_called |
| `dma-011` | dma | static_analysis | three_block_configs, single_dma_start |
| `dma-012` | dma | static_analysis | cache_flush_before_dma |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `esp-i2c-001` | spi-i2c | static_analysis | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver |
| `esp-nvs-001` | storage | static_heuristic | nvs_set_error_checked |
| `esp-sleep-001` | power-mgmt | static_heuristic | ext0_wakeup_level_low |
| `gpio-basic-001` | gpio-basic | static_heuristic | device_ready_check |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-002` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-005` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-006` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `kconfig-010` | kconfig | static_analysis | hw_cc3xx_enabled |
| `linux-driver-004` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-009` | linux-driver | static_analysis | gpio_direction_set |
| `memory-opt-001` | memory-opt | compile_gate | west_build_docker |
| `memory-opt-003` | memory-opt | compile_gate | west_build_docker |
| `memory-opt-005` | memory-opt | static_analysis | thread_added_to_domain |
| `memory-opt-006` | memory-opt | static_analysis | config_thread_stack_info_enabled |
| `memory-opt-012` | memory-opt | runtime_execution | output_validation |
| `networking-001` | networking | compile_gate | west_build_docker |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `ota-007` | ota | static_heuristic | write_error_checked_in_loop |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-009` | power-mgmt | compile_gate | west_build_docker |
| `pwm-001` | pwm | static_heuristic | infinite_loop_present |
| `security-001` | security | runtime_execution | output_validation |
| `security-002` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-008` | security | runtime_execution | output_validation |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-freertos-001` | threading | static_analysis | stm32_hal_header_included |
| `stm32-i2c-001` | spi-i2c | static_analysis | hal_i2c_mem_read_used |
| `stm32-lowpower-001` | power-mgmt | static_heuristic | rtc_nvic_configured_before_stop |
| `stm32-spi-001` | spi-i2c | static_heuristic | spi_clock_before_init |
| `stm32-timer-001` | timer | static_heuristic | timer_clock_before_init |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-006` | storage | static_heuristic | device_ready_checked |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, delete_after_commit |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-012` | storage | static_heuristic | write_rate_limited |
| `storage-013` | storage | static_heuristic | handler_registered |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-006` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-007` | watchdog | static_heuristic | device_ready_check |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `watchdog-010` | watchdog | static_heuristic | nvs_read_before_watchdog_setup, wdt_setup_called, wdt_install_timeout_called |
| `yocto-001` | yocto | static_analysis | summary_defined, license_defined, lic_files_chksum, src_uri_defined, do_install_defined |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 19 | dma-001, dma-008, isr-concurrency-001, memory-opt-001, memory-opt-003 (+14 more) |
| `output_validation` | 18 | dma-007, isr-concurrency-002, isr-concurrency-005, isr-concurrency-006, isr-concurrency-008 (+13 more) |
| `dma_reload_called` | 2 | dma-003, dma-010 |
| `device_ready_check` | 2 | gpio-basic-001, watchdog-007 |
| `init_error_path_cleanup` | 2 | linux-driver-004, linux-driver-006 |
| `runtime_started` | 1 | dma-002 |
| `cyclic_flag_set` | 1 | dma-003 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `pre_invalidate_dst_before_dma` | 1 | dma-005 |
| `dma_config_after_stop` | 1 | dma-009 |
| `timeout_mechanism_present` | 1 | dma-009 |
| `three_block_configs` | 1 | dma-011 |
| `single_dma_start` | 1 | dma-011 |
| `cache_flush_before_dma` | 1 | dma-012 |
| `i2c_master_header` | 1 | esp-i2c-001 |
| `i2c_master_new_api` | 1 | esp-i2c-001 |
| `no_legacy_i2c_driver` | 1 | esp-i2c-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `thread_added_to_domain` | 1 | memory-opt-005 |
| `config_thread_stack_info_enabled` | 1 | memory-opt-006 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `write_error_checked_in_loop` | 1 | ota-007 |
| `self_test_failure_branch` | 1 | ota-011 |
| `infinite_loop_present` | 1 | pwm-001 |
| `stm32_hal_header_included` | 1 | stm32-freertos-001 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `spi_clock_before_init` | 1 | stm32-spi-001 |
| `device_ready_checked` | 1 | storage-006 |
| `write_verify_commit_order` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `write_rate_limited` | 1 | storage-012 |
| `handler_registered` | 1 | storage-013 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `nvs_read_before_watchdog_setup` | 1 | watchdog-010 |
| `wdt_setup_called` | 1 | watchdog-010 |
| `wdt_install_timeout_called` | 1 | watchdog-010 |
| `summary_defined` | 1 | yocto-001 |
| `license_defined` | 1 | yocto-001 |
| `lic_files_chksum` | 1 | yocto-001 |
| `src_uri_defined` | 1 | yocto-001 |
| `do_install_defined` | 1 | yocto-001 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `nvs_set_error_checked` | 1 | esp-nvs-001 |
| `ext0_wakeup_level_low` | 1 | esp-sleep-001 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `gpio_direction_set` | 1 | linux-driver-009 |
| `rtc_nvic_configured_before_stop` | 1 | stm32-lowpower-001 |
| `timer_clock_before_init` | 1 | stm32-timer-001 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 78 | dma-001, dma-002, dma-003, dma-004, dma-005 (+73 more) |
| LLM format failure (prose) | 1 | yocto-007 |

*Adjusted pass@1 (excluding format failures): 66.4% (154/232)*


## TC Improvement Suggestions

