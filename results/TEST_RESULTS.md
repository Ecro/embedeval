# EmbedEval Test Results

*Last updated: 2026-04-11 12:17 UTC*

## Summary

| Model | Cases | Passed | Failed | pass@1 | Retest |
|-------|-------|--------|--------|--------|--------|
| claude-code://haiku | 233 | 144 | 89 | 61.8% | - |
| claude-code://sonnet | 239 | 177 | 62 | 74.1% | - |
| mock | 8 | 0 | 8 | 0.0% | - |

## claude-code://haiku

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 2 | 100% | - |
| ble | 10 | 6 | 60% | west_build_docker, conn_cleanup_on_failed_connect, west_build_docker, bt_l2cap_chan_send_used |
| boot | 10 | 10 | 100% | - |
| device-tree | 10 | 9 | 90% | pwm_polarity_specified |
| dma | 12 | 0 | 0% | dma_header_included, dma_config_called, cyclic_flag_set, dma_reload_called, dma_header_included (+13) |
| esp-adc | 1 | 0 | 0% | calibration_before_raw_to_voltage, adc_read_error_checked |
| esp-ble | 1 | 1 | 100% | - |
| esp-gpio | 1 | 0 | 0% | gpio_header, app_main_defined, gpio_config_used |
| esp-i2c | 1 | 0 | 0% | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver |
| esp-nvs | 1 | 1 | 100% | - |
| esp-ota | 1 | 0 | 0% | rollback_on_failure, firmware_validation, error_handling_present |
| esp-sleep | 1 | 0 | 0% | esp_sleep_header, app_main_defined, deep_sleep_used |
| esp-spi | 1 | 1 | 100% | - |
| esp-timer | 1 | 1 | 100% | - |
| esp-wifi | 1 | 1 | 100% | - |
| gpio-basic | 4 | 3 | 75% | west_build_docker |
| isr-concurrency | 12 | 5 | 42% | llm_call, no_printk_in_isr, init_before_isr_call, fifo_reserved_field, memory_barrier_present (+3) |
| kconfig | 10 | 7 | 70% | spi_dma_enabled, uart_line_ctrl_enabled, mbedtls_builtin_enabled, mbedtls_psa_crypto_enabled, hw_cc3xx_enabled |
| linux-driver | 10 | 9 | 90% | init_error_path_cleanup |
| memory-opt | 12 | 5 | 42% | mem_slab_defined, slab_alloc_called, slab_free_called, slab_defined, slab_alloc_called (+9) |
| networking | 10 | 6 | 60% | west_build_docker, timeout_not_infinite, connect_error_handling, west_build_docker |
| ota | 11 | 8 | 73% | rollback_abort_on_download_error, rollback_on_error, west_build_docker, self_test_failure_branch |
| power-mgmt | 10 | 8 | 80% | pm_action_run_called, battery_level_printed, periodic_battery_check, multiple_sleep_depths |
| pwm | 1 | 1 | 100% | - |
| security | 10 | 5 | 50% | west_build_docker, runtime_started, output_validation, output_validation, return_value_checked |
| sensor-driver | 10 | 8 | 80% | west_build_docker, west_build_docker |
| spi-i2c | 10 | 8 | 80% | spi_header_included, write_command_0x02, read_command_0x03, west_build_docker |
| stm32-adc | 1 | 0 | 0% | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used |
| stm32-dma | 1 | 0 | 0% | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used |
| stm32-freertos | 2 | 2 | 100% | - |
| stm32-gpio | 1 | 1 | 100% | - |
| stm32-i2c | 1 | 0 | 0% | hal_i2c_mem_read_used |
| stm32-lowpower | 1 | 0 | 0% | stm32_hal_header_included, stop_mode_api_used, rtc_handle_typedef_used |
| stm32-spi | 1 | 1 | 100% | - |
| stm32-timer | 1 | 0 | 0% | stm32_hal_header_included, tim_handle_typedef_used, tim3_instance_used |
| stm32-uart | 1 | 0 | 0% | interrupt_receive_used |
| storage | 12 | 6 | 50% | runtime_started, west_build_docker, success_printed, west_build_docker, zero_size_check (+1) |
| threading | 14 | 4 | 29% | different_thread_priorities, west_build_docker, west_build_docker, lock_order_a_before_b, unlock_order_b_before_a (+10) |
| timer | 10 | 8 | 80% | counter_is_volatile, west_build_docker |
| uart | 3 | 1 | 33% | callback_before_rx_enable, west_build_docker |
| watchdog | 10 | 8 | 80% | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max, kernel_header_included, watchdog_header_included (+1) |
| yocto | 10 | 8 | 80% | rootfs_size_uses_weak_assignment, machine_features_defined, kernel_devicetree_defined, serial_consoles_defined |

