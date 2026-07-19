# EmbedEval Test Results

*Last updated: 2026-07-19 12:25 UTC*

## Summary

> **474 case(s) need retesting** — run `/test <model> --retest-only`

| Model | Cases | Passed | Failed | pass@1 | Retest |
|-------|-------|--------|--------|--------|--------|
| claude-code://claude-sonnet-5 | 263 | 177 | 86 | 67.3% | - |
| claude-code://haiku | 233 | 133 | 100 | 57.1% | 233 |
| claude-code://sonnet | 239 | 163 | 76 | 68.2% | 233 |
| mock | 8 | 0 | 8 | 0.0% | 8 |

## claude-code://claude-sonnet-5

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 2 | 100% | - |
| ble | 10 | 7 | 70% | scan_stopped_before_connect, west_build_docker, west_build_docker |
| boot | 9 | 9 | 100% | - |
| boot-uboot | 4 | 4 | 100% | - |
| device-tree | 10 | 10 | 100% | - |
| dma | 12 | 5 | 42% | runtime_started, cyclic_flag_set, multiple_block_descriptors, post_invalidate_dst_after_dma, two_dma_config_calls (+2) |
| esp-adc | 1 | 0 | 0% | adc_read_error_checked |
| esp-ble | 1 | 1 | 100% | - |
| esp-gpio | 1 | 1 | 100% | - |
| esp-i2c | 1 | 1 | 100% | - |
| esp-nvs | 1 | 1 | 100% | - |
| esp-ota | 1 | 1 | 100% | - |
| esp-sleep | 1 | 1 | 100% | - |
| esp-spi | 1 | 1 | 100% | - |
| esp-timer | 1 | 1 | 100% | - |
| esp-wifi | 1 | 0 | 0% | nvs_initialized_before_wifi |
| gpio-basic | 4 | 3 | 75% | west_build_docker |
| isr-concurrency | 12 | 4 | 33% | no_printk, output_validation, k_sleep_present, init_before_isr_call, output_validation (+3) |
| kconfig | 10 | 7 | 70% | spi_dma_enabled, bt_hci_enabled, hw_cc3xx_enabled |
| linux-driver | 16 | 11 | 69% | init_error_path_cleanup, isr_uses_spin_lock_irqsave, free_irq_before_cancel_work, mod_devicetable_header_included, is_err_guards_reset_control_get |
| linux-userspace | 8 | 6 | 75% | nonzero_exit_on_error, comm_array_size_16_bytes |
| memory-opt | 12 | 6 | 50% | output_validation, output_validation, config_thread_stack_info_enabled, output_validation, output_validation (+1) |
| networking | 10 | 8 | 80% | request_timeout_set, west_build_docker |
| networking-kernel | 5 | 2 | 40% | producer_uses_skb_clone, skb_clone_uses_gfp_atomic, skb_clone_return_null_checked, input_cb_sends_netlink_unicast, skbuff_header_included |
| ota | 11 | 7 | 64% | done_after_write, rollback_abort_on_download_error, rollback_on_error, west_build_docker, self_test_failure_branch |
| ota-rauc | 2 | 2 | 100% | - |
| ota-swupdate | 4 | 1 | 25% | hardware_compatibility_list_nonempty, hardware_compatibility_list_nonempty, two_selection_groups_copy_1_copy_2, copy_1_has_three_images, hardware_compatibility_list_nonempty |
| power-mgmt | 10 | 8 | 80% | periodic_battery_check, multiple_sleep_depths, state_get_return_checked |
| pwm | 1 | 1 | 100% | - |
| security | 10 | 6 | 60% | output_validation, output_validation, error_path_returns_early, output_validation |
| sensor-driver | 10 | 7 | 70% | error_handling, west_build_docker, west_build_docker |
| spi-i2c | 10 | 9 | 90% | west_build_docker |
| stm32-adc | 1 | 1 | 100% | - |
| stm32-dma | 1 | 0 | 0% | data_verified_after_transfer |
| stm32-freertos | 2 | 2 | 100% | - |
| stm32-gpio | 1 | 1 | 100% | - |
| stm32-i2c | 1 | 0 | 0% | i2c_clock_enabled |
| stm32-lowpower | 1 | 1 | 100% | - |
| stm32-spi | 1 | 0 | 0% | cs_asserted_before_transfer, spi_clock_before_init |
| stm32-timer | 1 | 1 | 100% | - |
| stm32-uart | 1 | 0 | 0% | uart_clock_before_init |
| storage | 12 | 6 | 50% | output_validation, output_validation, output_validation, west_build_docker, west_build_docker (+1) |
| threading | 14 | 7 | 50% | output_validation, output_validation, reader_count_variable, output_validation, west_build_docker (+4) |
| timer | 10 | 8 | 80% | expiry_increments_counter, counter_is_volatile, timer_period_less_than_wdt_timeout |
| uart | 3 | 2 | 67% | west_build_docker |
| watchdog | 10 | 8 | 80% | distinct_channel_timeouts, window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| yocto | 12 | 7 | 58% | lic_files_chksum, srcrev_defined, summary_defined, license_defined, inherit_systemd (+7) |

### Failed Cases (86)

