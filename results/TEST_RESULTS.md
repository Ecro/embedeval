# EmbedEval Test Results

*Last updated: 2026-04-12 22:09 UTC*

## Summary

| Model | Cases | Passed | Failed | pass@1 | Retest |
|-------|-------|--------|--------|--------|--------|
| claude-code://haiku | 233 | 133 | 100 | 57.1% | - |
| claude-code://sonnet | 239 | 163 | 76 | 68.2% | - |
| mock | 8 | 0 | 8 | 0.0% | - |

## claude-code://haiku

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 1 | 50% | periodic_read_with_sleep |
| ble | 10 | 4 | 40% | west_build_docker, west_build_docker, security_set_in_connected_cb, conn_cleanup_on_failed_connect, west_build_docker (+1) |
| boot | 10 | 10 | 100% | - |
| device-tree | 10 | 10 | 100% | - |
| dma | 12 | 1 | 8% | dma_config_called, output_validation, dma_header_included, cyclic_flag_set, dma_reload_called (+9) |
| esp-adc | 1 | 0 | 0% | calibration_before_raw_to_voltage, adc_read_error_checked |
| esp-ble | 1 | 1 | 100% | - |
| esp-gpio | 1 | 1 | 100% | - |
| esp-i2c | 1 | 0 | 0% | transmit_receive_used |
| esp-nvs | 1 | 1 | 100% | - |
| esp-ota | 1 | 0 | 0% | rollback_on_failure |
| esp-sleep | 1 | 0 | 0% | esp_sleep_header, app_main_defined, deep_sleep_used |
| esp-spi | 1 | 1 | 100% | - |
| esp-timer | 1 | 1 | 100% | - |
| esp-wifi | 1 | 1 | 100% | - |
| gpio-basic | 4 | 3 | 75% | west_build_docker |
| isr-concurrency | 12 | 4 | 33% | uses_atomic_operations, zephyr_headers_included, output_validation, k_sleep_present, init_before_isr_call (+5) |
| kconfig | 10 | 6 | 60% | spi_dma_enabled, uart_line_ctrl_enabled, net_sockets_sockopt_tls_enabled, tls_credentials_enabled, mbedtls_builtin_enabled (+2) |
| linux-driver | 10 | 7 | 70% | sysfs_create_group_error_handled, init_error_path_cleanup, gpiod_set_value_used |
| memory-opt | 12 | 4 | 33% | mem_slab_defined, slab_alloc_called, slab_free_called, minimal_libc_enabled, newlib_not_enabled (+11) |
| networking | 10 | 7 | 70% | west_build_docker, connect_error_handling, west_build_docker |
| ota | 11 | 7 | 64% | rollback_abort_on_download_error, rollback_on_error, west_build_docker, west_build_docker, self_test_failure_branch |
| power-mgmt | 10 | 8 | 80% | multiple_printk_calls, battery_level_printed, periodic_battery_check, multiple_sleep_depths |
| pwm | 1 | 1 | 100% | - |
| security | 10 | 7 | 70% | west_build_docker, output_validation, output_validation |
| sensor-driver | 10 | 8 | 80% | west_build_docker, west_build_docker |
| spi-i2c | 10 | 8 | 80% | found_count_reported, west_build_docker |
| stm32-adc | 1 | 0 | 0% | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used |
| stm32-dma | 1 | 0 | 0% | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used |
| stm32-freertos | 2 | 1 | 50% | stm32_hal_header_included |
| stm32-gpio | 1 | 1 | 100% | - |
| stm32-i2c | 1 | 0 | 0% | stm32_hal_header_included, i2c_handle_typedef_used, i2c1_instance_configured |
| stm32-lowpower | 1 | 0 | 0% | stm32_hal_header_included |
| stm32-spi | 1 | 0 | 0% | stm32_hal_header_included, spi_handle_typedef_used, spi1_instance_configured |
| stm32-timer | 1 | 0 | 0% | stm32_hal_header_included, tim_handle_typedef_used, tim3_instance_used |
| stm32-uart | 1 | 1 | 100% | - |
| storage | 12 | 3 | 25% | output_validation, runtime_started, west_build_docker, west_build_docker, success_printed (+4) |
| threading | 14 | 5 | 36% | runtime_started, output_validation, volatile_on_initialized_flag, deadline_constant_not_magic, k_sem_for_write_exclusion (+6) |
| timer | 10 | 5 | 50% | counter_is_volatile, one_shot_period_no_wait, main_waits_for_work, west_build_docker, west_build_docker |
| uart | 3 | 2 | 67% | west_build_docker |
| watchdog | 10 | 6 | 60% | install_before_setup, two_channels_installed, separate_channel_ids, wdt_feed_after_flag_check, window_min_greater_than_zero (+2) |
| yocto | 10 | 7 | 70% | summary_defined, license_defined, lic_files_chksum, rootfs_size_uses_weak_assignment, machine_features_defined (+2) |