### Failed Cases (89)

| Case | Layer | Failed Checks | Tested |
|------|-------|---------------|--------|
| ble-001 | L1 | west_build_docker | 2026-04-04 |
| ble-008 | L3 | conn_cleanup_on_failed_connect | 2026-04-04 |
| ble-009 | L1 | west_build_docker | 2026-04-11 |
| ble-010 | L0 | bt_l2cap_chan_send_used | 2026-04-11 |
| device-tree-003 | L3 | pwm_polarity_specified | 2026-03-29 |
| dma-001 | L0 | dma_header_included | 2026-04-04 |
| dma-002 | L0 | dma_config_called | 2026-03-29 |
| dma-003 | L0 | cyclic_flag_set, dma_reload_called | 2026-04-04 |
| dma-004 | L0 | dma_header_included, multiple_block_descriptors | 2026-03-29 |
| dma-005 | L0 | cache_flush_present, cache_invalidate_present, dst_buffer_aligned | 2026-03-29 |
| dma-006 | L1 | west_build_docker | 2026-03-29 |
| dma-007 | L0 | channel_priority_field_used | 2026-03-29 |
| dma-008 | L2 | output_validation | 2026-04-04 |
| dma-009 | L0 | dma_header_included, kernel_header_included | 2026-04-04 |
| dma-010 | L0 | dma_reload_called | 2026-04-11 |
| dma-011 | L0 | block_count_three | 2026-04-11 |
| dma-012 | L0 | dma_header_included, cache_flush_before_dma | 2026-04-11 |
| esp-adc-001 | L3 | calibration_before_raw_to_voltage, adc_read_error_checked | 2026-04-11 |
| esp-gpio-001 | L0 | gpio_header, app_main_defined, gpio_config_used, no_zephyr_apis | 2026-04-04 |
| esp-i2c-001 | L0 | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver, no_zephyr_apis | 2026-03-29 |
| esp-ota-001 | L3 | rollback_on_failure, firmware_validation, error_handling_present | 2026-04-11 |
| esp-sleep-001 | L0 | esp_sleep_header, app_main_defined, deep_sleep_used, gpio_wakeup_configured | 2026-04-11 |
| gpio-basic-010 | L1 | west_build_docker | 2026-04-11 |
| isr-concurrency-001 | L0 | llm_call | 2026-04-04 |
| isr-concurrency-002 | L0 | no_printk_in_isr | 2026-03-29 |
| isr-concurrency-005 | L0 | init_before_isr_call | 2026-03-29 |
| isr-concurrency-006 | L0 | fifo_reserved_field | 2026-03-29 |
| isr-concurrency-008 | L3 | memory_barrier_present, barrier_between_data_and_index_update | 2026-04-04 |
| isr-concurrency-009 | L1 | west_build_docker | 2026-04-11 |
| isr-concurrency-011 | L1 | west_build_docker | 2026-04-04 |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-04 |
| kconfig-003 | L0 | uart_line_ctrl_enabled | 2026-03-29 |
| kconfig-010 | L0 | mbedtls_builtin_enabled, mbedtls_psa_crypto_enabled, hw_cc3xx_enabled | 2026-04-11 |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-03-29 |
| memory-opt-001 | L0 | mem_slab_defined, slab_alloc_called, slab_free_called | 2026-04-04 |
| memory-opt-003 | L0 | slab_defined, slab_alloc_called, slab_free_called | 2026-03-29 |
| memory-opt-004 | L0 | thread_analyzer_header, thread_analyzer_config, thread_analyzer_print_called | 2026-04-04 |
| memory-opt-005 | L0 | app_memdomain_header, partition_defined | 2026-04-04 |
| memory-opt-007 | L0 | null_returned_on_exhaustion | 2026-04-04 |
| memory-opt-008 | L0 | dynamic_thread_disabled | 2026-04-04 |
| memory-opt-012 | L2 | output_validation | 2026-04-11 |
| networking-003 | L1 | west_build_docker | 2026-04-04 |
| networking-007 | L3 | timeout_not_infinite | 2026-04-04 |
| networking-008 | L3 | connect_error_handling | 2026-04-11 |
| networking-009 | L1 | west_build_docker | 2026-04-11 |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-04 |
| ota-010 | L1 | west_build_docker | 2026-04-11 |
| ota-011 | L3 | self_test_failure_branch | 2026-04-11 |
| power-mgmt-005 | L0 | pm_action_run_called | 2026-04-04 |
| power-mgmt-009 | L3 | battery_level_printed, periodic_battery_check, multiple_sleep_depths | 2026-04-11 |
| security-001 | L1 | west_build_docker | 2026-04-04 |
| security-002 | L2 | runtime_started | 2026-04-11 |
| security-004 | L2 | output_validation | 2026-04-11 |
| security-008 | L2 | output_validation | 2026-04-11 |
| security-009 | L0 | return_value_checked | 2026-04-11 |
| sensor-driver-009 | L1 | west_build_docker | 2026-04-11 |
| sensor-driver-010 | L1 | west_build_docker | 2026-04-11 |
| spi-i2c-004 | L0 | spi_header_included, write_command_0x02, read_command_0x03 | 2026-04-04 |
| spi-i2c-009 | L1 | west_build_docker | 2026-04-11 |
| stm32-adc-001 | L0 | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used, adc_started_with_dma (+1) | 2026-04-11 |
| stm32-dma-001 | L0 | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used, m2m_direction_configured (+1) | 2026-04-11 |
| stm32-i2c-001 | L0 | hal_i2c_mem_read_used | 2026-03-29 |
| stm32-lowpower-001 | L0 | stm32_hal_header_included, stop_mode_api_used, rtc_handle_typedef_used, rtc_alarm_interrupt_used (+1) | 2026-04-11 |
| stm32-timer-001 | L0 | stm32_hal_header_included, tim_handle_typedef_used, tim3_instance_used, pwm_start_called (+1) | 2026-04-11 |
| stm32-uart-001 | L0 | interrupt_receive_used | 2026-03-29 |
| storage-002 | L2 | runtime_started | 2026-03-29 |
| storage-005 | L1 | west_build_docker | 2026-03-29 |
| storage-006 | L3 | success_printed | 2026-03-29 |
| storage-008 | L1 | west_build_docker | 2026-03-29 |
| storage-009 | L0 | zero_size_check | 2026-04-11 |
| storage-012 | L3 | write_rate_limited | 2026-04-04 |
| threading-001 | L3 | different_thread_priorities | 2026-04-11 |
| threading-004 | L1 | west_build_docker | 2026-03-29 |
| threading-005 | L1 | west_build_docker | 2026-03-29 |
| threading-006 | L3 | lock_order_a_before_b, unlock_order_b_before_a | 2026-04-04 |
| threading-007 | L1 | west_build_docker | 2026-04-04 |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-04 |
| threading-011 | L1 | west_build_docker | 2026-03-29 |
| threading-012 | L0 | kernel_header_included, thread_created, has_main_function | 2026-03-29 |
| threading-013 | L2 | output_validation | 2026-04-11 |
| threading-014 | L0 | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag | 2026-04-11 |
| timer-001 | L3 | counter_is_volatile | 2026-04-04 |
| timer-005 | L1 | west_build_docker | 2026-04-04 |
| uart-002 | L3 | callback_before_rx_enable | 2026-04-04 |
| uart-003 | L1 | west_build_docker | 2026-04-11 |
| watchdog-009 | L0 | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max, wdt_configured | 2026-04-11 |
| watchdog-010 | L0 | kernel_header_included, watchdog_header_included, persistent_storage_header_included, printk_present | 2026-04-04 |
| yocto-007 | L3 | rootfs_size_uses_weak_assignment | 2026-03-29 |
| yocto-009 | L0 | machine_features_defined, kernel_devicetree_defined, serial_consoles_defined, kernel_imagetype_defined | 2026-04-11 |

