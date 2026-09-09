# Benchmark Report: claude-code://claude-opus-5

**Date:** 2026-09-09 04:30 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://claude-opus-5 |
| Total Cases | 267 |
| Passed | 187 |
| Failed | 80 |
| pass@1 | 70.0% |

## Failed Cases (80)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-008` | ble | static_heuristic | bt_enable_before_scan, conn_unref_in_disconnected, discovery_after_connected, conn_cleanup_on_failed_connect |
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `dma-002` | dma | runtime_execution | runtime_started |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-005` | dma | static_heuristic | pre_invalidate_dst_before_dma |
| `dma-007` | dma | static_analysis | two_dma_config_calls |
| `dma-011` | dma | static_analysis | three_block_configs, single_dma_start, block_count_three |
| `esp-i2c-001` | spi-i2c | static_analysis | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver |
| `esp-sleep-001` | power-mgmt | static_heuristic | ext0_wakeup_level_low |
| `esp-wifi-001` | networking | static_heuristic | nvs_initialized_before_wifi |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | static_analysis | no_printk |
| `isr-concurrency-002` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-004` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-005` | isr-concurrency | static_analysis | init_before_isr_call |
| `isr-concurrency-006` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | compile_gate | west_build_docker |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-010` | linux-driver | static_analysis | module_platform_driver_macro |
| `linux-driver-011` | linux-driver | static_heuristic | free_irq_before_cancel_work |
| `linux-driver-016` | linux-driver | static_heuristic | is_err_guards_reset_control_get |
| `linux-userspace-001` | linux-userspace | static_heuristic | nonzero_exit_on_error |
| `memory-opt-003` | memory-opt | runtime_execution | output_validation |
| `memory-opt-006` | memory-opt | static_analysis | config_thread_stack_info_enabled |
| `memory-opt-007` | memory-opt | runtime_execution | output_validation |
| `memory-opt-011` | memory-opt | runtime_execution | output_validation |
| `memory-opt-012` | memory-opt | runtime_execution | output_validation |
| `networking-009` | networking | compile_gate | west_build_docker |
| `networking-kernel-002` | networking | static_heuristic | exit_cancels_work_then_purges_queue |
| `networking-kernel-003` | networking | static_heuristic | input_cb_sends_netlink_unicast |
| `networking-kernel-004` | networking | static_heuristic | genl_family_has_name_field |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `ota-swupdate-001` | ota | static_heuristic | hardware_compatibility_list_nonempty |
| `ota-swupdate-002` | ota | static_heuristic | hardware_compatibility_list_nonempty |
| `ota-swupdate-004` | ota | static_heuristic | hardware_compatibility_list_nonempty |
| `power-mgmt-009` | power-mgmt | compile_gate | west_build_docker |
| `security-001` | security | runtime_execution | output_validation |
| `security-003` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-008` | security | runtime_execution | output_validation |
| `security-009` | security | static_analysis | minimum_32_bytes |
| `security-010` | security | static_analysis | key_bits_256 |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-dma-001` | dma | static_heuristic | data_verified_after_transfer |
| `stm32-i2c-001` | spi-i2c | static_heuristic | i2c_address_left_shifted |
| `stm32-lowpower-001` | power-mgmt | static_heuristic | sysclock_reconfigured_after_stop_wakeup, led_toggled_after_wakeup, clock_restored_after_stop_wakeup |
| `stm32-spi-001` | spi-i2c | static_heuristic | cs_deasserted_after_transfer |
| `stm32-timer-001` | timer | static_heuristic | prescaler_arr_gives_1khz, duty_cycle_approximately_50pct, timer_clock_before_init |
| `stm32-uart-001` | networking | static_heuristic | receive_it_rearmed_in_callback, uart_clock_before_init |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-004` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, delete_after_commit |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-013` | storage | static_heuristic | handler_registered |
| `threading-001` | threading | static_heuristic | different_thread_priorities, queue_capacity_positive |
| `threading-002` | threading | runtime_execution | output_validation |
| `threading-006` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-010` | threading | static_analysis | k_sem_for_write_exclusion |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, consumer_waits_for_flag |
| `timer-001` | timer | runtime_execution | output_validation |
| `timer-007` | timer | static_heuristic | timer_period_less_than_wdt_timeout |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-004` | watchdog | static_analysis | separate_channel_ids, both_channels_fed |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `yocto-005` | yocto | static_heuristic | no_custom_do_compile |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |
| `yocto-014` | yocto | static_heuristic | no_make_test_in_install_ptest |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `output_validation` | 19 | isr-concurrency-002, isr-concurrency-008, memory-opt-003, memory-opt-007, memory-opt-011 (+14 more) |
| `west_build_docker` | 16 | ble-009, ble-010, gpio-basic-010, isr-concurrency-004, isr-concurrency-006 (+11 more) |
| `hardware_compatibility_list_nonempty` | 3 | ota-swupdate-001, ota-swupdate-002, ota-swupdate-004 |
| `bt_enable_before_scan` | 1 | ble-008 |
| `conn_unref_in_disconnected` | 1 | ble-008 |
| `discovery_after_connected` | 1 | ble-008 |
| `conn_cleanup_on_failed_connect` | 1 | ble-008 |
| `runtime_started` | 1 | dma-002 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `pre_invalidate_dst_before_dma` | 1 | dma-005 |
| `two_dma_config_calls` | 1 | dma-007 |
| `three_block_configs` | 1 | dma-011 |
| `single_dma_start` | 1 | dma-011 |
| `block_count_three` | 1 | dma-011 |
| `i2c_master_header` | 1 | esp-i2c-001 |
| `i2c_master_new_api` | 1 | esp-i2c-001 |
| `no_legacy_i2c_driver` | 1 | esp-i2c-001 |
| `ext0_wakeup_level_low` | 1 | esp-sleep-001 |
| `nvs_initialized_before_wifi` | 1 | esp-wifi-001 |
| `no_printk` | 1 | isr-concurrency-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `init_before_isr_call` | 1 | isr-concurrency-005 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `init_error_path_cleanup` | 1 | linux-driver-006 |
| `module_platform_driver_macro` | 1 | linux-driver-010 |
| `free_irq_before_cancel_work` | 1 | linux-driver-011 |
| `is_err_guards_reset_control_get` | 1 | linux-driver-016 |
| `nonzero_exit_on_error` | 1 | linux-userspace-001 |
| `config_thread_stack_info_enabled` | 1 | memory-opt-006 |
| `exit_cancels_work_then_purges_queue` | 1 | networking-kernel-002 |
| `input_cb_sends_netlink_unicast` | 1 | networking-kernel-003 |
| `genl_family_has_name_field` | 1 | networking-kernel-004 |
| `self_test_failure_branch` | 1 | ota-011 |
| `minimum_32_bytes` | 1 | security-009 |
| `key_bits_256` | 1 | security-010 |
| `data_verified_after_transfer` | 1 | stm32-dma-001 |
| `i2c_address_left_shifted` | 1 | stm32-i2c-001 |
| `sysclock_reconfigured_after_stop_wakeup` | 1 | stm32-lowpower-001 |
| `led_toggled_after_wakeup` | 1 | stm32-lowpower-001 |
| `clock_restored_after_stop_wakeup` | 1 | stm32-lowpower-001 |
| `cs_deasserted_after_transfer` | 1 | stm32-spi-001 |
| `prescaler_arr_gives_1khz` | 1 | stm32-timer-001 |
| `duty_cycle_approximately_50pct` | 1 | stm32-timer-001 |
| `timer_clock_before_init` | 1 | stm32-timer-001 |
| `receive_it_rearmed_in_callback` | 1 | stm32-uart-001 |
| `uart_clock_before_init` | 1 | stm32-uart-001 |
| `write_verify_commit_order` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `handler_registered` | 1 | storage-013 |
| `different_thread_priorities` | 1 | threading-001 |
| `queue_capacity_positive` | 1 | threading-001 |
| `k_sem_for_write_exclusion` | 1 | threading-010 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `timer_period_less_than_wdt_timeout` | 1 | timer-007 |
| `separate_channel_ids` | 1 | watchdog-004 |
| `both_channels_fed` | 1 | watchdog-004 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |
| `no_custom_do_compile` | 1 | yocto-005 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |
| `no_make_test_in_install_ptest` | 1 | yocto-014 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 75 | ble-008, ble-009, ble-010, dma-002, dma-004 (+70 more) |
| LLM format failure (prose) | 5 | ota-swupdate-001, ota-swupdate-004, yocto-005, yocto-007, yocto-014 |

*Adjusted pass@1 (excluding format failures): 71.4% (187/262)*


## TC Improvement Suggestions