### Failed Cases (100)

| Case | Layer | Failed Checks | Tested |
|------|-------|---------------|--------|
| adc-002 | L3 | periodic_read_with_sleep | 2026-04-12 |
| ble-001 | L1 | west_build_docker | 2026-04-12 |
| ble-003 | L1 | west_build_docker | 2026-04-12 |
| ble-005 | L3 | security_set_in_connected_cb | 2026-04-12 |
| ble-008 | L3 | conn_cleanup_on_failed_connect | 2026-04-12 |
| ble-009 | L1 | west_build_docker | 2026-04-12 |
| ble-010 | L0 | bt_l2cap_chan_send_used | 2026-04-12 |
| dma-001 | L0 | dma_config_called | 2026-04-12 |
| dma-002 | L2 | output_validation | 2026-04-12 |
| dma-003 | L0 | dma_header_included, cyclic_flag_set, dma_reload_called, dma_config_and_start | 2026-04-12 |
| dma-004 | L0 | multiple_block_descriptors | 2026-04-12 |
| dma-005 | L0 | dst_buffer_aligned | 2026-04-12 |
| dma-006 | L1 | west_build_docker | 2026-04-12 |
| dma-007 | L0 | channel_priority_field_used | 2026-04-12 |
| dma-008 | L1 | west_build_docker | 2026-04-12 |
| dma-009 | L0 | dma_header_included | 2026-04-12 |
| dma-010 | L0 | atomic_buffer_index, dma_reload_called | 2026-04-12 |
| dma-012 | L0 | cache_flush_before_dma | 2026-04-12 |
| esp-adc-001 | L3 | calibration_before_raw_to_voltage, adc_read_error_checked | 2026-04-12 |
| esp-i2c-001 | L3 | transmit_receive_used | 2026-04-12 |
| esp-ota-001 | L3 | rollback_on_failure | 2026-04-12 |
| esp-sleep-001 | L0 | esp_sleep_header, app_main_defined, deep_sleep_used, gpio_wakeup_configured | 2026-04-12 |
| gpio-basic-010 | L1 | west_build_docker | 2026-04-12 |
| isr-concurrency-001 | L0 | uses_atomic_operations, zephyr_headers_included | 2026-04-12 |
| isr-concurrency-002 | L2 | output_validation | 2026-04-12 |
| isr-concurrency-003 | L3 | k_sleep_present | 2026-04-12 |
| isr-concurrency-005 | L0 | init_before_isr_call | 2026-04-12 |
| isr-concurrency-006 | L0 | fifo_reserved_field | 2026-04-12 |
| isr-concurrency-008 | L3 | memory_barrier_present, barrier_between_data_and_index_update | 2026-04-12 |
| isr-concurrency-009 | L1 | west_build_docker | 2026-04-12 |
| isr-concurrency-011 | L1 | west_build_docker | 2026-04-12 |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-12 |
| kconfig-003 | L0 | uart_line_ctrl_enabled | 2026-04-12 |
| kconfig-005 | L0 | net_sockets_sockopt_tls_enabled, tls_credentials_enabled, mbedtls_builtin_enabled | 2026-04-12 |
| kconfig-010 | L0 | mbedtls_psa_crypto_enabled, hw_cc3xx_enabled | 2026-04-12 |
| linux-driver-005 | L3 | sysfs_create_group_error_handled | 2026-04-12 |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-04-12 |
| linux-driver-009 | L0 | gpiod_set_value_used | 2026-04-12 |
| memory-opt-001 | L0 | mem_slab_defined, slab_alloc_called, slab_free_called | 2026-04-12 |
| memory-opt-002 | L0 | minimal_libc_enabled, newlib_not_enabled | 2026-04-12 |
| memory-opt-003 | L0 | slab_defined, slab_alloc_called, slab_free_called | 2026-04-12 |
| memory-opt-004 | L0 | thread_analyzer_header, thread_analyzer_config, thread_stack_defined, thread_analyzer_print_called | 2026-04-12 |
| memory-opt-005 | L0 | app_memdomain_header | 2026-04-12 |
| memory-opt-006 | L0 | config_thread_stack_info_enabled | 2026-04-12 |
| memory-opt-008 | L0 | cbprintf_nano_enabled, dynamic_thread_disabled | 2026-04-12 |
| memory-opt-012 | L2 | output_validation | 2026-04-12 |
| networking-001 | L1 | west_build_docker | 2026-04-12 |
| networking-008 | L3 | connect_error_handling | 2026-04-12 |
| networking-009 | L1 | west_build_docker | 2026-04-12 |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-12 |
| ota-009 | L1 | west_build_docker | 2026-04-12 |
| ota-010 | L1 | west_build_docker | 2026-04-12 |
| ota-011 | L3 | self_test_failure_branch | 2026-04-12 |
| power-mgmt-002 | L3 | multiple_printk_calls | 2026-04-12 |
| power-mgmt-009 | L3 | battery_level_printed, periodic_battery_check, multiple_sleep_depths | 2026-04-12 |
| security-001 | L1 | west_build_docker | 2026-04-12 |
| security-004 | L2 | output_validation | 2026-04-12 |
| security-008 | L2 | output_validation | 2026-04-12 |
| sensor-driver-009 | L1 | west_build_docker | 2026-04-12 |
| sensor-driver-010 | L1 | west_build_docker | 2026-04-12 |
| spi-i2c-005 | L3 | found_count_reported | 2026-04-12 |
| spi-i2c-009 | L1 | west_build_docker | 2026-04-12 |
| stm32-adc-001 | L0 | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used, adc_started_with_dma (+1) | 2026-04-12 |
| stm32-dma-001 | L0 | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used, m2m_direction_configured (+1) | 2026-04-12 |
| stm32-freertos-001 | L0 | stm32_hal_header_included | 2026-04-12 |
| stm32-i2c-001 | L0 | stm32_hal_header_included, i2c_handle_typedef_used, i2c1_instance_configured, hal_i2c_mem_read_used (+1) | 2026-04-12 |
| stm32-lowpower-001 | L0 | stm32_hal_header_included | 2026-04-12 |
| stm32-spi-001 | L0 | stm32_hal_header_included, spi_handle_typedef_used, spi1_instance_configured, software_nss_used (+1) | 2026-04-12 |
| stm32-timer-001 | L0 | stm32_hal_header_included, tim_handle_typedef_used, tim3_instance_used, pwm_start_called (+1) | 2026-04-12 |
| storage-001 | L2 | output_validation | 2026-04-12 |
| storage-002 | L2 | runtime_started | 2026-04-12 |
| storage-004 | L1 | west_build_docker | 2026-04-12 |
| storage-005 | L1 | west_build_docker | 2026-04-12 |
| storage-006 | L3 | success_printed | 2026-04-12 |
| storage-008 | L0 | memcmp_verification | 2026-04-12 |
| storage-009 | L1 | west_build_docker | 2026-04-12 |
| storage-012 | L0 | no_freertos_apis | 2026-04-12 |
| storage-013 | L0 | flash_write_rate_limited | 2026-04-12 |
| threading-002 | L2 | runtime_started | 2026-04-12 |
| threading-006 | L2 | output_validation | 2026-04-12 |
| threading-007 | L3 | volatile_on_initialized_flag | 2026-04-12 |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-12 |
| threading-010 | L0 | k_sem_for_write_exclusion | 2026-04-12 |
| threading-011 | L2 | output_validation | 2026-04-12 |
| threading-012 | L1 | west_build_docker | 2026-04-12 |
| threading-013 | L2 | output_validation | 2026-04-12 |
| threading-014 | L0 | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag | 2026-04-12 |
| timer-001 | L3 | counter_is_volatile | 2026-04-12 |
| timer-002 | L0 | one_shot_period_no_wait | 2026-04-12 |
| timer-004 | L3 | main_waits_for_work | 2026-04-12 |
| timer-005 | L1 | west_build_docker | 2026-04-12 |
| timer-008 | L1 | west_build_docker | 2026-04-12 |
| uart-003 | L1 | west_build_docker | 2026-04-12 |
| watchdog-001 | L3 | install_before_setup | 2026-04-12 |
| watchdog-004 | L0 | two_channels_installed, separate_channel_ids | 2026-04-12 |
| watchdog-007 | L3 | wdt_feed_after_flag_check | 2026-04-12 |
| watchdog-009 | L0 | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max | 2026-04-12 |
| yocto-001 | L0 | summary_defined, license_defined, lic_files_chksum, src_uri_defined (+1) | 2026-04-12 |
| yocto-007 | L3 | rootfs_size_uses_weak_assignment | 2026-04-12 |
| yocto-009 | L0 | machine_features_defined, kernel_devicetree_defined, serial_consoles_defined, kernel_imagetype_defined | 2026-04-12 |