## claude-code://sonnet

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 2 | 100% | - |
| ble | 10 | 8 | 80% | west_build_docker, west_build_docker |
| boot | 10 | 10 | 100% | - |
| device-tree | 10 | 10 | 100% | - |
| dma | 12 | 5 | 42% | west_build_docker, cyclic_enabled, multiple_block_descriptors, channel_priority_field_used, dma_config_after_stop (+3) |
| esp-adc | 1 | 0 | 0% | adc_read_error_checked |
| esp-ble | 1 | 1 | 100% | - |
| esp-gpio | 1 | 1 | 100% | - |
| esp-i2c | 1 | 1 | 100% | - |
| esp-nvs | 1 | 1 | 100% | - |
| esp-ota | 1 | 1 | 100% | - |
| esp-sleep | 1 | 1 | 100% | - |
| esp-spi | 1 | 1 | 100% | - |
| esp-timer | 1 | 1 | 100% | - |
| esp-wifi | 1 | 1 | 100% | - |
| gpio-basic | 10 | 8 | 80% | device_ready_check, west_build_docker |
| isr-concurrency | 12 | 5 | 42% | message_struct_defined, no_forbidden_apis_in_isr, k_sleep_present, output_validation, west_build_docker (+3) |
| kconfig | 10 | 8 | 80% | spi_dma_enabled, hw_cc3xx_enabled |
| linux-driver | 10 | 7 | 70% | init_error_path_cleanup, init_error_path_cleanup, gpio_direction_set |
| memory-opt | 12 | 7 | 58% | west_build_docker, output_validation, partition_added_to_domain, fpu_disabled, output_validation |
| networking | 10 | 9 | 90% | west_build_docker |
| ota | 11 | 8 | 73% | rollback_abort_on_download_error, rollback_on_error, west_build_docker, self_test_failure_branch |
| power-mgmt | 10 | 9 | 90% | west_build_docker |
| pwm | 1 | 1 | 100% | - |
| security | 10 | 6 | 60% | output_validation, output_validation, error_path_returns_early, output_validation |
| sensor-driver | 10 | 8 | 80% | west_build_docker, west_build_docker |
| spi-i2c | 10 | 8 | 80% | poll_loop_bounded, west_build_docker |
| stm32-adc | 1 | 1 | 100% | - |
| stm32-dma | 1 | 1 | 100% | - |
| stm32-freertos | 2 | 1 | 50% | stm32_hal_header_included |
| stm32-gpio | 1 | 1 | 100% | - |
| stm32-i2c | 1 | 1 | 100% | - |
| stm32-lowpower | 1 | 1 | 100% | - |
| stm32-spi | 1 | 0 | 0% | spi_clock_before_init |
| stm32-timer | 1 | 0 | 0% | timer_clock_before_init |
| stm32-uart | 1 | 1 | 100% | - |
| storage | 12 | 6 | 50% | output_validation, output_validation, write_verify_commit_order, verify_before_commit, delete_after_commit (+3) |
| threading | 14 | 6 | 43% | output_validation, output_validation, deadline_constant_not_magic, west_build_docker, output_validation (+5) |
| timer | 10 | 10 | 100% | - |
| uart | 3 | 2 | 67% | west_build_docker |
| watchdog | 10 | 8 | 80% | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max, llm_call |
| yocto | 10 | 10 | 100% | - |

