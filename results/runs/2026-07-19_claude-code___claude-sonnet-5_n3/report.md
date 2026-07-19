# Benchmark Report: claude-code://claude-sonnet-5

**Date:** 2026-07-19 12:25 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://claude-sonnet-5 |
| Total Cases | 263 |
| Passed | 177 |
| Failed | 86 |
| pass@1 | 67.3% |

## Failed Cases (86)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-008` | ble | static_heuristic | scan_stopped_before_connect |
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `dma-002` | dma | runtime_execution | runtime_started |
| `dma-003` | dma | static_analysis | cyclic_flag_set |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-005` | dma | static_heuristic | post_invalidate_dst_after_dma |
| `dma-007` | dma | static_analysis | two_dma_config_calls |
| `dma-009` | dma | static_heuristic | dma_start_called_twice |
| `dma-012` | dma | static_analysis | buffer_alignment |
| `esp-adc-001` | sensor-driver | static_heuristic | adc_read_error_checked |
| `esp-wifi-001` | networking | static_heuristic | nvs_initialized_before_wifi |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | static_analysis | no_printk |
| `isr-concurrency-002` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-005` | isr-concurrency | static_analysis | init_before_isr_call |
| `isr-concurrency-006` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | compile_gate | west_build_docker |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `kconfig-002` | kconfig | static_analysis | bt_hci_enabled |
| `kconfig-010` | kconfig | static_analysis | hw_cc3xx_enabled |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-009` | linux-driver | static_heuristic | isr_uses_spin_lock_irqsave |
| `linux-driver-011` | linux-driver | static_heuristic | free_irq_before_cancel_work |
| `linux-driver-013` | linux-driver | static_analysis | mod_devicetable_header_included |
| `linux-driver-016` | linux-driver | static_heuristic | is_err_guards_reset_control_get |
| `linux-userspace-001` | linux-userspace | static_heuristic | nonzero_exit_on_error |
| `linux-userspace-008` | linux-userspace | static_heuristic | comm_array_size_16_bytes |
| `memory-opt-001` | memory-opt | runtime_execution | output_validation |
| `memory-opt-003` | memory-opt | runtime_execution | output_validation |
| `memory-opt-006` | memory-opt | static_analysis | config_thread_stack_info_enabled |
| `memory-opt-007` | memory-opt | runtime_execution | output_validation |
| `memory-opt-011` | memory-opt | runtime_execution | output_validation |
| `memory-opt-012` | memory-opt | static_heuristic | no_large_string_literals |
| `networking-005` | networking | static_heuristic | request_timeout_set |
| `networking-009` | networking | compile_gate | west_build_docker |
| `networking-kernel-002` | networking | static_heuristic | producer_uses_skb_clone, skb_clone_uses_gfp_atomic, skb_clone_return_null_checked, exit_cancels_work_then_purges_queue |
| `networking-kernel-003` | networking | static_heuristic | input_cb_sends_netlink_unicast |
| `networking-kernel-004` | networking | static_analysis | skbuff_header_included |
| `ota-003` | ota | static_heuristic | done_after_write |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `ota-swupdate-001` | ota | static_heuristic | hardware_compatibility_list_nonempty |
| `ota-swupdate-002` | ota | static_heuristic | hardware_compatibility_list_nonempty, two_selection_groups_copy_1_copy_2, copy_1_has_three_images, copy_2_has_three_images, selection_groups_have_distinct_devices, all_image_entries_have_sha256 |
| `ota-swupdate-004` | ota | static_heuristic | hardware_compatibility_list_nonempty |
| `power-mgmt-009` | power-mgmt | static_heuristic | periodic_battery_check, multiple_sleep_depths |
| `power-mgmt-010` | power-mgmt | static_heuristic | state_get_return_checked |
| `security-001` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-007` | security | static_heuristic | error_path_returns_early |
| `security-008` | security | runtime_execution | output_validation |
| `sensor-driver-003` | sensor-driver | static_heuristic | error_handling |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-dma-001` | dma | static_heuristic | data_verified_after_transfer |
| `stm32-i2c-001` | spi-i2c | static_analysis | i2c_clock_enabled |
| `stm32-spi-001` | spi-i2c | static_heuristic | cs_asserted_before_transfer, spi_clock_before_init |
| `stm32-uart-001` | networking | static_heuristic | uart_clock_before_init |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-004` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-008` | storage | compile_gate | west_build_docker |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-013` | storage | static_heuristic | handler_registered |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-010` | threading | static_analysis | reader_count_variable |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `timer-001` | timer | static_heuristic | expiry_increments_counter, counter_is_volatile |
| `timer-007` | timer | static_heuristic | timer_period_less_than_wdt_timeout |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-004` | watchdog | static_heuristic | distinct_channel_timeouts |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `yocto-002` | yocto | static_analysis | lic_files_chksum, srcrev_defined |
| `yocto-003` | yocto | static_analysis | summary_defined, license_defined, inherit_systemd, systemd_service_var, service_in_src_uri, do_install_defined |
| `yocto-004` | yocto | static_analysis | depends_defined, rdepends_defined, do_install_defined |
| `yocto-005` | yocto | static_analysis | summary_defined, license_defined, inherit_module, src_uri_defined, kernel_module_autoload, lic_files_chksum |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `output_validation` | 17 | isr-concurrency-002, isr-concurrency-006, isr-concurrency-008, memory-opt-001, memory-opt-003 (+12 more) |
| `west_build_docker` | 14 | isr-concurrency-011, storage-008, threading-012, ble-009, ble-010 (+9 more) |
| `hardware_compatibility_list_nonempty` | 3 | ota-swupdate-001, ota-swupdate-002, ota-swupdate-004 |
| `lic_files_chksum` | 2 | yocto-002, yocto-005 |
| `summary_defined` | 2 | yocto-003, yocto-005 |
| `license_defined` | 2 | yocto-003, yocto-005 |
| `do_install_defined` | 2 | yocto-003, yocto-004 |
| `init_error_path_cleanup` | 1 | linux-driver-006 |
| `isr_uses_spin_lock_irqsave` | 1 | linux-driver-009 |
| `free_irq_before_cancel_work` | 1 | linux-driver-011 |
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
| `two_selection_groups_copy_1_copy_2` | 1 | ota-swupdate-002 |
| `copy_1_has_three_images` | 1 | ota-swupdate-002 |
| `copy_2_has_three_images` | 1 | ota-swupdate-002 |
| `selection_groups_have_distinct_devices` | 1 | ota-swupdate-002 |
| `all_image_entries_have_sha256` | 1 | ota-swupdate-002 |
| `srcrev_defined` | 1 | yocto-002 |
| `inherit_systemd` | 1 | yocto-003 |
| `systemd_service_var` | 1 | yocto-003 |
| `service_in_src_uri` | 1 | yocto-003 |
| `depends_defined` | 1 | yocto-004 |
| `rdepends_defined` | 1 | yocto-004 |
| `inherit_module` | 1 | yocto-005 |
| `src_uri_defined` | 1 | yocto-005 |
| `kernel_module_autoload` | 1 | yocto-005 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |
| `nvs_initialized_before_wifi` | 1 | esp-wifi-001 |
| `i2c_clock_enabled` | 1 | stm32-i2c-001 |
| `cs_asserted_before_transfer` | 1 | stm32-spi-001 |
| `spi_clock_before_init` | 1 | stm32-spi-001 |
| `uart_clock_before_init` | 1 | stm32-uart-001 |
| `scan_stopped_before_connect` | 1 | ble-008 |
| `runtime_started` | 1 | dma-002 |
| `cyclic_flag_set` | 1 | dma-003 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `post_invalidate_dst_after_dma` | 1 | dma-005 |
| `two_dma_config_calls` | 1 | dma-007 |
| `dma_start_called_twice` | 1 | dma-009 |
| `buffer_alignment` | 1 | dma-012 |
| `no_printk` | 1 | isr-concurrency-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `init_before_isr_call` | 1 | isr-concurrency-005 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `bt_hci_enabled` | 1 | kconfig-002 |
| `config_thread_stack_info_enabled` | 1 | memory-opt-006 |
| `no_large_string_literals` | 1 | memory-opt-012 |
| `request_timeout_set` | 1 | networking-005 |
| `done_after_write` | 1 | ota-003 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `self_test_failure_branch` | 1 | ota-011 |
| `error_path_returns_early` | 1 | security-007 |
| `error_handling` | 1 | sensor-driver-003 |
| `handler_registered` | 1 | storage-013 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `expiry_increments_counter` | 1 | timer-001 |
| `counter_is_volatile` | 1 | timer-001 |
| `timer_period_less_than_wdt_timeout` | 1 | timer-007 |
| `distinct_channel_timeouts` | 1 | watchdog-004 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `data_verified_after_transfer` | 1 | stm32-dma-001 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `multiple_sleep_depths` | 1 | power-mgmt-009 |
| `state_get_return_checked` | 1 | power-mgmt-010 |
| `reader_count_variable` | 1 | threading-010 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 78 | linux-driver-006, linux-driver-009, linux-driver-011, linux-driver-013, linux-driver-016 (+73 more) |
| LLM format failure (prose) | 8 | ota-swupdate-001, ota-swupdate-002, ota-swupdate-004, yocto-002, yocto-003, yocto-004, yocto-005, yocto-007 |

*Adjusted pass@1 (excluding format failures): 69.4% (177/255)*


## TC Improvement Suggestions

