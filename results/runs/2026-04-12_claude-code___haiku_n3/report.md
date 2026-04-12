# Benchmark Report: claude-code://haiku

**Date:** 2026-04-12 09:37 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 233 |
| Passed | 133 |
| Failed | 100 |
| pass@1 | 57.1% |

## Failed Cases (100)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `adc-002` | adc | static_heuristic | periodic_read_with_sleep |
| `ble-001` | ble | compile_gate | west_build_docker |
| `ble-003` | ble | compile_gate | west_build_docker |
| `ble-005` | ble | static_heuristic | security_set_in_connected_cb |
| `ble-008` | ble | static_heuristic | conn_cleanup_on_failed_connect |
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | static_analysis | bt_l2cap_chan_send_used |
| `dma-001` | dma | static_analysis | dma_config_called |
| `dma-002` | dma | runtime_execution | output_validation |
| `dma-003` | dma | static_analysis | dma_header_included, cyclic_flag_set, dma_reload_called, dma_config_and_start |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-005` | dma | static_analysis | dst_buffer_aligned |
| `dma-006` | dma | compile_gate | west_build_docker |
| `dma-007` | dma | static_analysis | channel_priority_field_used |
| `dma-008` | dma | compile_gate | west_build_docker |
| `dma-009` | dma | static_analysis | dma_header_included |
| `dma-010` | dma | static_analysis | atomic_buffer_index, dma_reload_called |
| `dma-012` | dma | static_analysis | cache_flush_before_dma |
| `esp-adc-001` | sensor-driver | static_heuristic | calibration_before_raw_to_voltage, adc_read_error_checked |
| `esp-i2c-001` | spi-i2c | static_heuristic | transmit_receive_used |
| `esp-ota-001` | ota | static_heuristic | rollback_on_failure |
| `esp-sleep-001` | power-mgmt | static_analysis | esp_sleep_header, app_main_defined, deep_sleep_used, gpio_wakeup_configured |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-001` | isr-concurrency | static_analysis | uses_atomic_operations, zephyr_headers_included |
| `isr-concurrency-002` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present |
| `isr-concurrency-005` | isr-concurrency | static_analysis | init_before_isr_call |
| `isr-concurrency-006` | isr-concurrency | static_analysis | fifo_reserved_field |
| `isr-concurrency-008` | isr-concurrency | static_heuristic | memory_barrier_present, barrier_between_data_and_index_update |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | compile_gate | west_build_docker |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `kconfig-003` | kconfig | static_analysis | uart_line_ctrl_enabled |
| `kconfig-005` | kconfig | static_analysis | net_sockets_sockopt_tls_enabled, tls_credentials_enabled, mbedtls_builtin_enabled |
| `kconfig-010` | kconfig | static_analysis | mbedtls_psa_crypto_enabled, hw_cc3xx_enabled |
| `linux-driver-005` | linux-driver | static_heuristic | sysfs_create_group_error_handled |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-009` | linux-driver | static_analysis | gpiod_set_value_used |
| `memory-opt-001` | memory-opt | static_analysis | mem_slab_defined, slab_alloc_called, slab_free_called |
| `memory-opt-002` | memory-opt | static_analysis | minimal_libc_enabled, newlib_not_enabled |
| `memory-opt-003` | memory-opt | static_analysis | slab_defined, slab_alloc_called, slab_free_called |
| `memory-opt-004` | memory-opt | static_analysis | thread_analyzer_header, thread_analyzer_config, thread_stack_defined, thread_analyzer_print_called |
| `memory-opt-005` | memory-opt | static_analysis | app_memdomain_header |
| `memory-opt-006` | memory-opt | static_analysis | config_thread_stack_info_enabled |
| `memory-opt-008` | memory-opt | static_analysis | cbprintf_nano_enabled, dynamic_thread_disabled |
| `memory-opt-012` | memory-opt | runtime_execution | output_validation |
| `networking-001` | networking | compile_gate | west_build_docker |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `ota-009` | ota | compile_gate | west_build_docker |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-002` | power-mgmt | static_heuristic | multiple_printk_calls |
| `power-mgmt-009` | power-mgmt | static_heuristic | battery_level_printed, periodic_battery_check, multiple_sleep_depths |
| `security-001` | security | compile_gate | west_build_docker |
| `security-004` | security | runtime_execution | output_validation |
| `security-008` | security | runtime_execution | output_validation |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-005` | spi-i2c | static_heuristic | found_count_reported |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-adc-001` | sensor-driver | static_analysis | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used, adc_started_with_dma, adc_12bit_resolution |
| `stm32-dma-001` | dma | static_analysis | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used, m2m_direction_configured, dma_start_it_used |
| `stm32-freertos-001` | threading | static_analysis | stm32_hal_header_included |
| `stm32-i2c-001` | spi-i2c | static_analysis | stm32_hal_header_included, i2c_handle_typedef_used, i2c1_instance_configured, hal_i2c_mem_read_used, i2c_clock_enabled |
| `stm32-lowpower-001` | power-mgmt | static_analysis | stm32_hal_header_included |
| `stm32-spi-001` | spi-i2c | static_analysis | stm32_hal_header_included, spi_handle_typedef_used, spi1_instance_configured, software_nss_used, spi_clock_enabled |
| `stm32-timer-001` | timer | static_analysis | stm32_hal_header_included, tim_handle_typedef_used, tim3_instance_used, pwm_start_called, timer_clock_enabled |
| `storage-001` | storage | runtime_execution | output_validation |
| `storage-002` | storage | runtime_execution | runtime_started |
| `storage-004` | storage | compile_gate | west_build_docker |
| `storage-005` | storage | compile_gate | west_build_docker |
| `storage-006` | storage | static_heuristic | success_printed |
| `storage-008` | storage | static_analysis | memcmp_verification |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-012` | storage | static_analysis | no_freertos_apis |
| `storage-013` | storage | static_analysis | flash_write_rate_limited |
| `threading-002` | threading | runtime_execution | runtime_started |
| `threading-006` | threading | runtime_execution | output_validation |
| `threading-007` | threading | static_heuristic | volatile_on_initialized_flag |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `threading-010` | threading | static_analysis | k_sem_for_write_exclusion |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-002` | timer | static_analysis | one_shot_period_no_wait |
| `timer-004` | timer | static_heuristic | main_waits_for_work |
| `timer-005` | timer | compile_gate | west_build_docker |
| `timer-008` | timer | compile_gate | west_build_docker |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-001` | watchdog | static_heuristic | install_before_setup |
| `watchdog-004` | watchdog | static_analysis | two_channels_installed, separate_channel_ids |
| `watchdog-007` | watchdog | static_heuristic | wdt_feed_after_flag_check |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `yocto-001` | yocto | static_analysis | summary_defined, license_defined, lic_files_chksum, src_uri_defined, do_install_defined |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |
| `yocto-009` | yocto | static_analysis | machine_features_defined, kernel_devicetree_defined, serial_consoles_defined, kernel_imagetype_defined |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 23 | ble-001, ble-003, dma-006, dma-008, isr-concurrency-011 (+18 more) |
| `output_validation` | 9 | dma-002, isr-concurrency-002, memory-opt-012, security-004, security-008 (+4 more) |
| `stm32_hal_header_included` | 7 | stm32-freertos-001, stm32-i2c-001, stm32-spi-001, stm32-adc-001, stm32-dma-001 (+2 more) |
| `dma_header_included` | 2 | dma-003, dma-009 |
| `dma_reload_called` | 2 | dma-003, dma-010 |
| `slab_alloc_called` | 2 | memory-opt-001, memory-opt-003 |
| `slab_free_called` | 2 | memory-opt-001, memory-opt-003 |
| `runtime_started` | 2 | storage-002, threading-002 |
| `dma_handle_typedef_used` | 2 | stm32-adc-001, stm32-dma-001 |
| `periodic_read_with_sleep` | 1 | adc-002 |
| `security_set_in_connected_cb` | 1 | ble-005 |
| `conn_cleanup_on_failed_connect` | 1 | ble-008 |
| `dma_config_called` | 1 | dma-001 |
| `cyclic_flag_set` | 1 | dma-003 |
| `dma_config_and_start` | 1 | dma-003 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `dst_buffer_aligned` | 1 | dma-005 |
| `channel_priority_field_used` | 1 | dma-007 |
| `cache_flush_before_dma` | 1 | dma-012 |
| `transmit_receive_used` | 1 | esp-i2c-001 |
| `uses_atomic_operations` | 1 | isr-concurrency-001 |
| `zephyr_headers_included` | 1 | isr-concurrency-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `init_before_isr_call` | 1 | isr-concurrency-005 |
| `fifo_reserved_field` | 1 | isr-concurrency-006 |
| `memory_barrier_present` | 1 | isr-concurrency-008 |
| `barrier_between_data_and_index_update` | 1 | isr-concurrency-008 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `uart_line_ctrl_enabled` | 1 | kconfig-003 |
| `net_sockets_sockopt_tls_enabled` | 1 | kconfig-005 |
| `tls_credentials_enabled` | 1 | kconfig-005 |
| `mbedtls_builtin_enabled` | 1 | kconfig-005 |
| `sysfs_create_group_error_handled` | 1 | linux-driver-005 |
| `init_error_path_cleanup` | 1 | linux-driver-006 |
| `mem_slab_defined` | 1 | memory-opt-001 |
| `minimal_libc_enabled` | 1 | memory-opt-002 |
| `newlib_not_enabled` | 1 | memory-opt-002 |
| `slab_defined` | 1 | memory-opt-003 |
| `thread_analyzer_header` | 1 | memory-opt-004 |
| `thread_analyzer_config` | 1 | memory-opt-004 |
| `thread_stack_defined` | 1 | memory-opt-004 |
| `thread_analyzer_print_called` | 1 | memory-opt-004 |
| `app_memdomain_header` | 1 | memory-opt-005 |
| `config_thread_stack_info_enabled` | 1 | memory-opt-006 |
| `cbprintf_nano_enabled` | 1 | memory-opt-008 |
| `dynamic_thread_disabled` | 1 | memory-opt-008 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `self_test_failure_branch` | 1 | ota-011 |
| `multiple_printk_calls` | 1 | power-mgmt-002 |
| `found_count_reported` | 1 | spi-i2c-005 |
| `i2c_handle_typedef_used` | 1 | stm32-i2c-001 |
| `i2c1_instance_configured` | 1 | stm32-i2c-001 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `i2c_clock_enabled` | 1 | stm32-i2c-001 |
| `spi_handle_typedef_used` | 1 | stm32-spi-001 |
| `spi1_instance_configured` | 1 | stm32-spi-001 |
| `software_nss_used` | 1 | stm32-spi-001 |
| `spi_clock_enabled` | 1 | stm32-spi-001 |
| `success_printed` | 1 | storage-006 |
| `memcmp_verification` | 1 | storage-008 |
| `no_freertos_apis` | 1 | storage-012 |
| `flash_write_rate_limited` | 1 | storage-013 |
| `volatile_on_initialized_flag` | 1 | threading-007 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `counter_is_volatile` | 1 | timer-001 |
| `one_shot_period_no_wait` | 1 | timer-002 |
| `main_waits_for_work` | 1 | timer-004 |
| `install_before_setup` | 1 | watchdog-001 |
| `two_channels_installed` | 1 | watchdog-004 |
| `separate_channel_ids` | 1 | watchdog-004 |
| `wdt_feed_after_flag_check` | 1 | watchdog-007 |
| `summary_defined` | 1 | yocto-001 |
| `license_defined` | 1 | yocto-001 |
| `lic_files_chksum` | 1 | yocto-001 |
| `src_uri_defined` | 1 | yocto-001 |
| `do_install_defined` | 1 | yocto-001 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |
| `bt_l2cap_chan_send_used` | 1 | ble-010 |
| `atomic_buffer_index` | 1 | dma-010 |
| `calibration_before_raw_to_voltage` | 1 | esp-adc-001 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `rollback_on_failure` | 1 | esp-ota-001 |
| `esp_sleep_header` | 1 | esp-sleep-001 |
| `app_main_defined` | 1 | esp-sleep-001 |
| `deep_sleep_used` | 1 | esp-sleep-001 |
| `gpio_wakeup_configured` | 1 | esp-sleep-001 |
| `mbedtls_psa_crypto_enabled` | 1 | kconfig-010 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `gpiod_set_value_used` | 1 | linux-driver-009 |
| `battery_level_printed` | 1 | power-mgmt-009 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `multiple_sleep_depths` | 1 | power-mgmt-009 |
| `adc_handle_typedef_used` | 1 | stm32-adc-001 |
| `adc_started_with_dma` | 1 | stm32-adc-001 |
| `adc_12bit_resolution` | 1 | stm32-adc-001 |
| `dma2_stream0_used` | 1 | stm32-dma-001 |
| `m2m_direction_configured` | 1 | stm32-dma-001 |
| `dma_start_it_used` | 1 | stm32-dma-001 |
| `tim_handle_typedef_used` | 1 | stm32-timer-001 |
| `tim3_instance_used` | 1 | stm32-timer-001 |
| `pwm_start_called` | 1 | stm32-timer-001 |
| `timer_clock_enabled` | 1 | stm32-timer-001 |
| `k_sem_for_write_exclusion` | 1 | threading-010 |
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
| Genuine code error | 91 | adc-002, ble-001, ble-003, ble-005, ble-008 (+86 more) |
| LLM format failure (prose) | 9 | stm32-i2c-001, stm32-spi-001, yocto-001, yocto-007, esp-sleep-001, stm32-adc-001, stm32-dma-001, stm32-timer-001, yocto-009 |

*Adjusted pass@1 (excluding format failures): 59.4% (133/224)*


## TC Improvement Suggestions