## claude-code://sonnet

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 2 | 100% | - |
| ble | 10 | 8 | 80% | west_build_docker, west_build_docker |
| boot | 10 | 9 | 90% | img_manager_dependency |
| device-tree | 10 | 10 | 100% | - |
| dma | 12 | 3 | 25% | west_build_docker, west_build_docker, cyclic_flag_set, output_validation, output_validation (+4) |
| esp-adc | 1 | 0 | 0% | adc_read_error_checked |
| esp-ble | 1 | 1 | 100% | - |
| esp-gpio | 1 | 1 | 100% | - |
| esp-i2c | 1 | 1 | 100% | - |
| esp-nvs | 1 | 0 | 0% | nvs_set_error_checked |
| esp-ota | 1 | 0 | 0% | firmware_validation |
| esp-sleep | 1 | 0 | 0% | gpio_pull_configured |
| esp-spi | 1 | 1 | 100% | - |
| esp-timer | 1 | 1 | 100% | - |
| esp-wifi | 1 | 1 | 100% | - |
| gpio-basic | 10 | 8 | 80% | device_ready_check, west_build_docker |
| isr-concurrency | 12 | 3 | 25% | no_printk, output_validation, k_sleep_present, output_validation, output_validation (+5) |
| kconfig | 10 | 9 | 90% | spi_dma_enabled |
| linux-driver | 10 | 7 | 70% | init_error_path_cleanup, init_error_path_cleanup, gpio_direction_set |
| memory-opt | 12 | 8 | 67% | output_validation, output_validation, partition_added_to_domain, no_large_string_literals |
| networking | 10 | 8 | 80% | connect_error_handling, west_build_docker |
| ota | 11 | 8 | 73% | rollback_abort_on_download_error, rollback_on_error, west_build_docker, self_test_failure_branch |
| power-mgmt | 10 | 8 | 80% | all_three_devices_suspended, periodic_battery_check |
| pwm | 1 | 1 | 100% | - |
| security | 10 | 5 | 50% | output_validation, output_validation, output_validation, error_path_returns_early, output_validation |
| sensor-driver | 10 | 8 | 80% | west_build_docker, west_build_docker |
| spi-i2c | 10 | 9 | 90% | west_build_docker |
| stm32-adc | 1 | 1 | 100% | - |
| stm32-dma | 1 | 1 | 100% | - |
| stm32-freertos | 2 | 0 | 0% | different_task_priorities, stm32_hal_header_included |
| stm32-gpio | 1 | 1 | 100% | - |
| stm32-i2c | 1 | 0 | 0% | hal_i2c_mem_read_used |
| stm32-lowpower | 1 | 1 | 100% | - |
| stm32-spi | 1 | 0 | 0% | cs_deasserted_after_transfer |
| stm32-timer | 1 | 0 | 0% | timer_clock_before_init |
| stm32-uart | 1 | 0 | 0% | receive_it_rearmed_in_callback |
| storage | 12 | 7 | 58% | output_validation, output_validation, write_verify_commit_order, verify_before_commit, delete_after_commit (+2) |
| threading | 14 | 5 | 36% | output_validation, output_validation, output_validation, deadline_constant_not_magic, west_build_docker (+6) |
| timer | 10 | 9 | 90% | output_validation |
| uart | 3 | 1 | 33% | callback_before_rx_enable, west_build_docker |
| watchdog | 10 | 9 | 90% | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| yocto | 10 | 8 | 80% | summary_defined, license_defined, lic_files_chksum, rootfs_size_uses_weak_assignment |