| Case | Layer | Failed Checks | Tested |
|------|-------|---------------|--------|
| ble-008 | L3 | scan_stopped_before_connect | 2026-07-19 |
| ble-009 | L1 | west_build_docker | 2026-07-19 |
| ble-010 | L1 | west_build_docker | 2026-07-19 |
| dma-002 | L2 | runtime_started | 2026-07-19 |
| dma-003 | L0 | cyclic_flag_set | 2026-07-19 |
| dma-004 | L0 | multiple_block_descriptors | 2026-07-19 |
| dma-005 | L3 | post_invalidate_dst_after_dma | 2026-07-19 |
| dma-007 | L0 | two_dma_config_calls | 2026-07-19 |
| dma-009 | L3 | dma_start_called_twice | 2026-07-19 |
| dma-012 | L0 | buffer_alignment | 2026-07-19 |
| esp-adc-001 | L3 | adc_read_error_checked | 2026-07-19 |
| esp-wifi-001 | L3 | nvs_initialized_before_wifi | 2026-07-19 |
| gpio-basic-010 | L1 | west_build_docker | 2026-07-19 |
| isr-concurrency-001 | L0 | no_printk | 2026-07-19 |
| isr-concurrency-002 | L2 | output_validation | 2026-07-19 |
| isr-concurrency-003 | L3 | k_sleep_present | 2026-07-19 |
| isr-concurrency-005 | L0 | init_before_isr_call | 2026-07-19 |
| isr-concurrency-006 | L2 | output_validation | 2026-07-19 |
| isr-concurrency-008 | L2 | output_validation | 2026-07-19 |
| isr-concurrency-009 | L1 | west_build_docker | 2026-07-19 |
| isr-concurrency-011 | L1 | west_build_docker | 2026-07-19 |
| kconfig-001 | L0 | spi_dma_enabled | 2026-07-19 |
| kconfig-002 | L0 | bt_hci_enabled | 2026-07-19 |
| kconfig-010 | L0 | hw_cc3xx_enabled | 2026-07-19 |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-07-19 |
| linux-driver-009 | L3 | isr_uses_spin_lock_irqsave | 2026-07-19 |
| linux-driver-011 | L3 | free_irq_before_cancel_work | 2026-07-19 |
| linux-driver-013 | L0 | mod_devicetable_header_included | 2026-07-19 |
| linux-driver-016 | L3 | is_err_guards_reset_control_get | 2026-07-19 |
| linux-userspace-001 | L3 | nonzero_exit_on_error | 2026-07-19 |
| linux-userspace-008 | L3 | comm_array_size_16_bytes | 2026-07-19 |
| memory-opt-001 | L2 | output_validation | 2026-07-19 |
| memory-opt-003 | L2 | output_validation | 2026-07-19 |
| memory-opt-006 | L0 | config_thread_stack_info_enabled | 2026-07-19 |
| memory-opt-007 | L2 | output_validation | 2026-07-19 |
| memory-opt-011 | L2 | output_validation | 2026-07-19 |
| memory-opt-012 | L3 | no_large_string_literals | 2026-07-19 |
| networking-005 | L3 | request_timeout_set | 2026-07-19 |
| networking-009 | L1 | west_build_docker | 2026-07-19 |
| networking-kernel-002 | L3 | producer_uses_skb_clone, skb_clone_uses_gfp_atomic, skb_clone_return_null_checked, exit_cancels_work_then_purges_queue | 2026-07-19 |
| networking-kernel-003 | L3 | input_cb_sends_netlink_unicast | 2026-07-19 |
| networking-kernel-004 | L0 | skbuff_header_included | 2026-07-19 |
| ota-003 | L3 | done_after_write | 2026-07-19 |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-07-19 |
| ota-010 | L1 | west_build_docker | 2026-07-19 |
| ota-011 | L3 | self_test_failure_branch | 2026-07-19 |
| ota-swupdate-001 | L3 | hardware_compatibility_list_nonempty | 2026-07-19 |
| ota-swupdate-002 | L3 | hardware_compatibility_list_nonempty, two_selection_groups_copy_1_copy_2, copy_1_has_three_images, copy_2_has_three_images (+2) | 2026-07-19 |
| ota-swupdate-004 | L3 | hardware_compatibility_list_nonempty | 2026-07-19 |
| power-mgmt-009 | L3 | periodic_battery_check, multiple_sleep_depths | 2026-07-19 |
| power-mgmt-010 | L3 | state_get_return_checked | 2026-07-19 |
| security-001 | L2 | output_validation | 2026-07-19 |
| security-004 | L2 | output_validation | 2026-07-19 |
| security-007 | L3 | error_path_returns_early | 2026-07-19 |
| security-008 | L2 | output_validation | 2026-07-19 |
| sensor-driver-003 | L3 | error_handling | 2026-07-19 |
| sensor-driver-009 | L1 | west_build_docker | 2026-07-19 |
| sensor-driver-010 | L1 | west_build_docker | 2026-07-19 |
| spi-i2c-009 | L1 | west_build_docker | 2026-07-19 |
| stm32-dma-001 | L3 | data_verified_after_transfer | 2026-07-19 |
| stm32-i2c-001 | L0 | i2c_clock_enabled | 2026-07-19 |
| stm32-spi-001 | L3 | cs_asserted_before_transfer, spi_clock_before_init | 2026-07-19 |
| stm32-uart-001 | L3 | uart_clock_before_init | 2026-07-19 |
| storage-002 | L2 | output_validation | 2026-07-19 |
| storage-004 | L2 | output_validation | 2026-07-19 |
| storage-005 | L2 | output_validation | 2026-07-19 |
| storage-008 | L1 | west_build_docker | 2026-07-19 |
| storage-009 | L1 | west_build_docker | 2026-07-19 |
| storage-013 | L3 | handler_registered | 2026-07-19 |
| threading-001 | L2 | output_validation | 2026-07-19 |
| threading-007 | L2 | output_validation | 2026-07-19 |
| threading-010 | L0 | reader_count_variable | 2026-07-19 |
| threading-011 | L2 | output_validation | 2026-07-19 |
| threading-012 | L1 | west_build_docker | 2026-07-19 |
| threading-013 | L2 | output_validation | 2026-07-19 |
| threading-014 | L0 | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag | 2026-07-19 |
| timer-001 | L3 | expiry_increments_counter, counter_is_volatile | 2026-07-19 |
| timer-007 | L3 | timer_period_less_than_wdt_timeout | 2026-07-19 |
| uart-003 | L1 | west_build_docker | 2026-07-19 |
| watchdog-004 | L3 | distinct_channel_timeouts | 2026-07-19 |
| watchdog-009 | L0 | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max | 2026-07-19 |
| yocto-002 | L0 | lic_files_chksum, srcrev_defined | 2026-07-19 |
| yocto-003 | L0 | summary_defined, license_defined, inherit_systemd, systemd_service_var (+2) | 2026-07-19 |
| yocto-004 | L0 | depends_defined, rdepends_defined, do_install_defined | 2026-07-19 |
| yocto-005 | L0 | summary_defined, license_defined, inherit_module, src_uri_defined (+2) | 2026-07-19 |
| yocto-007 | L3 | rootfs_size_uses_weak_assignment | 2026-07-19 |

## claude-code://haiku

### Needs Retest (233)

