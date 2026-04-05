# EmbedEval Test Results

*Last updated: 2026-04-04 17:54 UTC*

## Summary

> **3 case(s) need retesting** — run `/test <model> --retest-only`

| Model | Cases | Passed | Failed | pass@1 | Retest |
|-------|-------|--------|--------|--------|--------|
| claude-code://haiku | 179 | 116 | 63 | 64.8% | 2 |
| claude-code://sonnet | 227 | 182 | 45 | 80.2% | - |
| mock | 8 | 0 | 8 | 0.0% | 1 |

## claude-code://haiku

### Needs Retest (2)

- **networking-008** (was FAIL, tested 2026-04-04)
- **timer-002** (was FAIL, tested 2026-03-29)

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 2 | 100% | - |
| ble | 8 | 6 | 75% | west_build_docker, conn_cleanup_on_failed_connect |
| boot | 8 | 8 | 100% | - |
| device-tree | 8 | 7 | 88% | pwm_polarity_specified |
| dma | 9 | 0 | 0% | dma_header_included, dma_config_called, cyclic_flag_set, dma_reload_called, dma_header_included (+9) |
| esp-gpio | 1 | 0 | 0% | gpio_header, app_main_defined, gpio_config_used |
| esp-i2c | 1 | 0 | 0% | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver |
| esp-spi | 1 | 1 | 100% | - |
| esp-timer | 1 | 1 | 100% | - |
| esp-wifi | 1 | 1 | 100% | - |
| gpio-basic | 3 | 3 | 100% | - |
| isr-concurrency | 9 | 2 | 22% | llm_call, no_printk_in_isr, init_before_isr_call, fifo_reserved_field, west_build_docker (+3) |
| kconfig | 8 | 6 | 75% | spi_dma_enabled, uart_line_ctrl_enabled |
| linux-driver | 8 | 7 | 88% | init_error_path_cleanup |
| memory-opt | 10 | 3 | 30% | mem_slab_defined, slab_alloc_called, slab_free_called, slab_defined, slab_alloc_called (+9) |
| networking | 8 | 5 | 62% | west_build_docker, timeout_not_infinite, will_configured_before_connect |
| ota | 8 | 7 | 88% | rollback_abort_on_download_error, rollback_on_error |
| power-mgmt | 8 | 7 | 88% | pm_action_run_called |
| pwm | 1 | 1 | 100% | - |
| security | 8 | 3 | 38% | west_build_docker, output_validation, output_validation, output_validation, output_validation |
| sensor-driver | 8 | 8 | 100% | - |
| spi-i2c | 8 | 7 | 88% | spi_header_included, write_command_0x02, read_command_0x03 |
| stm32-freertos | 1 | 1 | 100% | - |
| stm32-gpio | 1 | 1 | 100% | - |
| stm32-i2c | 1 | 0 | 0% | hal_i2c_mem_read_used |
| stm32-spi | 1 | 1 | 100% | - |
| stm32-uart | 1 | 0 | 0% | interrupt_receive_used |
| storage | 9 | 4 | 44% | runtime_started, west_build_docker, success_printed, west_build_docker, write_rate_limited |
| threading | 11 | 3 | 27% | west_build_docker, west_build_docker, lock_order_a_before_b, unlock_order_b_before_a, west_build_docker (+6) |
| timer | 8 | 5 | 62% | counter_is_volatile, main_sleeps_after_start, west_build_docker |
| uart | 2 | 1 | 50% | callback_before_rx_enable |
| watchdog | 9 | 8 | 89% | kernel_header_included, watchdog_header_included, persistent_storage_header_included |
| yocto | 8 | 7 | 88% | rootfs_size_uses_weak_assignment |

### Failed Cases (63)