### Failed Cases (76)

| Case | Layer | Failed Checks | Tested |
|------|-------|---------------|--------|
| ble-009 | L1 | west_build_docker | 2026-04-12 |
| ble-010 | L1 | west_build_docker | 2026-04-12 |
| boot-001 | L3 | img_manager_dependency | 2026-04-12 |
| dma-001 | L1 | west_build_docker | 2026-04-12 |
| dma-002 | L1 | west_build_docker | 2026-04-12 |
| dma-003 | L0 | cyclic_flag_set | 2026-04-12 |
| dma-004 | L2 | output_validation | 2026-04-12 |
| dma-007 | L2 | output_validation | 2026-04-12 |
| dma-009 | L3 | dma_config_after_stop | 2026-04-12 |
| dma-010 | L0 | dma_reload_called | 2026-04-12 |
| dma-011 | L0 | single_dma_start | 2026-04-12 |
| dma-012 | L0 | cache_flush_before_dma | 2026-04-12 |
| esp-adc-001 | L3 | adc_read_error_checked | 2026-04-12 |
| esp-nvs-001 | L3 | nvs_set_error_checked | 2026-04-12 |
| esp-ota-001 | L3 | firmware_validation | 2026-04-12 |
| esp-sleep-001 | L3 | gpio_pull_configured | 2026-04-12 |
| gpio-basic-001 | L3 | device_ready_check | 2026-04-12 |
| gpio-basic-010 | L1 | west_build_docker | 2026-04-12 |
| isr-concurrency-001 | L0 | no_printk | 2026-04-12 |
| isr-concurrency-002 | L2 | output_validation | 2026-04-12 |
| isr-concurrency-003 | L3 | k_sleep_present | 2026-04-12 |
| isr-concurrency-005 | L2 | output_validation | 2026-04-12 |
| isr-concurrency-006 | L2 | output_validation | 2026-04-12 |
| isr-concurrency-008 | L3 | memory_barrier_present, barrier_between_data_and_index_update | 2026-04-12 |
| isr-concurrency-009 | L1 | west_build_docker | 2026-04-12 |
| isr-concurrency-011 | L2 | output_validation | 2026-04-12 |
| isr-concurrency-012 | L1 | west_build_docker | 2026-04-12 |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-12 |
| linux-driver-004 | L3 | init_error_path_cleanup | 2026-04-12 |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-04-12 |
| linux-driver-009 | L0 | gpio_direction_set | 2026-04-12 |
| memory-opt-001 | L2 | output_validation | 2026-04-12 |
| memory-opt-003 | L2 | output_validation | 2026-04-12 |
| memory-opt-005 | L0 | partition_added_to_domain | 2026-04-12 |
| memory-opt-012 | L3 | no_large_string_literals | 2026-04-12 |
| networking-008 | L3 | connect_error_handling | 2026-04-12 |
| networking-009 | L1 | west_build_docker | 2026-04-12 |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-12 |
| ota-010 | L1 | west_build_docker | 2026-04-12 |
| ota-011 | L3 | self_test_failure_branch | 2026-04-12 |
| power-mgmt-005 | L3 | all_three_devices_suspended | 2026-04-12 |
| power-mgmt-009 | L3 | periodic_battery_check | 2026-04-12 |
| security-001 | L2 | output_validation | 2026-04-12 |
| security-002 | L2 | output_validation | 2026-04-12 |
| security-004 | L2 | output_validation | 2026-04-12 |
| security-007 | L3 | error_path_returns_early | 2026-04-12 |
| security-008 | L2 | output_validation | 2026-04-12 |
| sensor-driver-009 | L1 | west_build_docker | 2026-04-12 |
| sensor-driver-010 | L1 | west_build_docker | 2026-04-12 |
| spi-i2c-009 | L1 | west_build_docker | 2026-04-12 |
| stm32-freertos-001 | L3 | different_task_priorities | 2026-04-12 |
| stm32-freertos-002 | L0 | stm32_hal_header_included | 2026-04-12 |
| stm32-i2c-001 | L0 | hal_i2c_mem_read_used | 2026-04-12 |
| stm32-spi-001 | L3 | cs_deasserted_after_transfer | 2026-04-12 |
| stm32-timer-001 | L3 | timer_clock_before_init | 2026-04-12 |
| stm32-uart-001 | L3 | receive_it_rearmed_in_callback | 2026-04-12 |
| storage-002 | L2 | output_validation | 2026-04-12 |
| storage-005 | L2 | output_validation | 2026-04-12 |
| storage-008 | L3 | write_verify_commit_order, verify_before_commit, delete_after_commit | 2026-04-12 |
| storage-009 | L1 | west_build_docker | 2026-04-12 |
| storage-012 | L3 | write_rate_limited | 2026-04-12 |
| threading-001 | L2 | output_validation | 2026-04-12 |
| threading-006 | L2 | output_validation | 2026-04-12 |
| threading-007 | L2 | output_validation | 2026-04-12 |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-12 |
| threading-010 | L1 | west_build_docker | 2026-04-12 |
| threading-011 | L2 | output_validation | 2026-04-12 |
| threading-012 | L1 | west_build_docker | 2026-04-12 |
| threading-013 | L2 | output_validation | 2026-04-12 |
| threading-014 | L0 | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag | 2026-04-12 |
| timer-001 | L2 | output_validation | 2026-04-12 |
| uart-002 | L3 | callback_before_rx_enable | 2026-04-12 |
| uart-003 | L1 | west_build_docker | 2026-04-12 |
| watchdog-009 | L0 | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max | 2026-04-12 |
| yocto-001 | L0 | summary_defined, license_defined, lic_files_chksum, src_uri_defined (+1) | 2026-04-12 |
| yocto-007 | L3 | rootfs_size_uses_weak_assignment | 2026-04-12 |