- **adc-001** (was PASS, tested 2026-04-12)
- **adc-002** (was FAIL, tested 2026-04-12)
- **ble-001** (was FAIL, tested 2026-04-12)
- **ble-002** (was PASS, tested 2026-04-12)
- **ble-003** (was FAIL, tested 2026-04-12)
- **ble-004** (was PASS, tested 2026-04-12)
- **ble-005** (was FAIL, tested 2026-04-12)
- **ble-006** (was PASS, tested 2026-04-12)
- **ble-007** (was PASS, tested 2026-04-12)
- **ble-008** (was FAIL, tested 2026-04-12)
- **ble-009** (was FAIL, tested 2026-04-12)
- **ble-010** (was FAIL, tested 2026-04-12)
- **boot-001** (was PASS, tested 2026-04-12)
- **boot-003** (was PASS, tested 2026-04-12)
- **boot-004** (was PASS, tested 2026-04-12)
- **boot-005** (was PASS, tested 2026-04-12)
- **boot-006** (was PASS, tested 2026-04-12)
- **boot-007** (was PASS, tested 2026-04-12)
- **boot-008** (was PASS, tested 2026-04-12)
- **boot-009** (was PASS, tested 2026-04-12)
- **boot-010** (was PASS, tested 2026-04-12)
- **boot-uboot-001** (was PASS, tested 2026-04-12)
- **device-tree-001** (was PASS, tested 2026-04-12)
- **device-tree-002** (was PASS, tested 2026-04-12)
- **device-tree-003** (was PASS, tested 2026-04-12)
- **device-tree-004** (was PASS, tested 2026-04-12)
- **device-tree-005** (was PASS, tested 2026-04-12)
- **device-tree-006** (was PASS, tested 2026-04-12)
- **device-tree-007** (was PASS, tested 2026-04-12)
- **device-tree-008** (was PASS, tested 2026-04-12)
- **device-tree-009** (was PASS, tested 2026-04-12)
- **device-tree-010** (was PASS, tested 2026-04-12)
- **dma-001** (was FAIL, tested 2026-04-12)
- **dma-002** (was FAIL, tested 2026-04-12)
- **dma-003** (was FAIL, tested 2026-04-12)
- **dma-004** (was FAIL, tested 2026-04-12)
- **dma-005** (was FAIL, tested 2026-04-12)
- **dma-006** (was FAIL, tested 2026-04-12)
- **dma-007** (was FAIL, tested 2026-04-12)
- **dma-008** (was FAIL, tested 2026-04-12)
- **dma-009** (was FAIL, tested 2026-04-12)
- **dma-010** (was FAIL, tested 2026-04-12)
- **dma-011** (was PASS, tested 2026-04-12)
- **dma-012** (was FAIL, tested 2026-04-12)
- **esp-adc-001** (was FAIL, tested 2026-04-12)
- **esp-ble-001** (was PASS, tested 2026-04-12)
- **esp-gpio-001** (was PASS, tested 2026-04-12)
- **esp-i2c-001** (was FAIL, tested 2026-04-12)
- **esp-nvs-001** (was PASS, tested 2026-04-12)
- **esp-ota-001** (was FAIL, tested 2026-04-12)
- **esp-sleep-001** (was FAIL, tested 2026-04-12)
- **esp-spi-001** (was PASS, tested 2026-04-12)
- **esp-timer-001** (was PASS, tested 2026-04-12)
- **esp-wifi-001** (was PASS, tested 2026-04-12)
- **gpio-basic-001** (was PASS, tested 2026-04-12)
- **gpio-basic-005** (was PASS, tested 2026-04-12)
- **gpio-basic-006** (was PASS, tested 2026-04-12)
- **gpio-basic-010** (was FAIL, tested 2026-04-12)
- **isr-concurrency-001** (was FAIL, tested 2026-04-12)
- **isr-concurrency-002** (was FAIL, tested 2026-04-12)
- **isr-concurrency-003** (was FAIL, tested 2026-04-12)
- **isr-concurrency-004** (was PASS, tested 2026-04-12)
- **isr-concurrency-005** (was FAIL, tested 2026-04-12)
- **isr-concurrency-006** (was FAIL, tested 2026-04-12)
- **isr-concurrency-007** (was PASS, tested 2026-04-12)
- **isr-concurrency-008** (was FAIL, tested 2026-04-12)
- **isr-concurrency-009** (was FAIL, tested 2026-04-12)
- **isr-concurrency-010** (was PASS, tested 2026-04-12)
- **isr-concurrency-011** (was FAIL, tested 2026-04-12)
- **isr-concurrency-012** (was PASS, tested 2026-04-12)
- **kconfig-001** (was FAIL, tested 2026-04-12)
- **kconfig-002** (was PASS, tested 2026-04-12)
- **kconfig-003** (was FAIL, tested 2026-04-12)
- **kconfig-004** (was PASS, tested 2026-04-12)
- **kconfig-005** (was FAIL, tested 2026-04-12)
- **kconfig-006** (was PASS, tested 2026-04-12)
- **kconfig-007** (was PASS, tested 2026-04-12)
- **kconfig-008** (was PASS, tested 2026-04-12)
- **kconfig-009** (was PASS, tested 2026-04-12)
- **kconfig-010** (was FAIL, tested 2026-04-12)
- **linux-driver-001** (was PASS, tested 2026-04-12)
- **linux-driver-002** (was PASS, tested 2026-04-12)
- **linux-driver-003** (was PASS, tested 2026-04-12)
- **linux-driver-004** (was PASS, tested 2026-04-12)
- **linux-driver-005** (was FAIL, tested 2026-04-12)
- **linux-driver-006** (was FAIL, tested 2026-04-12)
- **linux-driver-007** (was PASS, tested 2026-04-12)
- **linux-driver-008** (was PASS, tested 2026-04-12)
- **linux-driver-009** (was FAIL, tested 2026-04-12)
- **linux-driver-010** (was PASS, tested 2026-04-12)
- **memory-opt-001** (was FAIL, tested 2026-04-12)
- **memory-opt-002** (was FAIL, tested 2026-04-12)
- **memory-opt-003** (was FAIL, tested 2026-04-12)
- **memory-opt-004** (was FAIL, tested 2026-04-12)
- **memory-opt-005** (was FAIL, tested 2026-04-12)
- **memory-opt-006** (was FAIL, tested 2026-04-12)
- **memory-opt-007** (was PASS, tested 2026-04-12)
- **memory-opt-008** (was FAIL, tested 2026-04-12)
- **memory-opt-009** (was PASS, tested 2026-04-12)
- **memory-opt-010** (was PASS, tested 2026-04-12)
- **memory-opt-011** (was PASS, tested 2026-04-12)
- **memory-opt-012** (was FAIL, tested 2026-04-12)
- **networking-001** (was FAIL, tested 2026-04-12)
- **networking-002** (was PASS, tested 2026-04-12)
- **networking-003** (was PASS, tested 2026-04-12)
- **networking-004** (was PASS, tested 2026-04-12)
- **networking-005** (was PASS, tested 2026-04-12)
- **networking-006** (was PASS, tested 2026-04-12)
- **networking-007** (was PASS, tested 2026-04-12)
- **networking-008** (was FAIL, tested 2026-04-12)
- **networking-009** (was FAIL, tested 2026-04-12)
- **networking-010** (was PASS, tested 2026-04-12)
- **ota-001** (was PASS, tested 2026-04-12)
- **ota-002** (was PASS, tested 2026-04-12)
- **ota-003** (was PASS, tested 2026-04-12)
- **ota-004** (was PASS, tested 2026-04-12)
- **ota-005** (was FAIL, tested 2026-04-12)
- **ota-006** (was PASS, tested 2026-04-12)
- **ota-007** (was PASS, tested 2026-04-12)
- **ota-008** (was PASS, tested 2026-04-12)
- **ota-009** (was FAIL, tested 2026-04-12)
- **ota-010** (was FAIL, tested 2026-04-12)
- **ota-011** (was FAIL, tested 2026-04-12)
- **power-mgmt-001** (was PASS, tested 2026-04-12)
- **power-mgmt-002** (was FAIL, tested 2026-04-12)
- **power-mgmt-003** (was PASS, tested 2026-04-12)
- **power-mgmt-004** (was PASS, tested 2026-04-12)
- **power-mgmt-005** (was PASS, tested 2026-04-12)
- **power-mgmt-006** (was PASS, tested 2026-04-12)
- **power-mgmt-007** (was PASS, tested 2026-04-12)
- **power-mgmt-008** (was PASS, tested 2026-04-12)
- **power-mgmt-009** (was FAIL, tested 2026-04-12)
- **power-mgmt-010** (was PASS, tested 2026-04-12)
- **pwm-001** (was PASS, tested 2026-04-12)
- **security-001** (was FAIL, tested 2026-04-12)
- **security-002** (was PASS, tested 2026-04-12)
- **security-003** (was PASS, tested 2026-04-12)
- **security-004** (was FAIL, tested 2026-04-12)
- **security-005** (was PASS, tested 2026-04-12)
- **security-006** (was PASS, tested 2026-04-12)
- **security-007** (was PASS, tested 2026-04-12)
- **security-008** (was FAIL, tested 2026-04-12)
- **security-009** (was PASS, tested 2026-04-12)
- **security-010** (was PASS, tested 2026-04-12)
- **sensor-driver-001** (was PASS, tested 2026-04-12)
- **sensor-driver-002** (was PASS, tested 2026-04-12)
- **sensor-driver-003** (was PASS, tested 2026-04-12)
- **sensor-driver-004** (was PASS, tested 2026-04-12)
- **sensor-driver-005** (was PASS, tested 2026-04-12)
- **sensor-driver-006** (was PASS, tested 2026-04-12)
- **sensor-driver-007** (was PASS, tested 2026-04-12)
- **sensor-driver-008** (was PASS, tested 2026-04-12)
- **sensor-driver-009** (was FAIL, tested 2026-04-12)
- **sensor-driver-010** (was FAIL, tested 2026-04-12)
- **spi-i2c-001** (was PASS, tested 2026-04-12)
- **spi-i2c-002** (was PASS, tested 2026-04-12)
- **spi-i2c-003** (was PASS, tested 2026-04-12)
- **spi-i2c-004** (was PASS, tested 2026-04-12)
- **spi-i2c-005** (was FAIL, tested 2026-04-12)
- **spi-i2c-006** (was PASS, tested 2026-04-12)
- **spi-i2c-007** (was PASS, tested 2026-04-12)
- **spi-i2c-008** (was PASS, tested 2026-04-12)
- **spi-i2c-009** (was FAIL, tested 2026-04-12)
- **spi-i2c-010** (was PASS, tested 2026-04-12)
- **stm32-adc-001** (was FAIL, tested 2026-04-12)
- **stm32-dma-001** (was FAIL, tested 2026-04-12)
- **stm32-freertos-001** (was FAIL, tested 2026-04-12)
- **stm32-freertos-002** (was PASS, tested 2026-04-12)
- **stm32-gpio-001** (was PASS, tested 2026-04-12)
- **stm32-i2c-001** (was FAIL, tested 2026-04-12)
- **stm32-lowpower-001** (was FAIL, tested 2026-04-12)
- **stm32-spi-001** (was FAIL, tested 2026-04-12)
- **stm32-timer-001** (was FAIL, tested 2026-04-12)
- **stm32-uart-001** (was PASS, tested 2026-04-12)
- **storage-001** (was FAIL, tested 2026-04-12)
- **storage-002** (was FAIL, tested 2026-04-12)
- **storage-003** (was PASS, tested 2026-04-12)
- **storage-004** (was FAIL, tested 2026-04-12)
- **storage-005** (was FAIL, tested 2026-04-12)
- **storage-006** (was FAIL, tested 2026-04-12)
- **storage-007** (was PASS, tested 2026-04-12)
- **storage-008** (was FAIL, tested 2026-04-12)
- **storage-009** (was FAIL, tested 2026-04-12)
- **storage-010** (was PASS, tested 2026-04-12)
- **storage-012** (was FAIL, tested 2026-04-12)
- **storage-013** (was FAIL, tested 2026-04-12)
- **threading-001** (was PASS, tested 2026-04-12)
- **threading-002** (was FAIL, tested 2026-04-12)
- **threading-003** (was PASS, tested 2026-04-12)
- **threading-004** (was PASS, tested 2026-04-12)
- **threading-005** (was PASS, tested 2026-04-12)
- **threading-006** (was FAIL, tested 2026-04-12)
- **threading-007** (was FAIL, tested 2026-04-12)
- **threading-008** (was FAIL, tested 2026-04-12)
- **threading-009** (was PASS, tested 2026-04-12)
- **threading-010** (was FAIL, tested 2026-04-12)
- **threading-011** (was FAIL, tested 2026-04-12)
- **threading-012** (was FAIL, tested 2026-04-12)
- **threading-013** (was FAIL, tested 2026-04-12)
- **threading-014** (was FAIL, tested 2026-04-12)
- **timer-001** (was FAIL, tested 2026-04-12)
- **timer-002** (was FAIL, tested 2026-04-12)
- **timer-003** (was PASS, tested 2026-04-12)
- **timer-004** (was FAIL, tested 2026-04-12)
- **timer-005** (was FAIL, tested 2026-04-12)
- **timer-006** (was PASS, tested 2026-04-12)
- **timer-007** (was PASS, tested 2026-04-12)
- **timer-008** (was FAIL, tested 2026-04-12)
- **timer-009** (was PASS, tested 2026-04-12)
- **timer-010** (was PASS, tested 2026-04-12)
- **uart-001** (was PASS, tested 2026-04-12)
- **uart-002** (was PASS, tested 2026-04-12)
- **uart-003** (was FAIL, tested 2026-04-12)
- **watchdog-001** (was FAIL, tested 2026-04-12)
- **watchdog-002** (was PASS, tested 2026-04-12)
- **watchdog-003** (was PASS, tested 2026-04-12)
- **watchdog-004** (was FAIL, tested 2026-04-12)
- **watchdog-005** (was PASS, tested 2026-04-12)
- **watchdog-006** (was PASS, tested 2026-04-12)
- **watchdog-007** (was FAIL, tested 2026-04-12)
- **watchdog-008** (was PASS, tested 2026-04-12)
- **watchdog-009** (was FAIL, tested 2026-04-12)
- **watchdog-010** (was PASS, tested 2026-04-12)
- **yocto-001** (was FAIL, tested 2026-04-12)
- **yocto-002** (was PASS, tested 2026-04-12)
- **yocto-003** (was PASS, tested 2026-04-12)
- **yocto-004** (was PASS, tested 2026-04-12)
- **yocto-005** (was PASS, tested 2026-04-12)
- **yocto-006** (was PASS, tested 2026-04-12)
- **yocto-007** (was FAIL, tested 2026-04-12)
- **yocto-008** (was PASS, tested 2026-04-12)
- **yocto-009** (was FAIL, tested 2026-04-12)
- **yocto-010** (was PASS, tested 2026-04-12)

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 1 | 50% | periodic_read_with_sleep |
| ble | 10 | 4 | 40% | west_build_docker, west_build_docker, security_set_in_connected_cb, conn_cleanup_on_failed_connect, west_build_docker (+1) |
| boot | 9 | 9 | 100% | - |
| boot-uboot | 1 | 1 | 100% | - |
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