### Failed Cases (62)

| Case | Layer | Failed Checks | Tested |
|------|-------|---------------|--------|
| ble-009 | L1 | west_build_docker | 2026-04-11 |
| ble-010 | L1 | west_build_docker | 2026-04-11 |
| dma-002 | L1 | west_build_docker | 2026-03-30 |
| dma-003 | L3 | cyclic_enabled | 2026-04-04 |
| dma-004 | L0 | multiple_block_descriptors | 2026-03-30 |
| dma-007 | L0 | channel_priority_field_used | 2026-03-30 |
| dma-009 | L3 | dma_config_after_stop, dma_start_called_twice | 2026-04-04 |
| dma-010 | L0 | dma_reload_called | 2026-04-11 |
| dma-011 | L0 | single_dma_start | 2026-04-11 |
| esp-adc-001 | L3 | adc_read_error_checked | 2026-04-11 |
| gpio-basic-001 | L3 | device_ready_check | 2026-04-04 |
| gpio-basic-010 | L1 | west_build_docker | 2026-04-11 |
| isr-concurrency-002 | L3 | message_struct_defined, no_forbidden_apis_in_isr | 2026-03-29 |
| isr-concurrency-003 | L3 | k_sleep_present | 2026-04-11 |
| isr-concurrency-005 | L2 | output_validation | 2026-03-30 |
| isr-concurrency-006 | L1 | west_build_docker | 2026-03-30 |
| isr-concurrency-008 | L2 | output_validation | 2026-04-04 |
| isr-concurrency-009 | L1 | west_build_docker | 2026-04-11 |
| isr-concurrency-012 | L0 | no_isr_unsafe_primitives | 2026-04-11 |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-04 |
| kconfig-010 | L0 | hw_cc3xx_enabled | 2026-04-11 |
| linux-driver-004 | L3 | init_error_path_cleanup | 2026-03-29 |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-03-29 |
| linux-driver-009 | L0 | gpio_direction_set | 2026-04-11 |
| memory-opt-001 | L1 | west_build_docker | 2026-04-04 |
| memory-opt-003 | L2 | output_validation | 2026-03-30 |
| memory-opt-005 | L0 | partition_added_to_domain | 2026-04-04 |
| memory-opt-008 | L0 | fpu_disabled | 2026-04-04 |
| memory-opt-012 | L2 | output_validation | 2026-04-11 |
| networking-009 | L1 | west_build_docker | 2026-04-11 |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-04 |
| ota-010 | L1 | west_build_docker | 2026-04-11 |
| ota-011 | L3 | self_test_failure_branch | 2026-04-11 |
| power-mgmt-009 | L1 | west_build_docker | 2026-04-11 |
| security-001 | L2 | output_validation | 2026-04-04 |
| security-004 | L2 | output_validation | 2026-04-11 |
| security-007 | L3 | error_path_returns_early | 2026-04-04 |
| security-008 | L2 | output_validation | 2026-04-11 |
| sensor-driver-009 | L1 | west_build_docker | 2026-04-11 |
| sensor-driver-010 | L1 | west_build_docker | 2026-04-11 |
| spi-i2c-004 | L3 | poll_loop_bounded | 2026-04-04 |
| spi-i2c-009 | L1 | west_build_docker | 2026-04-11 |
| stm32-freertos-001 | L0 | stm32_hal_header_included | 2026-03-29 |
| stm32-spi-001 | L3 | spi_clock_before_init | 2026-03-29 |
| stm32-timer-001 | L3 | timer_clock_before_init | 2026-04-11 |
| storage-002 | L2 | output_validation | 2026-03-30 |
| storage-005 | L2 | output_validation | 2026-03-30 |
| storage-008 | L3 | write_verify_commit_order, verify_before_commit, delete_after_commit | 2026-03-30 |
| storage-009 | L0 | offset_plus_size_boundary_check | 2026-04-11 |
| storage-012 | L3 | write_rate_limited | 2026-04-04 |
| storage-013 | L0 | save_not_unconditional_in_loop | 2026-04-11 |
| threading-001 | L2 | output_validation | 2026-04-11 |
| threading-007 | L2 | output_validation | 2026-04-04 |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-04 |
| threading-010 | L1 | west_build_docker | 2026-04-11 |
| threading-011 | L2 | output_validation | 2026-03-30 |
| threading-012 | L1 | west_build_docker | 2026-03-30 |
| threading-013 | L2 | output_validation | 2026-04-11 |
| threading-014 | L0 | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag | 2026-04-11 |
| uart-003 | L1 | west_build_docker | 2026-04-11 |
| watchdog-009 | L0 | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max | 2026-04-11 |
| watchdog-010 | L0 | llm_call | 2026-04-04 |

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

