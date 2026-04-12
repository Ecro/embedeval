# Benchmark Report: claude-code://haiku

**Date:** 2026-04-12 07:21 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 233 |
| Passed | 129 |
| Failed | 104 |
| pass@1 | 55.4% |

## Failed Cases (104)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `adc-002` | adc | static_heuristic | periodic_read_with_sleep |
| `ble-001` | ble | compile_gate | west_build_docker |
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | static_analysis | bt_l2cap_chan_send_used |
| `boot-001` | boot | static_analysis | mcuboot_enabled |
| `device-tree-003` | device-tree | static_heuristic | pwm_polarity_specified |
| `device-tree-010` | device-tree | static_heuristic | gpio_leds_compatible, gpio_keys_compatible |
| `dma-001` | dma | static_analysis | dma_config_called |
| `dma-002` | dma | static_analysis | dma_header_included, peripheral_to_memory_direction, dma_config_called |
| `dma-003` | dma | static_analysis | dma_header_included, dma_reload_called, dma_config_and_start |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-005` | dma | static_analysis | cache_header_included, cache_invalidate_present |
| `dma-006` | dma | static_analysis | dma_header_included |
| `dma-007` | dma | static_analysis | dma_header_included, channel_priority_field_used, two_dma_config_calls |
| `dma-008` | dma | compile_gate | west_build_docker |
| `dma-009` | dma | static_heuristic | dma_config_after_stop, dma_start_called_twice |
| `dma-010` | dma | static_analysis | dma_header_included, atomic_buffer_index, dma_reload_called |
| `dma-011` | dma | static_analysis | three_block_configs, block_count_three |
| `dma-012` | dma | static_analysis | cache_flush_before_dma |
| `esp-adc-001` | sensor-driver | static_heuristic | averaging_loop_present, adc_read_error_checked |
| `esp-ble-001` | ble | static_analysis | ble_header, app_main_defined, esp_bluedroid_init_called, gatts_app_register_called |
| `esp-i2c-001` | spi-i2c | static_analysis | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver |
| `esp-ota-001` | ota | static_heuristic | wifi_before_ota, rollback_on_failure, firmware_validation |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | static_analysis | no_kmalloc, no_floating_point, no_printk |
| `isr-concurrency-002` | isr-concurrency | static_analysis | k_msgq_used, k_no_wait_in_isr_put, no_kmalloc_in_isr |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-005` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-006` | isr-concurrency | static_analysis | fifo_reserved_field |
| `isr-concurrency-007` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-008` | isr-concurrency | static_heuristic | memory_barrier_present, barrier_between_data_and_index_update |
| `isr-concurrency-009` | isr-concurrency | static_analysis | signal_initialized |
| `isr-concurrency-010` | isr-concurrency | static_analysis | log_entry_struct_defined |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `kconfig-003` | kconfig | static_analysis | usb_cdc_acm_enabled |
| `kconfig-005` | kconfig | static_analysis | networking_enabled, net_sockets_sockopt_tls_enabled, mbedtls_builtin_enabled |
| `kconfig-010` | kconfig | static_analysis | mbedtls_psa_crypto_enabled, hw_cc3xx_enabled |
| `linux-driver-009` | linux-driver | static_analysis | gpio_direction_set |
| `memory-opt-001` | memory-opt | static_analysis | mem_slab_defined, slab_alloc_called, slab_free_called |
| `memory-opt-002` | memory-opt | static_analysis | minimal_libc_enabled |
| `memory-opt-003` | memory-opt | static_analysis | heap_alloc_called, heap_free_called |
| `memory-opt-004` | memory-opt | static_analysis | thread_analyzer_header, thread_analyzer_config, thread_analyzer_print_called |
| `memory-opt-005` | memory-opt | static_analysis | app_memdomain_header |
| `memory-opt-006` | memory-opt | static_analysis | config_thread_stack_info_enabled |
| `memory-opt-007` | memory-opt | static_heuristic | free_list_or_bitmap_tracking |
| `memory-opt-008` | memory-opt | static_analysis | dynamic_thread_disabled |
| `memory-opt-012` | memory-opt | static_analysis | no_lookup_table |
| `networking-001` | networking | compile_gate | west_build_docker |
| `networking-003` | networking | static_heuristic | exponential_backoff |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `ota-006` | ota | static_heuristic | dfu_done_false_on_mismatch |
| `ota-009` | ota | static_heuristic | full_version_reported |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-001` | power-mgmt | static_heuristic | pm_action_run_called |
| `power-mgmt-002` | power-mgmt | static_heuristic | multiple_printk_calls |
| `power-mgmt-009` | power-mgmt | compile_gate | west_build_docker |
| `security-001` | security | compile_gate | west_build_docker |
| `security-002` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-007` | security | static_heuristic | error_path_returns_early |
| `security-008` | security | compile_gate | west_build_docker |
| `security-009` | security | static_analysis | return_value_checked |
| `sensor-driver-003` | sensor-driver | static_heuristic | error_handling |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-001` | spi-i2c | static_heuristic | i2c_error_handling |
| `spi-i2c-004` | spi-i2c | static_heuristic | write_enable_before_write |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-adc-001` | sensor-driver | static_analysis | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used, adc_started_with_dma, adc_12bit_resolution |
| `stm32-dma-001` | dma | static_analysis | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used, m2m_direction_configured, dma_start_it_used |
| `stm32-freertos-001` | threading | static_heuristic | different_task_priorities |
| `stm32-gpio-001` | gpio-basic | static_analysis | stm32_hal_header_included, gpio_init_typedef_used, hal_gpio_init_called, gpio_clock_enabled, nvic_configured |
| `stm32-i2c-001` | spi-i2c | static_analysis | stm32_hal_header_included, i2c_handle_typedef_used, i2c1_instance_configured, hal_i2c_mem_read_used, i2c_clock_enabled |
| `stm32-lowpower-001` | power-mgmt | static_analysis | stm32_hal_header_included, stop_mode_api_used, rtc_handle_typedef_used, rtc_alarm_interrupt_used, no_cross_platform_hallucination, wfi_entry_mode_specified |
| `stm32-uart-001` | networking | static_analysis | stm32_hal_header_included, uart_handle_typedef_used, interrupt_receive_used, usart2_instance_configured, uart_clock_enabled |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-005` | storage | compile_gate | west_build_docker |
| `storage-006` | storage | static_heuristic | success_printed |
| `storage-008` | storage | static_analysis | memcmp_verification |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-012` | storage | static_heuristic | write_rate_limited |
| `storage-013` | storage | compile_gate | west_build_docker |
| `threading-001` | threading | compile_gate | west_build_docker |
| `threading-004` | threading | compile_gate | west_build_docker |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-004` | timer | static_heuristic | main_waits_for_work |
| `timer-006` | timer | static_heuristic | alarm_value_is_volatile |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-001` | watchdog | static_analysis | wdt_install_timeout_called |
| `watchdog-003` | watchdog | static_heuristic | install_before_setup |
| `watchdog-004` | watchdog | static_heuristic | install_before_setup |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `watchdog-010` | watchdog | static_analysis | no_freertos_contamination, printk_present |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |
| `yocto-009` | yocto | static_analysis | machine_features_defined, kernel_devicetree_defined, serial_consoles_defined, kernel_imagetype_defined |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 21 | ble-001, dma-008, isr-concurrency-007, networking-001, security-001 (+16 more) |
| `output_validation` | 8 | isr-concurrency-005, isr-concurrency-011, security-002, security-004, storage-002 (+3 more) |
| `stm32_hal_header_included` | 6 | stm32-gpio-001, stm32-i2c-001, stm32-uart-001, stm32-adc-001, stm32-dma-001 (+1 more) |
| `dma_header_included` | 5 | dma-002, dma-003, dma-006, dma-007, dma-010 |
| `dma_config_called` | 2 | dma-001, dma-002 |
| `dma_reload_called` | 2 | dma-003, dma-010 |
| `install_before_setup` | 2 | watchdog-003, watchdog-004 |
| `dma_handle_typedef_used` | 2 | stm32-adc-001, stm32-dma-001 |
| `periodic_read_with_sleep` | 1 | adc-002 |
| `mcuboot_enabled` | 1 | boot-001 |
| `pwm_polarity_specified` | 1 | device-tree-003 |
| `peripheral_to_memory_direction` | 1 | dma-002 |
| `dma_config_and_start` | 1 | dma-003 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `cache_header_included` | 1 | dma-005 |
| `cache_invalidate_present` | 1 | dma-005 |
| `channel_priority_field_used` | 1 | dma-007 |
| `two_dma_config_calls` | 1 | dma-007 |
| `dma_config_after_stop` | 1 | dma-009 |
| `dma_start_called_twice` | 1 | dma-009 |
| `three_block_configs` | 1 | dma-011 |
| `block_count_three` | 1 | dma-011 |
| `cache_flush_before_dma` | 1 | dma-012 |
| `i2c_master_header` | 1 | esp-i2c-001 |
| `i2c_master_new_api` | 1 | esp-i2c-001 |
| `no_legacy_i2c_driver` | 1 | esp-i2c-001 |
| `no_kmalloc` | 1 | isr-concurrency-001 |
| `no_floating_point` | 1 | isr-concurrency-001 |
| `no_printk` | 1 | isr-concurrency-001 |
| `k_msgq_used` | 1 | isr-concurrency-002 |
| `k_no_wait_in_isr_put` | 1 | isr-concurrency-002 |
| `no_kmalloc_in_isr` | 1 | isr-concurrency-002 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `fifo_reserved_field` | 1 | isr-concurrency-006 |
| `memory_barrier_present` | 1 | isr-concurrency-008 |
| `barrier_between_data_and_index_update` | 1 | isr-concurrency-008 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `usb_cdc_acm_enabled` | 1 | kconfig-003 |
| `networking_enabled` | 1 | kconfig-005 |
| `net_sockets_sockopt_tls_enabled` | 1 | kconfig-005 |
| `mbedtls_builtin_enabled` | 1 | kconfig-005 |
| `mem_slab_defined` | 1 | memory-opt-001 |
| `slab_alloc_called` | 1 | memory-opt-001 |
| `slab_free_called` | 1 | memory-opt-001 |
| `minimal_libc_enabled` | 1 | memory-opt-002 |
| `heap_alloc_called` | 1 | memory-opt-003 |
| `heap_free_called` | 1 | memory-opt-003 |
| `thread_analyzer_header` | 1 | memory-opt-004 |
| `thread_analyzer_config` | 1 | memory-opt-004 |
| `thread_analyzer_print_called` | 1 | memory-opt-004 |
| `app_memdomain_header` | 1 | memory-opt-005 |
| `config_thread_stack_info_enabled` | 1 | memory-opt-006 |
| `free_list_or_bitmap_tracking` | 1 | memory-opt-007 |
| `dynamic_thread_disabled` | 1 | memory-opt-008 |
| `no_lookup_table` | 1 | memory-opt-012 |
| `exponential_backoff` | 1 | networking-003 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `dfu_done_false_on_mismatch` | 1 | ota-006 |
| `self_test_failure_branch` | 1 | ota-011 |
| `pm_action_run_called` | 1 | power-mgmt-001 |
| `multiple_printk_calls` | 1 | power-mgmt-002 |
| `error_path_returns_early` | 1 | security-007 |
| `error_handling` | 1 | sensor-driver-003 |
| `i2c_error_handling` | 1 | spi-i2c-001 |
| `write_enable_before_write` | 1 | spi-i2c-004 |
| `different_task_priorities` | 1 | stm32-freertos-001 |
| `gpio_init_typedef_used` | 1 | stm32-gpio-001 |
| `hal_gpio_init_called` | 1 | stm32-gpio-001 |
| `gpio_clock_enabled` | 1 | stm32-gpio-001 |
| `nvic_configured` | 1 | stm32-gpio-001 |
| `i2c_handle_typedef_used` | 1 | stm32-i2c-001 |
| `i2c1_instance_configured` | 1 | stm32-i2c-001 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `i2c_clock_enabled` | 1 | stm32-i2c-001 |
| `uart_handle_typedef_used` | 1 | stm32-uart-001 |
| `interrupt_receive_used` | 1 | stm32-uart-001 |
| `usart2_instance_configured` | 1 | stm32-uart-001 |
| `uart_clock_enabled` | 1 | stm32-uart-001 |
| `success_printed` | 1 | storage-006 |
| `memcmp_verification` | 1 | storage-008 |
| `write_rate_limited` | 1 | storage-012 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `counter_is_volatile` | 1 | timer-001 |
| `main_waits_for_work` | 1 | timer-004 |
| `alarm_value_is_volatile` | 1 | timer-006 |
| `wdt_install_timeout_called` | 1 | watchdog-001 |
| `no_freertos_contamination` | 1 | watchdog-010 |
| `printk_present` | 1 | watchdog-010 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |
| `bt_l2cap_chan_send_used` | 1 | ble-010 |
| `gpio_leds_compatible` | 1 | device-tree-010 |
| `gpio_keys_compatible` | 1 | device-tree-010 |
| `atomic_buffer_index` | 1 | dma-010 |
| `averaging_loop_present` | 1 | esp-adc-001 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `ble_header` | 1 | esp-ble-001 |
| `app_main_defined` | 1 | esp-ble-001 |
| `esp_bluedroid_init_called` | 1 | esp-ble-001 |
| `gatts_app_register_called` | 1 | esp-ble-001 |
| `wifi_before_ota` | 1 | esp-ota-001 |
| `rollback_on_failure` | 1 | esp-ota-001 |
| `firmware_validation` | 1 | esp-ota-001 |
| `signal_initialized` | 1 | isr-concurrency-009 |
| `log_entry_struct_defined` | 1 | isr-concurrency-010 |
| `mbedtls_psa_crypto_enabled` | 1 | kconfig-010 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `gpio_direction_set` | 1 | linux-driver-009 |
| `full_version_reported` | 1 | ota-009 |
| `return_value_checked` | 1 | security-009 |
| `adc_handle_typedef_used` | 1 | stm32-adc-001 |
| `adc_started_with_dma` | 1 | stm32-adc-001 |
| `adc_12bit_resolution` | 1 | stm32-adc-001 |
| `dma2_stream0_used` | 1 | stm32-dma-001 |
| `m2m_direction_configured` | 1 | stm32-dma-001 |
| `dma_start_it_used` | 1 | stm32-dma-001 |
| `stop_mode_api_used` | 1 | stm32-lowpower-001 |
| `rtc_handle_typedef_used` | 1 | stm32-lowpower-001 |
| `rtc_alarm_interrupt_used` | 1 | stm32-lowpower-001 |
| `no_cross_platform_hallucination` | 1 | stm32-lowpower-001 |
| `wfi_entry_mode_specified` | 1 | stm32-lowpower-001 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |
| `machine_features_defined` | 1 | yocto-009 |
| `kernel_devicetree_defined` | 1 | yocto-009 |
| `serial_consoles_defined` | 1 | yocto-009 |
| `kernel_imagetype_defined` | 1 | yocto-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 96 | adc-002, ble-001, boot-001, device-tree-003, dma-001 (+91 more) |
| LLM format failure (prose) | 8 | stm32-gpio-001, stm32-i2c-001, stm32-uart-001, yocto-007, esp-ble-001, stm32-adc-001, stm32-dma-001, yocto-009 |

*Adjusted pass@1 (excluding format failures): 57.3% (129/225)*


## TC Improvement Suggestions