| Case | Layer | Failed Checks | Tested | Status |
|------|-------|---------------|--------|--------|
| adc-002 | L3 | periodic_read_with_sleep | 2026-04-12 | RETEST |
| ble-001 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ble-003 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ble-005 | L3 | security_set_in_connected_cb | 2026-04-12 | RETEST |
| ble-008 | L3 | conn_cleanup_on_failed_connect | 2026-04-12 | RETEST |
| ble-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ble-010 | L0 | bt_l2cap_chan_send_used | 2026-04-12 | RETEST |
| dma-001 | L0 | dma_config_called | 2026-04-12 | RETEST |
| dma-002 | L2 | output_validation | 2026-04-12 | RETEST |
| dma-003 | L0 | dma_header_included, cyclic_flag_set, dma_reload_called, dma_config_and_start | 2026-04-12 | RETEST |
| dma-004 | L0 | multiple_block_descriptors | 2026-04-12 | RETEST |
| dma-005 | L0 | dst_buffer_aligned | 2026-04-12 | RETEST |
| dma-006 | L1 | west_build_docker | 2026-04-12 | RETEST |
| dma-007 | L0 | channel_priority_field_used | 2026-04-12 | RETEST |
| dma-008 | L1 | west_build_docker | 2026-04-12 | RETEST |
| dma-009 | L0 | dma_header_included | 2026-04-12 | RETEST |
| dma-010 | L0 | atomic_buffer_index, dma_reload_called | 2026-04-12 | RETEST |
| dma-012 | L0 | cache_flush_before_dma | 2026-04-12 | RETEST |
| esp-adc-001 | L3 | calibration_before_raw_to_voltage, adc_read_error_checked | 2026-04-12 | RETEST |
| esp-i2c-001 | L3 | transmit_receive_used | 2026-04-12 | RETEST |
| esp-ota-001 | L3 | rollback_on_failure | 2026-04-12 | RETEST |
| esp-sleep-001 | L0 | esp_sleep_header, app_main_defined, deep_sleep_used, gpio_wakeup_configured | 2026-04-12 | RETEST |
| gpio-basic-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| isr-concurrency-001 | L0 | uses_atomic_operations, zephyr_headers_included | 2026-04-12 | RETEST |
| isr-concurrency-002 | L2 | output_validation | 2026-04-12 | RETEST |
| isr-concurrency-003 | L3 | k_sleep_present | 2026-04-12 | RETEST |
| isr-concurrency-005 | L0 | init_before_isr_call | 2026-04-12 | RETEST |
| isr-concurrency-006 | L0 | fifo_reserved_field | 2026-04-12 | RETEST |
| isr-concurrency-008 | L3 | memory_barrier_present, barrier_between_data_and_index_update | 2026-04-12 | RETEST |
| isr-concurrency-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| isr-concurrency-011 | L1 | west_build_docker | 2026-04-12 | RETEST |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-12 | RETEST |
| kconfig-003 | L0 | uart_line_ctrl_enabled | 2026-04-12 | RETEST |
| kconfig-005 | L0 | net_sockets_sockopt_tls_enabled, tls_credentials_enabled, mbedtls_builtin_enabled | 2026-04-12 | RETEST |
| kconfig-010 | L0 | mbedtls_psa_crypto_enabled, hw_cc3xx_enabled | 2026-04-12 | RETEST |
| linux-driver-005 | L3 | sysfs_create_group_error_handled | 2026-04-12 | RETEST |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-04-12 | RETEST |
| linux-driver-009 | L0 | gpiod_set_value_used | 2026-04-12 | RETEST |
| memory-opt-001 | L0 | mem_slab_defined, slab_alloc_called, slab_free_called | 2026-04-12 | RETEST |
| memory-opt-002 | L0 | minimal_libc_enabled, newlib_not_enabled | 2026-04-12 | RETEST |
| memory-opt-003 | L0 | slab_defined, slab_alloc_called, slab_free_called | 2026-04-12 | RETEST |
| memory-opt-004 | L0 | thread_analyzer_header, thread_analyzer_config, thread_stack_defined, thread_analyzer_print_called | 2026-04-12 | RETEST |
| memory-opt-005 | L0 | app_memdomain_header | 2026-04-12 | RETEST |
| memory-opt-006 | L0 | config_thread_stack_info_enabled | 2026-04-12 | RETEST |
| memory-opt-008 | L0 | cbprintf_nano_enabled, dynamic_thread_disabled | 2026-04-12 | RETEST |
| memory-opt-012 | L2 | output_validation | 2026-04-12 | RETEST |
| networking-001 | L1 | west_build_docker | 2026-04-12 | RETEST |
| networking-008 | L3 | connect_error_handling | 2026-04-12 | RETEST |
| networking-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-12 | RETEST |
| ota-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ota-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ota-011 | L3 | self_test_failure_branch | 2026-04-12 | RETEST |
| power-mgmt-002 | L3 | multiple_printk_calls | 2026-04-12 | RETEST |
| power-mgmt-009 | L3 | battery_level_printed, periodic_battery_check, multiple_sleep_depths | 2026-04-12 | RETEST |
| security-001 | L1 | west_build_docker | 2026-04-12 | RETEST |
| security-004 | L2 | output_validation | 2026-04-12 | RETEST |
| security-008 | L2 | output_validation | 2026-04-12 | RETEST |
| sensor-driver-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| sensor-driver-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| spi-i2c-005 | L3 | found_count_reported | 2026-04-12 | RETEST |
| spi-i2c-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| stm32-adc-001 | L0 | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used, adc_started_with_dma (+1) | 2026-04-12 | RETEST |
| stm32-dma-001 | L0 | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used, m2m_direction_configured (+1) | 2026-04-12 | RETEST |
| stm32-freertos-001 | L0 | stm32_hal_header_included | 2026-04-12 | RETEST |
| stm32-i2c-001 | L0 | stm32_hal_header_included, i2c_handle_typedef_used, i2c1_instance_configured, hal_i2c_mem_read_used (+1) | 2026-04-12 | RETEST |
| stm32-lowpower-001 | L0 | stm32_hal_header_included | 2026-04-12 | RETEST |
| stm32-spi-001 | L0 | stm32_hal_header_included, spi_handle_typedef_used, spi1_instance_configured, software_nss_used (+1) | 2026-04-12 | RETEST |
| stm32-timer-001 | L0 | stm32_hal_header_included, tim_handle_typedef_used, tim3_instance_used, pwm_start_called (+1) | 2026-04-12 | RETEST |
| storage-001 | L2 | output_validation | 2026-04-12 | RETEST |
| storage-002 | L2 | runtime_started | 2026-04-12 | RETEST |
| storage-004 | L1 | west_build_docker | 2026-04-12 | RETEST |
| storage-005 | L1 | west_build_docker | 2026-04-12 | RETEST |
| storage-006 | L3 | success_printed | 2026-04-12 | RETEST |
| storage-008 | L0 | memcmp_verification | 2026-04-12 | RETEST |
| storage-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| storage-012 | L0 | no_freertos_apis | 2026-04-12 | RETEST |
| storage-013 | L0 | flash_write_rate_limited | 2026-04-12 | RETEST |
| threading-002 | L2 | runtime_started | 2026-04-12 | RETEST |
| threading-006 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-007 | L3 | volatile_on_initialized_flag | 2026-04-12 | RETEST |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-12 | RETEST |
| threading-010 | L0 | k_sem_for_write_exclusion | 2026-04-12 | RETEST |
| threading-011 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-012 | L1 | west_build_docker | 2026-04-12 | RETEST |
| threading-013 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-014 | L0 | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag | 2026-04-12 | RETEST |
| timer-001 | L3 | counter_is_volatile | 2026-04-12 | RETEST |
| timer-002 | L0 | one_shot_period_no_wait | 2026-04-12 | RETEST |
| timer-004 | L3 | main_waits_for_work | 2026-04-12 | RETEST |
| timer-005 | L1 | west_build_docker | 2026-04-12 | RETEST |
| timer-008 | L1 | west_build_docker | 2026-04-12 | RETEST |
| uart-003 | L1 | west_build_docker | 2026-04-12 | RETEST |
| watchdog-001 | L3 | install_before_setup | 2026-04-12 | RETEST |
| watchdog-004 | L0 | two_channels_installed, separate_channel_ids | 2026-04-12 | RETEST |
| watchdog-007 | L3 | wdt_feed_after_flag_check | 2026-04-12 | RETEST |
| watchdog-009 | L0 | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max | 2026-04-12 | RETEST |
| yocto-001 | L0 | summary_defined, license_defined, lic_files_chksum, src_uri_defined (+1) | 2026-04-12 | RETEST |
| yocto-007 | L3 | rootfs_size_uses_weak_assignment | 2026-04-12 | RETEST |
| yocto-009 | L0 | machine_features_defined, kernel_devicetree_defined, serial_consoles_defined, kernel_imagetype_defined | 2026-04-12 | RETEST |

