# Benchmark Report: claude-code://claude-sonnet-5

**Date:** 2026-07-19 06:40 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://claude-sonnet-5 |
| Total Cases | 267 |
| Passed | 178 |
| Failed | 89 |
| pass@1 | 66.7% |

## Failed Cases (89)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-008` | ble | static_heuristic | discovery_after_connected, scan_stopped_before_connect |
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `dma-002` | dma | runtime_execution | runtime_started |
| `dma-003` | dma | static_analysis | cyclic_flag_set |
| `dma-004` | dma | runtime_execution | output_validation |
| `dma-007` | dma | runtime_execution | output_validation |
| `dma-008` | dma | static_heuristic | error_flag_is_volatile, callback_sets_flag_on_error_status, error_flag_causes_return, error_flag_read_after_sync |
| `dma-009` | dma | static_heuristic | timeout_mechanism_present, dma_start_called_twice |
| `dma-010` | dma | static_analysis | dma_reload_called |
| `dma-011` | dma | static_analysis | single_dma_start |
| `dma-012` | dma | static_analysis | buffer_alignment |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | static_analysis | no_printk |
| `isr-concurrency-002` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-005` | isr-concurrency | static_analysis | init_before_isr_call |
| `isr-concurrency-006` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `kconfig-002` | kconfig | static_analysis | bt_hci_enabled |
| `kconfig-010` | kconfig | static_heuristic | hw_cc3xx_requires_psa_driver |
| `linux-driver-004` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-009` | linux-driver | static_heuristic | isr_uses_spin_lock_irqsave |
| `linux-driver-009` | linux-driver | static_analysis | gpio_direction_set |
| `linux-driver-010` | linux-driver | static_analysis | module_platform_driver_macro |
| `linux-driver-013` | linux-driver | static_analysis | mod_devicetable_header_included |
| `linux-driver-016` | linux-driver | static_heuristic | is_err_guards_reset_control_get |
| `linux-userspace-001` | linux-userspace | static_heuristic | nonzero_exit_on_error |
| `linux-userspace-008` | linux-userspace | static_heuristic | comm_array_size_16_bytes |
| `memory-opt-001` | memory-opt | runtime_execution | output_validation |
| `memory-opt-003` | memory-opt | runtime_execution | output_validation |
| `memory-opt-006` | memory-opt | static_analysis | config_thread_stack_info_enabled |
| `memory-opt-011` | memory-opt | runtime_execution | output_validation |
| `memory-opt-012` | memory-opt | runtime_execution | output_validation |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `networking-kernel-002` | networking | static_heuristic | producer_uses_skb_clone, skb_clone_uses_gfp_atomic, skb_clone_return_null_checked, exit_cancels_work_then_purges_queue |
| `networking-kernel-003` | networking | static_heuristic | input_cb_sends_netlink_unicast |
| `networking-kernel-004` | networking | static_analysis | skbuff_header_included |
| `ota-003` | ota | static_heuristic | done_after_write |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `ota-swupdate-002` | ota | static_heuristic | hardware_compatibility_list_nonempty |
| `ota-swupdate-003` | ota | static_heuristic | sha256_values_64_lowercase_hex |
| `power-mgmt-009` | power-mgmt | static_heuristic | periodic_battery_check |
| `power-mgmt-010` | power-mgmt | static_heuristic | state_get_return_checked |
| `security-001` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-007` | security | static_heuristic | error_path_returns_early |
| `security-008` | security | runtime_execution | output_validation |
| `security-010` | security | static_analysis | key_bits_256 |
| `sensor-driver-003` | sensor-driver | static_heuristic | error_handling |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-dma-001` | dma | static_heuristic | data_verified_after_transfer |
| `stm32-lowpower-001` | power-mgmt | static_heuristic | led_toggled_after_wakeup, rtc_clock_source_configured |
| `stm32-spi-001` | spi-i2c | static_heuristic | cs_deasserted_after_transfer, spi_clock_before_init |
| `stm32-timer-001` | timer | static_heuristic | timer_clock_before_init |
| `stm32-uart-001` | networking | static_heuristic | uart_clock_before_init |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-004` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, verify_before_commit, delete_after_commit |
| `storage-009` | storage | static_analysis | offset_plus_size_boundary_check |
| `storage-012` | storage | static_heuristic | write_rate_limited |
| `storage-013` | storage | static_heuristic | handler_registered |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-002` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-010` | threading | static_analysis | k_sem_for_write_exclusion |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | static_analysis | main_function_present |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-007` | timer | static_heuristic | timer_period_less_than_wdt_timeout |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-004` | watchdog | static_heuristic | distinct_channel_timeouts |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `yocto-001` | yocto | static_analysis | summary_defined, license_defined, lic_files_chksum, src_uri_defined, do_install_defined |
| `yocto-003` | yocto | static_analysis | systemd_service_var |
| `yocto-005` | yocto | static_analysis | summary_defined, inherit_module, src_uri_defined, kernel_module_autoload, lic_files_chksum |
| `yocto-007` | yocto | static_analysis | summary_defined |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `output_validation` | 19 | dma-004, dma-007, isr-concurrency-006, isr-concurrency-008, isr-concurrency-011 (+14 more) |
| `west_build_docker` | 12 | isr-concurrency-002, threading-012, ble-009, ble-010, gpio-basic-010 (+7 more) |
| `summary_defined` | 3 | yocto-001, yocto-005, yocto-007 |
| `init_error_path_cleanup` | 2 | linux-driver-004, linux-driver-006 |
| `lic_files_chksum` | 2 | yocto-001, yocto-005 |
| `src_uri_defined` | 2 | yocto-001, yocto-005 |
| `isr_uses_spin_lock_irqsave` | 1 | linux-driver-009 |
| `module_platform_driver_macro` | 1 | linux-driver-010 |
| `mod_devicetable_header_included` | 1 | linux-driver-013 |
| `is_err_guards_reset_control_get` | 1 | linux-driver-016 |
| `nonzero_exit_on_error` | 1 | linux-userspace-001 |
| `comm_array_size_16_bytes` | 1 | linux-userspace-008 |
| `producer_uses_skb_clone` | 1 | networking-kernel-002 |
| `skb_clone_uses_gfp_atomic` | 1 | networking-kernel-002 |
| `skb_clone_return_null_checked` | 1 | networking-kernel-002 |
| `exit_cancels_work_then_purges_queue` | 1 | networking-kernel-002 |
| `input_cb_sends_netlink_unicast` | 1 | networking-kernel-003 |
| `skbuff_header_included` | 1 | networking-kernel-004 |
| `hardware_compatibility_list_nonempty` | 1 | ota-swupdate-002 |
| `sha256_values_64_lowercase_hex` | 1 | ota-swupdate-003 |
| `license_defined` | 1 | yocto-001 |
| `do_install_defined` | 1 | yocto-001 |
| `systemd_service_var` | 1 | yocto-003 |
| `inherit_module` | 1 | yocto-005 |
| `kernel_module_autoload` | 1 | yocto-005 |
| `cs_deasserted_after_transfer` | 1 | stm32-spi-001 |
| `spi_clock_before_init` | 1 | stm32-spi-001 |
| `uart_clock_before_init` | 1 | stm32-uart-001 |
| `discovery_after_connected` | 1 | ble-008 |
| `scan_stopped_before_connect` | 1 | ble-008 |
| `runtime_started` | 1 | dma-002 |
| `cyclic_flag_set` | 1 | dma-003 |
| `error_flag_is_volatile` | 1 | dma-008 |
| `callback_sets_flag_on_error_status` | 1 | dma-008 |
| `error_flag_causes_return` | 1 | dma-008 |
| `error_flag_read_after_sync` | 1 | dma-008 |
| `timeout_mechanism_present` | 1 | dma-009 |
| `dma_start_called_twice` | 1 | dma-009 |
| `single_dma_start` | 1 | dma-011 |
| `buffer_alignment` | 1 | dma-012 |
| `no_printk` | 1 | isr-concurrency-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `init_before_isr_call` | 1 | isr-concurrency-005 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `bt_hci_enabled` | 1 | kconfig-002 |
| `config_thread_stack_info_enabled` | 1 | memory-opt-006 |
| `connect_error_handling` | 1 | networking-008 |
| `done_after_write` | 1 | ota-003 |
| `self_test_failure_branch` | 1 | ota-011 |
| `error_path_returns_early` | 1 | security-007 |
| `error_handling` | 1 | sensor-driver-003 |
| `write_verify_commit_order` | 1 | storage-008 |
| `verify_before_commit` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `write_rate_limited` | 1 | storage-012 |
| `handler_registered` | 1 | storage-013 |
| `main_function_present` | 1 | threading-013 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `counter_is_volatile` | 1 | timer-001 |
| `timer_period_less_than_wdt_timeout` | 1 | timer-007 |
| `distinct_channel_timeouts` | 1 | watchdog-004 |
| `gpio_direction_set` | 1 | linux-driver-009 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `data_verified_after_transfer` | 1 | stm32-dma-001 |
| `led_toggled_after_wakeup` | 1 | stm32-lowpower-001 |
| `rtc_clock_source_configured` | 1 | stm32-lowpower-001 |
| `timer_clock_before_init` | 1 | stm32-timer-001 |
| `dma_reload_called` | 1 | dma-010 |
| `hw_cc3xx_requires_psa_driver` | 1 | kconfig-010 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `state_get_return_checked` | 1 | power-mgmt-010 |
| `key_bits_256` | 1 | security-010 |
| `offset_plus_size_boundary_check` | 1 | storage-009 |
| `k_sem_for_write_exclusion` | 1 | threading-010 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 84 | linux-driver-004, linux-driver-006, linux-driver-009, linux-driver-010, linux-driver-013 (+79 more) |
| LLM format failure (prose) | 5 | ota-swupdate-002, ota-swupdate-003, yocto-001, yocto-003, yocto-007 |

*Adjusted pass@1 (excluding format failures): 67.9% (178/262)*


## TC Improvement Suggestions

