# Benchmark Report: claude-code://claude-sonnet-5

**Date:** 2026-07-19 08:59 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://claude-sonnet-5 |
| Total Cases | 265 |
| Passed | 178 |
| Failed | 87 |
| pass@1 | 67.2% |

## Failed Cases (87)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-006` | ble | static_heuristic | auth_state_reset_on_disconnect |
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | compile_gate | west_build_docker |
| `device-tree-003` | device-tree | static_heuristic | period_20ms, pwm_polarity_specified |
| `dma-002` | dma | runtime_execution | runtime_started |
| `dma-003` | dma | static_analysis | cyclic_flag_set, dma_reload_called |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-007` | dma | static_analysis | two_dma_config_calls |
| `dma-008` | dma | static_heuristic | error_flag_is_volatile, callback_sets_flag_on_error_status, error_flag_causes_return, error_flag_read_after_sync |
| `dma-009` | dma | static_heuristic | dma_config_after_stop, timeout_mechanism_present |
| `dma-010` | dma | static_analysis | dma_reload_called |
| `dma-011` | dma | static_analysis | single_dma_start |
| `dma-012` | dma | static_analysis | cache_flush_before_dma |
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
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `kconfig-002` | kconfig | static_analysis | bt_hci_enabled |
| `kconfig-006` | kconfig | static_analysis | kconfig_format, stack_canaries_enabled, hw_stack_protection_enabled, secure_boot_enabled |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-009` | linux-driver | static_heuristic | isr_uses_spin_lock_irqsave |
| `linux-driver-010` | linux-driver | static_heuristic | isr_uses_spin_lock_irqsave |
| `linux-driver-013` | linux-driver | static_analysis | of_header_included, mod_devicetable_header_included |
| `linux-driver-016` | linux-driver | static_heuristic | is_err_guards_reset_control_get |
| `linux-userspace-006` | linux-userspace | static_heuristic | open_spidev0_0_rdwr |
| `linux-userspace-008` | linux-userspace | static_heuristic | comm_array_size_16_bytes |
| `memory-opt-001` | memory-opt | runtime_execution | output_validation |
| `memory-opt-003` | memory-opt | runtime_execution | output_validation |
| `memory-opt-006` | memory-opt | static_analysis | config_thread_stack_info_enabled |
| `memory-opt-007` | memory-opt | runtime_execution | output_validation |
| `memory-opt-012` | memory-opt | runtime_execution | output_validation |
| `networking-001` | networking | compile_gate | west_build_docker |
| `networking-006` | networking | static_heuristic | connection_closed_check |
| `networking-008` | networking | static_heuristic | will_configured_before_connect, connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `networking-kernel-002` | networking | static_heuristic | producer_uses_skb_clone, skb_clone_uses_gfp_atomic, skb_clone_return_null_checked, exit_cancels_work_then_purges_queue |
| `networking-kernel-003` | networking | static_heuristic | input_cb_uses_nlmsg_hdr, input_cb_sends_netlink_unicast, module_scope_sock_declared |
| `networking-kernel-004` | networking | static_analysis | skbuff_header_included |
| `ota-003` | ota | static_heuristic | done_after_write |
| `ota-006` | ota | static_heuristic | dfu_done_false_on_mismatch |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `ota-swupdate-002` | ota | static_heuristic | two_selection_groups_copy_1_copy_2, copy_1_has_three_images, copy_2_has_three_images, selection_groups_have_distinct_devices, all_image_entries_have_sha256 |
| `ota-swupdate-003` | ota | static_heuristic | hardware_compatibility_present, sha256_values_64_lowercase_hex |
| `power-mgmt-009` | power-mgmt | compile_gate | west_build_docker |
| `security-001` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-007` | security | static_heuristic | error_path_returns_early |
| `security-008` | security | runtime_execution | output_validation |
| `security-010` | security | compile_gate | west_build_docker |
| `sensor-driver-003` | sensor-driver | static_heuristic | error_handling |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-i2c-001` | spi-i2c | static_heuristic | i2c_address_left_shifted |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-004` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, verify_before_commit, delete_after_commit |
| `storage-009` | storage | compile_gate | west_build_docker |
| `storage-012` | storage | static_heuristic | write_rate_limited |
| `threading-001` | threading | static_heuristic | different_thread_priorities, queue_capacity_positive |
| `threading-004` | threading | static_heuristic | mutex_holder_sleeps_while_locked |
| `threading-006` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | runtime_execution | output_validation |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-007` | timer | static_heuristic | timer_period_less_than_wdt_timeout |
| `timer-009` | timer | compile_gate | west_build_docker |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-001` | watchdog | static_heuristic | setup_before_feed |
| `watchdog-004` | watchdog | static_heuristic | distinct_channel_timeouts |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max |
| `yocto-003` | yocto | static_analysis | summary_defined, license_defined, inherit_systemd, systemd_service_var, service_in_src_uri, do_install_defined |
| `yocto-005` | yocto | static_analysis | summary_defined, inherit_module, src_uri_defined, kernel_module_autoload, lic_files_chksum |
| `yocto-006` | yocto | static_analysis | patch_file_in_src_uri, filesextrapaths_set, lic_files_chksum_defined |
| `yocto-007` | yocto | static_analysis | inherits_core_image, image_install_defined, image_features_defined, summary_defined |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `output_validation` | 17 | isr-concurrency-002, isr-concurrency-006, isr-concurrency-008, memory-opt-001, memory-opt-003 (+12 more) |
| `west_build_docker` | 16 | networking-001, threading-012, ble-009, ble-010, gpio-basic-010 (+11 more) |
| `summary_defined` | 3 | yocto-003, yocto-005, yocto-007 |
| `isr_uses_spin_lock_irqsave` | 2 | linux-driver-009, linux-driver-010 |
| `dma_reload_called` | 2 | dma-003, dma-010 |
| `init_error_path_cleanup` | 1 | linux-driver-006 |
| `of_header_included` | 1 | linux-driver-013 |
| `mod_devicetable_header_included` | 1 | linux-driver-013 |
| `is_err_guards_reset_control_get` | 1 | linux-driver-016 |
| `open_spidev0_0_rdwr` | 1 | linux-userspace-006 |
| `comm_array_size_16_bytes` | 1 | linux-userspace-008 |
| `producer_uses_skb_clone` | 1 | networking-kernel-002 |
| `skb_clone_uses_gfp_atomic` | 1 | networking-kernel-002 |
| `skb_clone_return_null_checked` | 1 | networking-kernel-002 |
| `exit_cancels_work_then_purges_queue` | 1 | networking-kernel-002 |
| `input_cb_uses_nlmsg_hdr` | 1 | networking-kernel-003 |
| `input_cb_sends_netlink_unicast` | 1 | networking-kernel-003 |
| `module_scope_sock_declared` | 1 | networking-kernel-003 |
| `skbuff_header_included` | 1 | networking-kernel-004 |
| `two_selection_groups_copy_1_copy_2` | 1 | ota-swupdate-002 |
| `copy_1_has_three_images` | 1 | ota-swupdate-002 |
| `copy_2_has_three_images` | 1 | ota-swupdate-002 |
| `selection_groups_have_distinct_devices` | 1 | ota-swupdate-002 |
| `all_image_entries_have_sha256` | 1 | ota-swupdate-002 |
| `hardware_compatibility_present` | 1 | ota-swupdate-003 |
| `sha256_values_64_lowercase_hex` | 1 | ota-swupdate-003 |
| `license_defined` | 1 | yocto-003 |
| `inherit_systemd` | 1 | yocto-003 |
| `systemd_service_var` | 1 | yocto-003 |
| `service_in_src_uri` | 1 | yocto-003 |
| `do_install_defined` | 1 | yocto-003 |
| `inherit_module` | 1 | yocto-005 |
| `src_uri_defined` | 1 | yocto-005 |
| `kernel_module_autoload` | 1 | yocto-005 |
| `lic_files_chksum` | 1 | yocto-005 |
| `patch_file_in_src_uri` | 1 | yocto-006 |
| `filesextrapaths_set` | 1 | yocto-006 |
| `lic_files_chksum_defined` | 1 | yocto-006 |
| `inherits_core_image` | 1 | yocto-007 |
| `image_install_defined` | 1 | yocto-007 |
| `image_features_defined` | 1 | yocto-007 |
| `nvs_initialized_before_wifi` | 1 | esp-wifi-001 |
| `i2c_address_left_shifted` | 1 | stm32-i2c-001 |
| `auth_state_reset_on_disconnect` | 1 | ble-006 |
| `period_20ms` | 1 | device-tree-003 |
| `pwm_polarity_specified` | 1 | device-tree-003 |
| `runtime_started` | 1 | dma-002 |
| `cyclic_flag_set` | 1 | dma-003 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `two_dma_config_calls` | 1 | dma-007 |
| `error_flag_is_volatile` | 1 | dma-008 |
| `callback_sets_flag_on_error_status` | 1 | dma-008 |
| `error_flag_causes_return` | 1 | dma-008 |
| `error_flag_read_after_sync` | 1 | dma-008 |
| `dma_config_after_stop` | 1 | dma-009 |
| `timeout_mechanism_present` | 1 | dma-009 |
| `single_dma_start` | 1 | dma-011 |
| `cache_flush_before_dma` | 1 | dma-012 |
| `no_printk` | 1 | isr-concurrency-001 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `init_before_isr_call` | 1 | isr-concurrency-005 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `bt_hci_enabled` | 1 | kconfig-002 |
| `kconfig_format` | 1 | kconfig-006 |
| `stack_canaries_enabled` | 1 | kconfig-006 |
| `hw_stack_protection_enabled` | 1 | kconfig-006 |
| `secure_boot_enabled` | 1 | kconfig-006 |
| `config_thread_stack_info_enabled` | 1 | memory-opt-006 |
| `connection_closed_check` | 1 | networking-006 |
| `will_configured_before_connect` | 1 | networking-008 |
| `connect_error_handling` | 1 | networking-008 |
| `done_after_write` | 1 | ota-003 |
| `dfu_done_false_on_mismatch` | 1 | ota-006 |
| `self_test_failure_branch` | 1 | ota-011 |
| `error_path_returns_early` | 1 | security-007 |
| `error_handling` | 1 | sensor-driver-003 |
| `write_verify_commit_order` | 1 | storage-008 |
| `verify_before_commit` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `write_rate_limited` | 1 | storage-012 |
| `different_thread_priorities` | 1 | threading-001 |
| `queue_capacity_positive` | 1 | threading-001 |
| `mutex_holder_sleeps_while_locked` | 1 | threading-004 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `counter_is_volatile` | 1 | timer-001 |
| `timer_period_less_than_wdt_timeout` | 1 | timer-007 |
| `setup_before_feed` | 1 | watchdog-001 |
| `distinct_channel_timeouts` | 1 | watchdog-004 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 81 | linux-driver-006, linux-driver-009, linux-driver-010, linux-driver-013, linux-driver-016 (+76 more) |
| LLM format failure (prose) | 6 | ota-swupdate-002, ota-swupdate-003, yocto-003, yocto-006, yocto-007, kconfig-006 |

*Adjusted pass@1 (excluding format failures): 68.7% (178/259)*


## TC Improvement Suggestions