## claude-code://sonnet

### Needs Retest (233)

- **adc-001** (was PASS, tested 2026-04-12)
- **adc-002** (was PASS, tested 2026-04-12)
- **ble-001** (was PASS, tested 2026-04-12)
- **ble-002** (was PASS, tested 2026-04-12)
- **ble-003** (was PASS, tested 2026-04-12)
- **ble-004** (was PASS, tested 2026-04-12)
- **ble-005** (was PASS, tested 2026-04-12)
- **ble-006** (was PASS, tested 2026-04-12)
- **ble-007** (was PASS, tested 2026-04-12)
- **ble-008** (was PASS, tested 2026-04-12)
- **ble-009** (was FAIL, tested 2026-04-12)
- **ble-010** (was FAIL, tested 2026-04-12)
- **boot-001** (was FAIL, tested 2026-04-12)
- **boot-003** (was PASS, tested 2026-04-12)
- **boot-004** (was PASS, tested 2026-04-12)
- **boot-005** (was PASS, tested 2026-04-12)
- **boot-006** (was PASS, tested 2026-04-12)
- **boot-007** (was PASS, tested 2026-04-12)
- **boot-008** (was PASS, tested 2026-04-12)
- **boot-009** (was PASS, tested 2026-04-12)
- **boot-010** (was PASS, tested 2026-04-12)
- **boot-uboot-001** (was PASS, tested 2026-04-12)
- **device-tree-001** (was PASS, tested 2026-04-12)
- **device-tree-002** (was PASS, tested 2026-04-12)
- **device-tree-003** (was PASS, tested 2026-04-12)
- **device-tree-004** (was PASS, tested 2026-04-12)
- **device-tree-005** (was PASS, tested 2026-04-12)
- **device-tree-006** (was PASS, tested 2026-04-12)
- **device-tree-007** (was PASS, tested 2026-04-12)
- **device-tree-008** (was PASS, tested 2026-04-12)
- **device-tree-009** (was PASS, tested 2026-04-12)
- **device-tree-010** (was PASS, tested 2026-04-12)
- **dma-001** (was FAIL, tested 2026-04-12)
- **dma-002** (was FAIL, tested 2026-04-12)
- **dma-003** (was FAIL, tested 2026-04-12)
- **dma-004** (was FAIL, tested 2026-04-12)
- **dma-005** (was PASS, tested 2026-04-12)
- **dma-006** (was PASS, tested 2026-04-12)
- **dma-007** (was FAIL, tested 2026-04-12)
- **dma-008** (was PASS, tested 2026-04-12)
- **dma-009** (was FAIL, tested 2026-04-12)
- **dma-010** (was FAIL, tested 2026-04-12)
- **dma-011** (was FAIL, tested 2026-04-12)
- **dma-012** (was FAIL, tested 2026-04-12)
- **esp-adc-001** (was FAIL, tested 2026-04-12)
- **esp-ble-001** (was PASS, tested 2026-04-12)
- **esp-gpio-001** (was PASS, tested 2026-04-12)
- **esp-i2c-001** (was PASS, tested 2026-04-12)
- **esp-nvs-001** (was FAIL, tested 2026-04-12)
- **esp-ota-001** (was FAIL, tested 2026-04-12)
- **esp-sleep-001** (was FAIL, tested 2026-04-12)
- **esp-spi-001** (was PASS, tested 2026-04-12)
- **esp-timer-001** (was PASS, tested 2026-04-12)
- **esp-wifi-001** (was PASS, tested 2026-04-12)
- **gpio-basic-001** (was FAIL, tested 2026-04-12)
- **gpio-basic-005** (was PASS, tested 2026-04-12)
- **gpio-basic-006** (was PASS, tested 2026-04-12)
- **gpio-basic-010** (was FAIL, tested 2026-04-12)
- **isr-concurrency-001** (was FAIL, tested 2026-04-12)
- **isr-concurrency-002** (was FAIL, tested 2026-04-12)
- **isr-concurrency-003** (was FAIL, tested 2026-04-12)
- **isr-concurrency-004** (was PASS, tested 2026-04-12)
- **isr-concurrency-005** (was FAIL, tested 2026-04-12)
- **isr-concurrency-006** (was FAIL, tested 2026-04-12)
- **isr-concurrency-007** (was PASS, tested 2026-04-12)
- **isr-concurrency-008** (was FAIL, tested 2026-04-12)
- **isr-concurrency-009** (was FAIL, tested 2026-04-12)
- **isr-concurrency-010** (was PASS, tested 2026-04-12)
- **isr-concurrency-011** (was FAIL, tested 2026-04-12)
- **isr-concurrency-012** (was FAIL, tested 2026-04-12)
- **kconfig-001** (was FAIL, tested 2026-04-12)
- **kconfig-002** (was PASS, tested 2026-04-12)
- **kconfig-003** (was PASS, tested 2026-04-12)
- **kconfig-004** (was PASS, tested 2026-04-12)
- **kconfig-005** (was PASS, tested 2026-04-12)
- **kconfig-006** (was PASS, tested 2026-04-12)
- **kconfig-007** (was PASS, tested 2026-04-12)
- **kconfig-008** (was PASS, tested 2026-04-12)
- **kconfig-009** (was PASS, tested 2026-04-12)
- **kconfig-010** (was PASS, tested 2026-04-12)
- **linux-driver-001** (was PASS, tested 2026-04-12)
- **linux-driver-002** (was PASS, tested 2026-04-12)
- **linux-driver-003** (was PASS, tested 2026-04-12)
- **linux-driver-004** (was FAIL, tested 2026-04-12)
- **linux-driver-005** (was PASS, tested 2026-04-12)
- **linux-driver-006** (was FAIL, tested 2026-04-12)
- **linux-driver-007** (was PASS, tested 2026-04-12)
- **linux-driver-008** (was PASS, tested 2026-04-12)
- **linux-driver-009** (was FAIL, tested 2026-04-12)
- **linux-driver-010** (was PASS, tested 2026-04-12)
- **memory-opt-001** (was FAIL, tested 2026-04-12)
- **memory-opt-002** (was PASS, tested 2026-04-12)
- **memory-opt-003** (was FAIL, tested 2026-04-12)
- **memory-opt-004** (was PASS, tested 2026-04-12)
- **memory-opt-005** (was FAIL, tested 2026-04-12)
- **memory-opt-006** (was PASS, tested 2026-04-12)
- **memory-opt-007** (was PASS, tested 2026-04-12)
- **memory-opt-008** (was PASS, tested 2026-04-12)
- **memory-opt-009** (was PASS, tested 2026-04-12)
- **memory-opt-010** (was PASS, tested 2026-04-12)
- **memory-opt-011** (was PASS, tested 2026-04-12)
- **memory-opt-012** (was FAIL, tested 2026-04-12)
- **networking-001** (was PASS, tested 2026-04-12)
- **networking-002** (was PASS, tested 2026-04-12)
- **networking-003** (was PASS, tested 2026-04-12)
- **networking-004** (was PASS, tested 2026-04-12)
- **networking-005** (was PASS, tested 2026-04-12)
- **networking-006** (was PASS, tested 2026-04-12)
- **networking-007** (was PASS, tested 2026-04-12)
- **networking-008** (was FAIL, tested 2026-04-12)
- **networking-009** (was FAIL, tested 2026-04-12)
- **networking-010** (was PASS, tested 2026-04-12)
- **ota-001** (was PASS, tested 2026-04-12)
- **ota-002** (was PASS, tested 2026-04-12)
- **ota-003** (was PASS, tested 2026-04-12)
- **ota-004** (was PASS, tested 2026-04-12)
- **ota-005** (was FAIL, tested 2026-04-12)
- **ota-006** (was PASS, tested 2026-04-12)
- **ota-007** (was PASS, tested 2026-04-12)
- **ota-008** (was PASS, tested 2026-04-12)
- **ota-009** (was PASS, tested 2026-04-12)
- **ota-010** (was FAIL, tested 2026-04-12)
- **ota-011** (was FAIL, tested 2026-04-12)
- **power-mgmt-001** (was PASS, tested 2026-04-12)
- **power-mgmt-002** (was PASS, tested 2026-04-12)
- **power-mgmt-003** (was PASS, tested 2026-04-12)
- **power-mgmt-004** (was PASS, tested 2026-04-12)
- **power-mgmt-005** (was FAIL, tested 2026-04-12)
- **power-mgmt-006** (was PASS, tested 2026-04-12)
- **power-mgmt-007** (was PASS, tested 2026-04-12)
- **power-mgmt-008** (was PASS, tested 2026-04-12)
- **power-mgmt-009** (was FAIL, tested 2026-04-12)
- **power-mgmt-010** (was PASS, tested 2026-04-12)
- **pwm-001** (was PASS, tested 2026-04-12)
- **security-001** (was FAIL, tested 2026-04-12)
- **security-002** (was FAIL, tested 2026-04-12)
- **security-003** (was PASS, tested 2026-04-12)
- **security-004** (was FAIL, tested 2026-04-12)
- **security-005** (was PASS, tested 2026-04-12)
- **security-006** (was PASS, tested 2026-04-12)
- **security-007** (was FAIL, tested 2026-04-12)
- **security-008** (was FAIL, tested 2026-04-12)
- **security-009** (was PASS, tested 2026-04-12)
- **security-010** (was PASS, tested 2026-04-12)
- **sensor-driver-001** (was PASS, tested 2026-04-12)
- **sensor-driver-002** (was PASS, tested 2026-04-12)
- **sensor-driver-003** (was PASS, tested 2026-04-12)
- **sensor-driver-004** (was PASS, tested 2026-04-12)
- **sensor-driver-005** (was PASS, tested 2026-04-12)
- **sensor-driver-006** (was PASS, tested 2026-04-12)
- **sensor-driver-007** (was PASS, tested 2026-04-12)
- **sensor-driver-008** (was PASS, tested 2026-04-12)
- **sensor-driver-009** (was FAIL, tested 2026-04-12)
- **sensor-driver-010** (was FAIL, tested 2026-04-12)
- **spi-i2c-001** (was PASS, tested 2026-04-12)
- **spi-i2c-002** (was PASS, tested 2026-04-12)
- **spi-i2c-003** (was PASS, tested 2026-04-12)
- **spi-i2c-004** (was PASS, tested 2026-04-12)
- **spi-i2c-005** (was PASS, tested 2026-04-12)
- **spi-i2c-006** (was PASS, tested 2026-04-12)
- **spi-i2c-007** (was PASS, tested 2026-04-12)
- **spi-i2c-008** (was PASS, tested 2026-04-12)
- **spi-i2c-009** (was FAIL, tested 2026-04-12)
- **spi-i2c-010** (was PASS, tested 2026-04-12)
- **stm32-adc-001** (was PASS, tested 2026-04-12)
- **stm32-dma-001** (was PASS, tested 2026-04-12)
- **stm32-freertos-001** (was FAIL, tested 2026-04-12)
- **stm32-freertos-002** (was FAIL, tested 2026-04-12)
- **stm32-gpio-001** (was PASS, tested 2026-04-12)
- **stm32-i2c-001** (was FAIL, tested 2026-04-12)
- **stm32-lowpower-001** (was PASS, tested 2026-04-12)
- **stm32-spi-001** (was FAIL, tested 2026-04-12)
- **stm32-timer-001** (was FAIL, tested 2026-04-12)
- **stm32-uart-001** (was FAIL, tested 2026-04-12)
- **storage-001** (was PASS, tested 2026-04-12)
- **storage-002** (was FAIL, tested 2026-04-12)
- **storage-003** (was PASS, tested 2026-04-12)
- **storage-004** (was PASS, tested 2026-04-12)
- **storage-005** (was FAIL, tested 2026-04-12)
- **storage-006** (was PASS, tested 2026-04-12)
- **storage-007** (was PASS, tested 2026-04-12)
- **storage-008** (was FAIL, tested 2026-04-12)
- **storage-009** (was FAIL, tested 2026-04-12)
- **storage-010** (was PASS, tested 2026-04-12)
- **storage-012** (was FAIL, tested 2026-04-12)
- **storage-013** (was PASS, tested 2026-04-12)
- **threading-001** (was FAIL, tested 2026-04-12)
- **threading-002** (was PASS, tested 2026-04-12)
- **threading-003** (was PASS, tested 2026-04-12)
- **threading-004** (was PASS, tested 2026-04-12)
- **threading-005** (was PASS, tested 2026-04-12)
- **threading-006** (was FAIL, tested 2026-04-12)
- **threading-007** (was FAIL, tested 2026-04-12)
- **threading-008** (was FAIL, tested 2026-04-12)
- **threading-009** (was PASS, tested 2026-04-12)
- **threading-010** (was FAIL, tested 2026-04-12)
- **threading-011** (was FAIL, tested 2026-04-12)
- **threading-012** (was FAIL, tested 2026-04-12)
- **threading-013** (was FAIL, tested 2026-04-12)
- **threading-014** (was FAIL, tested 2026-04-12)
- **timer-001** (was FAIL, tested 2026-04-12)
- **timer-002** (was PASS, tested 2026-04-12)
- **timer-003** (was PASS, tested 2026-04-12)
- **timer-004** (was PASS, tested 2026-04-12)
- **timer-005** (was PASS, tested 2026-04-12)
- **timer-006** (was PASS, tested 2026-04-12)
- **timer-007** (was PASS, tested 2026-04-12)
- **timer-008** (was PASS, tested 2026-04-12)
- **timer-009** (was PASS, tested 2026-04-12)
- **timer-010** (was PASS, tested 2026-04-12)
- **uart-001** (was PASS, tested 2026-04-12)
- **uart-002** (was FAIL, tested 2026-04-12)
- **uart-003** (was FAIL, tested 2026-04-12)
- **watchdog-001** (was PASS, tested 2026-04-12)
- **watchdog-002** (was PASS, tested 2026-04-12)
- **watchdog-003** (was PASS, tested 2026-04-12)
- **watchdog-004** (was PASS, tested 2026-04-12)
- **watchdog-005** (was PASS, tested 2026-04-12)
- **watchdog-006** (was PASS, tested 2026-04-12)
- **watchdog-007** (was PASS, tested 2026-04-12)
- **watchdog-008** (was PASS, tested 2026-04-12)
- **watchdog-009** (was FAIL, tested 2026-04-12)
- **watchdog-010** (was PASS, tested 2026-04-12)
- **yocto-001** (was FAIL, tested 2026-04-12)
- **yocto-002** (was PASS, tested 2026-04-12)
- **yocto-003** (was PASS, tested 2026-04-12)
- **yocto-004** (was PASS, tested 2026-04-12)
- **yocto-005** (was PASS, tested 2026-04-12)
- **yocto-006** (was PASS, tested 2026-04-12)
- **yocto-007** (was FAIL, tested 2026-04-12)
- **yocto-008** (was PASS, tested 2026-04-12)
- **yocto-009** (was PASS, tested 2026-04-12)
- **yocto-010** (was PASS, tested 2026-04-12)

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| adc | 2 | 2 | 100% | - |
| ble | 10 | 8 | 80% | west_build_docker, west_build_docker |
| boot | 9 | 8 | 89% | img_manager_dependency |
| boot-uboot | 1 | 1 | 100% | - |
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