| Case | Layer | Failed Checks | Tested | Status |
|------|-------|---------------|--------|--------|
| ble-001 | L1 | west_build_docker | 2026-04-04 | - |
| ble-008 | L3 | conn_cleanup_on_failed_connect | 2026-04-04 | - |
| device-tree-003 | L3 | pwm_polarity_specified | 2026-03-29 | - |
| dma-001 | L0 | dma_header_included | 2026-04-04 | - |
| dma-002 | L0 | dma_config_called | 2026-03-29 | - |
| dma-003 | L0 | cyclic_flag_set, dma_reload_called | 2026-04-04 | - |
| dma-004 | L0 | dma_header_included, multiple_block_descriptors | 2026-03-29 | - |
| dma-005 | L0 | cache_flush_present, cache_invalidate_present, dst_buffer_aligned | 2026-03-29 | - |
| dma-006 | L1 | west_build_docker | 2026-03-29 | - |
| dma-007 | L0 | channel_priority_field_used | 2026-03-29 | - |
| dma-008 | L2 | output_validation | 2026-04-04 | - |
| dma-009 | L0 | dma_header_included, kernel_header_included | 2026-04-04 | - |
| esp-gpio-001 | L0 | gpio_header, app_main_defined, gpio_config_used, no_zephyr_apis | 2026-04-04 | - |
| esp-i2c-001 | L0 | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver, no_zephyr_apis | 2026-03-29 | - |
| isr-concurrency-001 | L0 | llm_call | 2026-04-04 | - |
| isr-concurrency-002 | L0 | no_printk_in_isr | 2026-03-29 | - |
| isr-concurrency-005 | L0 | init_before_isr_call | 2026-03-29 | - |
| isr-concurrency-006 | L0 | fifo_reserved_field | 2026-03-29 | - |
| isr-concurrency-007 | L1 | west_build_docker | 2026-03-29 | - |
| isr-concurrency-008 | L3 | memory_barrier_present, barrier_between_data_and_index_update | 2026-04-04 | - |
| isr-concurrency-011 | L1 | west_build_docker | 2026-04-04 | - |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-04 | - |
| kconfig-003 | L0 | uart_line_ctrl_enabled | 2026-03-29 | - |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-03-29 | - |
| memory-opt-001 | L0 | mem_slab_defined, slab_alloc_called, slab_free_called | 2026-04-04 | - |
| memory-opt-003 | L0 | slab_defined, slab_alloc_called, slab_free_called | 2026-03-29 | - |
| memory-opt-004 | L0 | thread_analyzer_header, thread_analyzer_config, thread_analyzer_print_called | 2026-04-04 | - |
| memory-opt-005 | L0 | app_memdomain_header, partition_defined | 2026-04-04 | - |
| memory-opt-007 | L0 | null_returned_on_exhaustion | 2026-04-04 | - |
| memory-opt-008 | L0 | dynamic_thread_disabled | 2026-04-04 | - |
| memory-opt-012 | L1 | west_build_docker | 2026-04-04 | - |
| networking-003 | L1 | west_build_docker | 2026-04-04 | - |
| networking-007 | L3 | timeout_not_infinite | 2026-04-04 | - |
| networking-008 | L3 | will_configured_before_connect | 2026-04-04 | RETEST |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-04 | - |
| power-mgmt-005 | L0 | pm_action_run_called | 2026-04-04 | - |
| security-001 | L1 | west_build_docker | 2026-04-04 | - |
| security-002 | L2 | output_validation | 2026-03-29 | - |
| security-004 | L2 | output_validation | 2026-03-29 | - |
| security-006 | L2 | output_validation | 2026-03-29 | - |
| security-008 | L2 | output_validation | 2026-04-04 | - |
| spi-i2c-004 | L0 | spi_header_included, write_command_0x02, read_command_0x03 | 2026-04-04 | - |
| stm32-i2c-001 | L0 | hal_i2c_mem_read_used | 2026-03-29 | - |
| stm32-uart-001 | L0 | interrupt_receive_used | 2026-03-29 | - |
| storage-002 | L2 | runtime_started | 2026-03-29 | - |
| storage-005 | L1 | west_build_docker | 2026-03-29 | - |
| storage-006 | L3 | success_printed | 2026-03-29 | - |
| storage-008 | L1 | west_build_docker | 2026-03-29 | - |
| storage-012 | L3 | write_rate_limited | 2026-04-04 | - |
| threading-004 | L1 | west_build_docker | 2026-03-29 | - |
| threading-005 | L1 | west_build_docker | 2026-03-29 | - |
| threading-006 | L3 | lock_order_a_before_b, unlock_order_b_before_a | 2026-04-04 | - |
| threading-007 | L1 | west_build_docker | 2026-04-04 | - |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-04 | - |
| threading-011 | L1 | west_build_docker | 2026-03-29 | - |
| threading-012 | L0 | kernel_header_included, thread_created, has_main_function | 2026-03-29 | - |
| threading-013 | L1 | west_build_docker | 2026-04-04 | - |
| timer-001 | L3 | counter_is_volatile | 2026-04-04 | - |
| timer-002 | L3 | main_sleeps_after_start | 2026-03-29 | RETEST |
| timer-005 | L1 | west_build_docker | 2026-04-04 | - |
| uart-002 | L3 | callback_before_rx_enable | 2026-04-04 | - |
| watchdog-010 | L0 | kernel_header_included, watchdog_header_included, persistent_storage_header_included, printk_present | 2026-04-04 | - |
| yocto-007 | L3 | rootfs_size_uses_weak_assignment | 2026-03-29 | - |