## mock

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| boot | 8 | 0 | 0% | kconfig_format, mcuboot_enabled, img_manager_enabled, kconfig_format, boot_delay_set (+19) |

### Failed Cases (8)

| Case | Layer | Failed Checks | Tested |
|------|-------|---------------|--------|
| boot-001 | L0 | kconfig_format, mcuboot_enabled, img_manager_enabled, flash_enabled | 2026-03-29 |
| boot-002 | L0 | kconfig_format, boot_delay_set, cmd_env_enabled | 2026-03-29 |
| boot-003 | L0 | kconfig_format, mcuboot_enabled, rsa_signature_type, signature_key_file (+1) | 2026-03-29 |
| boot-004 | L0 | kconfig_format, mcuboot_enabled, swap_using_move_enabled, max_img_sectors_set | 2026-03-29 |
| boot-005 | L0 | kconfig_format, mcuboot_enabled, boot_image_number_2, pcd_app_enabled | 2026-03-29 |
| boot-006 | L0 | kconfig_format, boot_encrypt_image_enabled, boot_encrypt_rsa_enabled, boot_signature_type_rsa_enabled | 2026-03-29 |
| boot-007 | L0 | kconfig_format, mcuboot_serial_enabled, boot_serial_cdc_acm_enabled, usb_device_stack_enabled | 2026-03-29 |
| boot-008 | L0 | kconfig_format, mcuboot_enabled, boot_version_cmp_build_number_enabled, boot_validate_slot0_enabled | 2026-03-29 |