| Case | Layer | Failed Checks | Tested | Status |
|------|-------|---------------|--------|--------|
| ble-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ble-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| boot-001 | L3 | img_manager_dependency | 2026-04-12 | RETEST |
| dma-001 | L1 | west_build_docker | 2026-04-12 | RETEST |
| dma-002 | L1 | west_build_docker | 2026-04-12 | RETEST |
| dma-003 | L0 | cyclic_flag_set | 2026-04-12 | RETEST |
| dma-004 | L2 | output_validation | 2026-04-12 | RETEST |
| dma-007 | L2 | output_validation | 2026-04-12 | RETEST |
| dma-009 | L3 | dma_config_after_stop | 2026-04-12 | RETEST |
| dma-010 | L0 | dma_reload_called | 2026-04-12 | RETEST |
| dma-011 | L0 | single_dma_start | 2026-04-12 | RETEST |
| dma-012 | L0 | cache_flush_before_dma | 2026-04-12 | RETEST |
| esp-adc-001 | L3 | adc_read_error_checked | 2026-04-12 | RETEST |
| esp-nvs-001 | L3 | nvs_set_error_checked | 2026-04-12 | RETEST |
| esp-ota-001 | L3 | firmware_validation | 2026-04-12 | RETEST |
| esp-sleep-001 | L3 | gpio_pull_configured | 2026-04-12 | RETEST |
| gpio-basic-001 | L3 | device_ready_check | 2026-04-12 | RETEST |
| gpio-basic-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| isr-concurrency-001 | L0 | no_printk | 2026-04-12 | RETEST |
| isr-concurrency-002 | L2 | output_validation | 2026-04-12 | RETEST |
| isr-concurrency-003 | L3 | k_sleep_present | 2026-04-12 | RETEST |
| isr-concurrency-005 | L2 | output_validation | 2026-04-12 | RETEST |
| isr-concurrency-006 | L2 | output_validation | 2026-04-12 | RETEST |
| isr-concurrency-008 | L3 | memory_barrier_present, barrier_between_data_and_index_update | 2026-04-12 | RETEST |
| isr-concurrency-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| isr-concurrency-011 | L2 | output_validation | 2026-04-12 | RETEST |
| isr-concurrency-012 | L1 | west_build_docker | 2026-04-12 | RETEST |
| kconfig-001 | L0 | spi_dma_enabled | 2026-04-12 | RETEST |
| linux-driver-004 | L3 | init_error_path_cleanup | 2026-04-12 | RETEST |
| linux-driver-006 | L3 | init_error_path_cleanup | 2026-04-12 | RETEST |
| linux-driver-009 | L0 | gpio_direction_set | 2026-04-12 | RETEST |
| memory-opt-001 | L2 | output_validation | 2026-04-12 | RETEST |
| memory-opt-003 | L2 | output_validation | 2026-04-12 | RETEST |
| memory-opt-005 | L0 | partition_added_to_domain | 2026-04-12 | RETEST |
| memory-opt-012 | L3 | no_large_string_literals | 2026-04-12 | RETEST |
| networking-008 | L3 | connect_error_handling | 2026-04-12 | RETEST |
| networking-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ota-005 | L3 | rollback_abort_on_download_error, rollback_on_error | 2026-04-12 | RETEST |
| ota-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| ota-011 | L3 | self_test_failure_branch | 2026-04-12 | RETEST |
| power-mgmt-005 | L3 | all_three_devices_suspended | 2026-04-12 | RETEST |
| power-mgmt-009 | L3 | periodic_battery_check | 2026-04-12 | RETEST |
| security-001 | L2 | output_validation | 2026-04-12 | RETEST |
| security-002 | L2 | output_validation | 2026-04-12 | RETEST |
| security-004 | L2 | output_validation | 2026-04-12 | RETEST |
| security-007 | L3 | error_path_returns_early | 2026-04-12 | RETEST |
| security-008 | L2 | output_validation | 2026-04-12 | RETEST |
| sensor-driver-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| sensor-driver-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| spi-i2c-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| stm32-freertos-001 | L3 | different_task_priorities | 2026-04-12 | RETEST |
| stm32-freertos-002 | L0 | stm32_hal_header_included | 2026-04-12 | RETEST |
| stm32-i2c-001 | L0 | hal_i2c_mem_read_used | 2026-04-12 | RETEST |
| stm32-spi-001 | L3 | cs_deasserted_after_transfer | 2026-04-12 | RETEST |
| stm32-timer-001 | L3 | timer_clock_before_init | 2026-04-12 | RETEST |
| stm32-uart-001 | L3 | receive_it_rearmed_in_callback | 2026-04-12 | RETEST |
| storage-002 | L2 | output_validation | 2026-04-12 | RETEST |
| storage-005 | L2 | output_validation | 2026-04-12 | RETEST |
| storage-008 | L3 | write_verify_commit_order, verify_before_commit, delete_after_commit | 2026-04-12 | RETEST |
| storage-009 | L1 | west_build_docker | 2026-04-12 | RETEST |
| storage-012 | L3 | write_rate_limited | 2026-04-12 | RETEST |
| threading-001 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-006 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-007 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-008 | L3 | deadline_constant_not_magic | 2026-04-12 | RETEST |
| threading-010 | L1 | west_build_docker | 2026-04-12 | RETEST |
| threading-011 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-012 | L1 | west_build_docker | 2026-04-12 | RETEST |
| threading-013 | L2 | output_validation | 2026-04-12 | RETEST |
| threading-014 | L0 | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag | 2026-04-12 | RETEST |
| timer-001 | L2 | output_validation | 2026-04-12 | RETEST |
| uart-002 | L3 | callback_before_rx_enable | 2026-04-12 | RETEST |
| uart-003 | L1 | west_build_docker | 2026-04-12 | RETEST |
| watchdog-009 | L0 | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max | 2026-04-12 | RETEST |
| yocto-001 | L0 | summary_defined, license_defined, lic_files_chksum, src_uri_defined (+1) | 2026-04-12 | RETEST |
| yocto-007 | L3 | rootfs_size_uses_weak_assignment | 2026-04-12 | RETEST |