## claude-code://sonnet

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 2 | 100% | - |
| ble | 10 | 10 | 100% | - |
| boot | 10 | 9 | 90% | img_manager_enabled |
| device-tree | 10 | 10 | 100% | - |
| dma | 10 | 5 | 50% | west_build_docker, cyclic_enabled, multiple_block_descriptors, channel_priority_field_used, dma_config_after_stop (+1) |
| esp-adc | 1 | 0 | 0% | adc_read_error_checked |
| esp-ble | 1 | 1 | 100% | - |
| esp-gpio | 1 | 1 | 100% | - |
| esp-i2c | 1 | 1 | 100% | - |
| esp-nvs | 1 | 0 | 0% | nvs_set_error_checked |
| esp-ota | 1 | 1 | 100% | - |
| esp-sleep | 1 | 1 | 100% | - |
| esp-spi | 1 | 1 | 100% | - |
| esp-timer | 1 | 1 | 100% | - |
| esp-wifi | 1 | 1 | 100% | - |
| gpio-basic | 10 | 9 | 90% | device_ready_check |
| isr-concurrency | 11 | 5 | 45% | message_struct_defined, no_forbidden_apis_in_isr, k_spinlock_used, k_spin_lock_called, spinlock_key_saved (+4) |
| kconfig | 10 | 9 | 90% | spi_dma_enabled |
| linux-driver | 10 | 8 | 80% | init_error_path_cleanup, init_error_path_cleanup |
| memory-opt | 12 | 7 | 58% | west_build_docker, output_validation, partition_added_to_domain, fpu_disabled, west_build_docker |
| networking | 10 | 10 | 100% | - |
| ota | 10 | 9 | 90% | rollback_abort_on_download_error, rollback_on_error |
| power-mgmt | 10 | 9 | 90% | periodic_battery_check |
| pwm | 1 | 1 | 100% | - |
| security | 10 | 4 | 40% | output_validation, output_validation, output_validation, output_validation, error_path_returns_early (+1) |
| sensor-driver | 10 | 10 | 100% | - |
| spi-i2c | 10 | 9 | 90% | poll_loop_bounded |
| stm32-freertos | 1 | 0 | 0% | stm32_hal_header_included |
| stm32-gpio | 1 | 1 | 100% | - |
| stm32-i2c | 1 | 1 | 100% | - |
| stm32-spi | 1 | 0 | 0% | spi_clock_before_init |
| stm32-uart | 1 | 1 | 100% | - |
| storage | 11 | 7 | 64% | output_validation, output_validation, write_verify_commit_order, verify_before_commit, delete_after_commit (+1) |
| threading | 13 | 7 | 54% | output_validation, output_validation, deadline_constant_not_magic, output_validation, west_build_docker (+1) |
| timer | 10 | 10 | 100% | - |
| uart | 2 | 2 | 100% | - |
| watchdog | 10 | 9 | 90% | llm_call |
| yocto | 10 | 10 | 100% | - |

### Failed Cases (45)

