# Benchmark Report: claude-code://haiku

**Date:** 2026-04-12 05:14 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 233 |
| Passed | 136 |
| Failed | 97 |
| pass@1 | 58.4% |

## Failed Cases (97)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `adc-002` | adc | static_heuristic | periodic_read_with_sleep |
| `ble-001` | ble | compile_gate | west_build_docker |
| `ble-008` | ble | static_heuristic | conn_cleanup_on_failed_connect |
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | static_analysis | bt_l2cap_chan_send_used |
| `device-tree-001` | device-tree | static_heuristic | interrupt_gpio_present |
| `dma-001` | dma | static_analysis | dma_config_called |
| `dma-002` | dma | compile_gate | west_build_docker |
| `dma-003` | dma | static_analysis | dma_header_included, cyclic_flag_set, dma_reload_called, dma_config_and_start |
| `dma-004` | dma | static_analysis | block_count_set |
| `dma-005` | dma | compile_gate | west_build_docker |
| `dma-006` | dma | runtime_execution | output_validation |
| `dma-007` | dma | static_analysis | two_dma_config_calls |
| `dma-008` | dma | compile_gate | west_build_docker |
| `dma-009` | dma | static_analysis | no_freertos_contamination, no_arduino_contamination |
| `dma-010` | dma | static_analysis | dma_header_included, dma_reload_called |
| `dma-011` | dma | static_analysis | single_dma_start |
| `dma-012` | dma | static_analysis | dma_header_included, buffer_alignment |
| `esp-adc-001` | sensor-driver | static_heuristic | averaging_loop_present, adc_read_error_checked |
| `esp-ble-001` | ble | static_analysis | ble_header, app_main_defined, esp_bluedroid_init_called, gatts_app_register_called, no_zephyr_bt_apis |
| `esp-i2c-001` | spi-i2c | static_analysis | i2c_master_header, app_main_defined, i2c_master_new_api |
| `esp-ota-001` | ota | static_heuristic | rollback_on_failure, firmware_validation |
| `esp-sleep-001` | power-mgmt | static_analysis | deep_sleep_used |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | static_analysis | zephyr_headers_included |
| `isr-concurrency-002` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | no_forbidden_apis_in_isr |
| `isr-concurrency-004` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-005` | isr-concurrency | static_analysis | k_work_submit_called, init_before_isr_call |
| `isr-concurrency-006` | isr-concurrency | static_analysis | fifo_reserved_field |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-009` | isr-concurrency | static_analysis | k_poll_signal_declared, signal_initialized, k_poll_signal_raise_in_isr |
| `isr-concurrency-010` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-012` | isr-concurrency | static_analysis | no_isr_unsafe_primitives |
| `kconfig-005` | kconfig | static_analysis | tls_credentials_enabled |
| `kconfig-010` | kconfig | static_analysis | mbedtls_psa_crypto_enabled, hw_cc3xx_enabled |
| `linux-driver-001` | linux-driver | static_heuristic | init_error_path_cleanup, init_cleanup_no_comments |
| `linux-driver-009` | linux-driver | static_analysis | gpio_direction_set |
| `memory-opt-001` | memory-opt | static_analysis | mem_slab_defined, slab_alloc_called, slab_free_called |
| `memory-opt-002` | memory-opt | static_heuristic | minimal_libc_enabled_value |
| `memory-opt-003` | memory-opt | static_analysis | heap_defined, heap_alloc_called, heap_free_called |
| `memory-opt-004` | memory-opt | static_analysis | thread_analyzer_header, thread_analyzer_config, thread_analyzer_print_called |
| `memory-opt-005` | memory-opt | static_analysis | app_memdomain_header |
| `memory-opt-008` | memory-opt | static_analysis | dynamic_thread_disabled |
| `memory-opt-012` | memory-opt | static_analysis | no_stdio |
| `networking-003` | networking | compile_gate | west_build_docker |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-002` | power-mgmt | static_heuristic | multiple_printk_calls |
| `power-mgmt-005` | power-mgmt | static_analysis | pm_action_run_called |
| `power-mgmt-009` | power-mgmt | compile_gate | west_build_docker |
| `pwm-001` | pwm | static_heuristic | infinite_loop_present |
| `security-001` | security | compile_gate | west_build_docker |
| `security-004` | security | runtime_execution | output_validation |
| `security-008` | security | compile_gate | west_build_docker |
| `sensor-driver-003` | sensor-driver | static_heuristic | error_handling |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-005` | spi-i2c | static_heuristic | found_count_reported |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-dma-001` | dma | static_analysis | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used, m2m_direction_configured, dma_start_it_used |
| `stm32-freertos-001` | threading | static_analysis | stm32_hal_header_included |
| `stm32-gpio-001` | gpio-basic | static_analysis | stm32_hal_header_included, gpio_init_typedef_used, hal_gpio_init_called, gpio_clock_enabled, nvic_configured |
| `stm32-i2c-001` | spi-i2c | static_analysis | stm32_hal_header_included, i2c_handle_typedef_used, i2c1_instance_configured, hal_i2c_mem_read_used, i2c_clock_enabled |
| `stm32-lowpower-001` | power-mgmt | static_analysis | stm32_hal_header_included, stop_mode_api_used, rtc_handle_typedef_used, rtc_alarm_interrupt_used, wfi_entry_mode_specified |
| `stm32-spi-001` | spi-i2c | static_analysis | stm32_hal_header_included, spi_handle_typedef_used, spi1_instance_configured, software_nss_used, spi_clock_enabled |
| `stm32-uart-001` | networking | static_analysis | stm32_hal_header_included, uart_handle_typedef_used, interrupt_receive_used, usart2_instance_configured, uart_clock_enabled |
| `storage-001` | storage | runtime_execution | output_validation |
| `storage-002` | storage | compile_gate | west_build_docker |
| `storage-005` | storage | compile_gate | west_build_docker |
| `storage-006` | storage | static_heuristic | success_printed |
| `storage-008` | storage | static_analysis | memcmp_verification |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-010` | storage | compile_gate | west_build_docker |
| `storage-012` | storage | static_analysis | no_stdio_h |
| `storage-013` | storage | compile_gate | west_build_docker |
| `threading-005` | threading | compile_gate | west_build_docker |
| `threading-006` | threading | static_heuristic | lock_order_a_before_b, unlock_order_b_before_a |
| `threading-007` | threading | static_heuristic | volatile_on_initialized_flag |
| `threading-008` | threading | compile_gate | west_build_docker |
| `threading-010` | threading | static_heuristic | first_reader_blocks_writer, last_reader_unblocks_writer, reader_count_protected |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-004` | timer | static_heuristic | main_waits_for_work |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-006` | watchdog | static_analysis | wdt_install_and_setup |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `yocto-001` | yocto | static_analysis | summary_defined, license_defined, lic_files_chksum, src_uri_defined, do_install_defined |
| `yocto-005` | yocto | static_analysis | summary_defined, inherit_module, src_uri_defined, kernel_module_autoload, lic_files_chksum |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 25 | ble-001, dma-002, dma-005, dma-008, networking-003 (+20 more) |
| `output_validation` | 9 | dma-006, isr-concurrency-002, isr-concurrency-004, isr-concurrency-008, isr-concurrency-011 (+4 more) |
| `stm32_hal_header_included` | 7 | stm32-freertos-001, stm32-gpio-001, stm32-i2c-001, stm32-spi-001, stm32-uart-001 (+2 more) |
| `dma_header_included` | 3 | dma-003, dma-012, dma-010 |
| `dma_reload_called` | 2 | dma-003, dma-010 |
| `app_main_defined` | 2 | esp-i2c-001, esp-ble-001 |
| `summary_defined` | 2 | yocto-001, yocto-005 |
| `lic_files_chksum` | 2 | yocto-001, yocto-005 |
| `src_uri_defined` | 2 | yocto-001, yocto-005 |
| `periodic_read_with_sleep` | 1 | adc-002 |
| `conn_cleanup_on_failed_connect` | 1 | ble-008 |
| `interrupt_gpio_present` | 1 | device-tree-001 |
| `dma_config_called` | 1 | dma-001 |
| `cyclic_flag_set` | 1 | dma-003 |
| `dma_config_and_start` | 1 | dma-003 |
| `block_count_set` | 1 | dma-004 |
| `two_dma_config_calls` | 1 | dma-007 |
| `no_freertos_contamination` | 1 | dma-009 |
| `no_arduino_contamination` | 1 | dma-009 |
| `single_dma_start` | 1 | dma-011 |
| `buffer_alignment` | 1 | dma-012 |
| `i2c_master_header` | 1 | esp-i2c-001 |
| `i2c_master_new_api` | 1 | esp-i2c-001 |
| `zephyr_headers_included` | 1 | isr-concurrency-001 |
| `no_forbidden_apis_in_isr` | 1 | isr-concurrency-003 |
| `k_work_submit_called` | 1 | isr-concurrency-005 |
| `init_before_isr_call` | 1 | isr-concurrency-005 |
| `fifo_reserved_field` | 1 | isr-concurrency-006 |
| `no_isr_unsafe_primitives` | 1 | isr-concurrency-012 |
| `tls_credentials_enabled` | 1 | kconfig-005 |
| `init_error_path_cleanup` | 1 | linux-driver-001 |
| `init_cleanup_no_comments` | 1 | linux-driver-001 |
| `mem_slab_defined` | 1 | memory-opt-001 |
| `slab_alloc_called` | 1 | memory-opt-001 |
| `slab_free_called` | 1 | memory-opt-001 |
| `minimal_libc_enabled_value` | 1 | memory-opt-002 |
| `heap_defined` | 1 | memory-opt-003 |
| `heap_alloc_called` | 1 | memory-opt-003 |
| `heap_free_called` | 1 | memory-opt-003 |
| `thread_analyzer_header` | 1 | memory-opt-004 |
| `thread_analyzer_config` | 1 | memory-opt-004 |
| `thread_analyzer_print_called` | 1 | memory-opt-004 |
| `app_memdomain_header` | 1 | memory-opt-005 |
| `dynamic_thread_disabled` | 1 | memory-opt-008 |
| `no_stdio` | 1 | memory-opt-012 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `self_test_failure_branch` | 1 | ota-011 |
| `multiple_printk_calls` | 1 | power-mgmt-002 |
| `pm_action_run_called` | 1 | power-mgmt-005 |
| `infinite_loop_present` | 1 | pwm-001 |
| `error_handling` | 1 | sensor-driver-003 |
| `found_count_reported` | 1 | spi-i2c-005 |
| `gpio_init_typedef_used` | 1 | stm32-gpio-001 |
| `hal_gpio_init_called` | 1 | stm32-gpio-001 |
| `gpio_clock_enabled` | 1 | stm32-gpio-001 |
| `nvic_configured` | 1 | stm32-gpio-001 |
| `i2c_handle_typedef_used` | 1 | stm32-i2c-001 |
| `i2c1_instance_configured` | 1 | stm32-i2c-001 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `i2c_clock_enabled` | 1 | stm32-i2c-001 |
| `spi_handle_typedef_used` | 1 | stm32-spi-001 |
| `spi1_instance_configured` | 1 | stm32-spi-001 |
| `software_nss_used` | 1 | stm32-spi-001 |
| `spi_clock_enabled` | 1 | stm32-spi-001 |
| `uart_handle_typedef_used` | 1 | stm32-uart-001 |
| `interrupt_receive_used` | 1 | stm32-uart-001 |
| `usart2_instance_configured` | 1 | stm32-uart-001 |
| `uart_clock_enabled` | 1 | stm32-uart-001 |
| `success_printed` | 1 | storage-006 |
| `memcmp_verification` | 1 | storage-008 |
| `no_stdio_h` | 1 | storage-012 |
| `lock_order_a_before_b` | 1 | threading-006 |
| `unlock_order_b_before_a` | 1 | threading-006 |
| `volatile_on_initialized_flag` | 1 | threading-007 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `counter_is_volatile` | 1 | timer-001 |
| `main_waits_for_work` | 1 | timer-004 |
| `wdt_install_and_setup` | 1 | watchdog-006 |
| `license_defined` | 1 | yocto-001 |
| `do_install_defined` | 1 | yocto-001 |
| `inherit_module` | 1 | yocto-005 |
| `kernel_module_autoload` | 1 | yocto-005 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |
| `bt_l2cap_chan_send_used` | 1 | ble-010 |
| `averaging_loop_present` | 1 | esp-adc-001 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `ble_header` | 1 | esp-ble-001 |
| `esp_bluedroid_init_called` | 1 | esp-ble-001 |
| `gatts_app_register_called` | 1 | esp-ble-001 |
| `no_zephyr_bt_apis` | 1 | esp-ble-001 |
| `rollback_on_failure` | 1 | esp-ota-001 |
| `firmware_validation` | 1 | esp-ota-001 |
| `deep_sleep_used` | 1 | esp-sleep-001 |
| `k_poll_signal_declared` | 1 | isr-concurrency-009 |
| `signal_initialized` | 1 | isr-concurrency-009 |
| `k_poll_signal_raise_in_isr` | 1 | isr-concurrency-009 |
| `mbedtls_psa_crypto_enabled` | 1 | kconfig-010 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `gpio_direction_set` | 1 | linux-driver-009 |
| `dma_handle_typedef_used` | 1 | stm32-dma-001 |
| `dma2_stream0_used` | 1 | stm32-dma-001 |
| `m2m_direction_configured` | 1 | stm32-dma-001 |
| `dma_start_it_used` | 1 | stm32-dma-001 |
| `stop_mode_api_used` | 1 | stm32-lowpower-001 |
| `rtc_handle_typedef_used` | 1 | stm32-lowpower-001 |
| `rtc_alarm_interrupt_used` | 1 | stm32-lowpower-001 |
| `wfi_entry_mode_specified` | 1 | stm32-lowpower-001 |
| `first_reader_blocks_writer` | 1 | threading-010 |
| `last_reader_unblocks_writer` | 1 | threading-010 |
| `reader_count_protected` | 1 | threading-010 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 87 | adc-002, ble-001, ble-008, device-tree-001, dma-001 (+82 more) |
| LLM format failure (prose) | 10 | esp-i2c-001, isr-concurrency-001, stm32-gpio-001, stm32-i2c-001, stm32-spi-001, stm32-uart-001, yocto-001, yocto-007, stm32-dma-001, stm32-lowpower-001 |

*Adjusted pass@1 (excluding format failures): 61.0% (136/223)*


## TC Improvement Suggestions