## mock

### Needs Retest (8)

- **boot-001** (was FAIL, tested 2026-03-29)
- **boot-003** (was FAIL, tested 2026-03-29)
- **boot-004** (was FAIL, tested 2026-03-29)
- **boot-005** (was FAIL, tested 2026-03-29)
- **boot-006** (was FAIL, tested 2026-03-29)
- **boot-007** (was FAIL, tested 2026-03-29)
- **boot-008** (was FAIL, tested 2026-03-29)
- **boot-uboot-001** (was FAIL, tested 2026-03-29)

| Category | Cases | Passed | pass@1 | Failed Checks |
|----------|-------|--------|--------|---------------|
| boot | 7 | 0 | 0% | kconfig_format, mcuboot_enabled, img_manager_enabled, kconfig_format, mcuboot_enabled (+16) |
| boot-uboot | 1 | 0 | 0% | kconfig_format, boot_delay_set, cmd_env_enabled |

### Failed Cases (8)

| Case | Layer | Failed Checks | Tested | Status |
|------|-------|---------------|--------|--------|
| boot-001 | L0 | kconfig_format, mcuboot_enabled, img_manager_enabled, flash_enabled | 2026-03-29 | RETEST |
| boot-003 | L0 | kconfig_format, mcuboot_enabled, rsa_signature_type, signature_key_file (+1) | 2026-03-29 | RETEST |
| boot-004 | L0 | kconfig_format, mcuboot_enabled, swap_using_move_enabled, max_img_sectors_set | 2026-03-29 | RETEST |
| boot-005 | L0 | kconfig_format, mcuboot_enabled, boot_image_number_2, pcd_app_enabled | 2026-03-29 | RETEST |
| boot-006 | L0 | kconfig_format, boot_encrypt_image_enabled, boot_encrypt_rsa_enabled, boot_signature_type_rsa_enabled | 2026-03-29 | RETEST |
| boot-007 | L0 | kconfig_format, mcuboot_serial_enabled, boot_serial_cdc_acm_enabled, usb_device_stack_enabled | 2026-03-29 | RETEST |
| boot-008 | L0 | kconfig_format, mcuboot_enabled, boot_version_cmp_build_number_enabled, boot_validate_slot0_enabled | 2026-03-29 | RETEST |
| boot-uboot-001 | L0 | kconfig_format, boot_delay_set, cmd_env_enabled | 2026-03-29 | RETEST |