| Case | Layer | Failed Checks | Tested |
|------|-------|---------------|--------|
| boot-001 | L0 | img_manager_enabled | 2026-04-04 |
| dma-002 | L1 | west_build_docker | 2026-03-30 |
| dma-003 | L3 | cyclic_enabled | 2026-04-04 |
| dma-004 | L0 | multiple_block_descriptors | 2026-03-30 |
| dma-007 | L0 | channel_priority_field_used | 2026-03-30 |
| dma-009 | L3 | dma_config_after_stop, dma_start_called_twice | 2026-04-04 |
| esp-adc-001 | L3 | adc_read_error_checked | 2026-03-28 |
| esp-nvs-001 | L3 | nvs_set_error_checked | 2026-03-28 |
| gpio-basic-001 | L3 | device_ready_check | 2026-04-04 |
| isr-concurrency-002 | L3 | message_struct_defined, no_forbidden_apis_in_isr | 2026-03-29 |
| isr-concurrency-003 | L0 | k_spinlock_used, k_spin_lock_called, spinlock_key_saved, k_spin_unlock_called (+1) | 2026-04-04 |
| isr-concurrency-005 | L2 | output_validation | 2026-03-30 |
| isr-concurrency-006 | L1 | west_build_docker | 2026-03-30 |
| isr-concurrency-007 | L1 | west_build_docker | 2026-03-30 |
| isr-concurrency-008 | L2 | output_validation | 2026-04-04 |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-04 |
| linux-driver-004 | L3 | init_error_path_cleanup | 2026-03-29 |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-03-29 |
| memory-opt-001 | L1 | west_build_docker | 2026-04-04 |
| memory-opt-003 | L2 | output_validation | 2026-03-30 |
| memory-opt-005 | L0 | partition_added_to_domain | 2026-04-04 |
| memory-opt-008 | L0 | fpu_disabled | 2026-04-04 |
| memory-opt-012 | L1 | west_build_docker | 2026-04-04 |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-04 |
| power-mgmt-009 | L3 | periodic_battery_check | 2026-03-28 |
| security-001 | L2 | output_validation | 2026-04-04 |
| security-002 | L2 | output_validation | 2026-03-30 |
| security-004 | L2 | output_validation | 2026-03-30 |
| security-006 | L2 | output_validation | 2026-03-30 |
| security-007 | L3 | error_path_returns_early | 2026-04-04 |
| security-008 | L2 | output_validation | 2026-03-30 |
| spi-i2c-004 | L3 | poll_loop_bounded | 2026-04-04 |
| stm32-freertos-001 | L0 | stm32_hal_header_included | 2026-03-29 |
| stm32-spi-001 | L3 | spi_clock_before_init | 2026-03-29 |
| storage-002 | L2 | output_validation | 2026-03-30 |
| storage-005 | L2 | output_validation | 2026-03-30 |
| storage-008 | L3 | write_verify_commit_order, verify_before_commit, delete_after_commit | 2026-03-30 |
| storage-012 | L3 | write_rate_limited | 2026-04-04 |
| threading-001 | L2 | output_validation | 2026-04-04 |
| threading-007 | L2 | output_validation | 2026-04-04 |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-04 |
| threading-011 | L2 | output_validation | 2026-03-30 |
| threading-012 | L1 | west_build_docker | 2026-03-30 |
| threading-013 | L1 | west_build_docker | 2026-03-30 |
| watchdog-010 | L0 | llm_call | 2026-04-04 |

## mock

### Needs Retest (1)

- **boot-001** (was FAIL, tested 2026-03-29)

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| boot | 8 | 0 | 0% | kconfig_format, mcuboot_enabled, img_manager_enabled, kconfig_format, boot_delay_set (+19) |

### Failed Cases (8)

| Case | Layer | Failed Checks | Tested | Status |
|------|-------|---------------|--------|--------|
| boot-001 | L0 | kconfig_format, mcuboot_enabled, img_manager_enabled, flash_enabled | 2026-03-29 | RETEST |
| boot-002 | L0 | kconfig_format, boot_delay_set, cmd_env_enabled | 2026-03-29 | - |
| boot-003 | L0 | kconfig_format, mcuboot_enabled, rsa_signature_type, signature_key_file (+1) | 2026-03-29 | - |
| boot-004 | L0 | kconfig_format, mcuboot_enabled, swap_using_move_enabled, max_img_sectors_set | 2026-03-29 | - |
| boot-005 | L0 | kconfig_format, mcuboot_enabled, boot_image_number_2, pcd_app_enabled | 2026-03-29 | - |
| boot-006 | L0 | kconfig_format, boot_encrypt_image_enabled, boot_encrypt_rsa_enabled, boot_signature_type_rsa_enabled | 2026-03-29 | - |
| boot-007 | L0 | kconfig_format, mcuboot_serial_enabled, boot_serial_cdc_acm_enabled, usb_device_stack_enabled | 2026-03-29 | - |
| boot-008 | L0 | kconfig_format, mcuboot_enabled, boot_version_cmp_build_number_enabled, boot_validate_slot0_enabled | 2026-03-29 | - |

