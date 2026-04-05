# Benchmark Report: claude-code://haiku

**Date:** 2026-03-28 23:24 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 179 |
| Passed | 126 |
| Failed | 53 |
| pass@1 | 70.4% |

## Failed Cases (53)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-008` | ble | static_heuristic | bt_enable_before_scan |
| `device-tree-003` | device-tree | static_heuristic | pwm_polarity_specified |
| `dma-002` | dma | static_analysis | dma_config_called |
| `dma-003` | dma | static_analysis | cyclic_flag_set, dma_reload_called, dma_config_and_start |
| `dma-004` | dma | static_analysis | block_count_set, multiple_block_descriptors |
| `dma-005` | dma | static_analysis | cache_flush_present, cache_invalidate_present |
| `dma-006` | dma | static_analysis | dma_header_included |
| `dma-007` | dma | static_analysis | channel_priority_field_used, two_dma_config_calls |
| `dma-008` | dma | static_heuristic | error_flag_is_volatile, error_flag_checked_after_wait, callback_sets_flag_on_error_status, error_flag_causes_return, error_flag_read_after_sync |
| `dma-009` | dma | static_heuristic | dma_start_called_twice |
| `esp-gpio-001` | gpio-basic | static_heuristic | vtaskdelay_used, tick_conversion_macro |
| `esp-i2c-001` | spi-i2c | static_analysis | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver |
| `isr-concurrency-002` | isr-concurrency | static_analysis | no_printk_in_isr |
| `isr-concurrency-003` | isr-concurrency | static_heuristic | k_sleep_present, no_forbidden_apis_in_isr |
| `isr-concurrency-005` | isr-concurrency | static_heuristic | work_handler_does_processing, k_sleep_for_drain |
| `isr-concurrency-006` | isr-concurrency | static_analysis | fifo_reserved_field |
| `isr-concurrency-008` | isr-concurrency | static_heuristic | memory_barrier_present, barrier_between_data_and_index_update |
| `kconfig-005` | kconfig | static_analysis | tls_credentials_enabled |
| `linux-driver-002` | linux-driver | static_heuristic | of_match_table_sentinel |
| `linux-driver-005` | linux-driver | static_heuristic | sysfs_create_group_error_handled |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-008` | linux-driver | static_heuristic | proc_create_failure_returns_error |
| `memory-opt-001` | memory-opt | static_analysis | mem_slab_defined, slab_alloc_called, slab_free_called |
| `memory-opt-002` | memory-opt | static_analysis | main_stack_size_defined, minimal_libc_enabled |
| `memory-opt-003` | memory-opt | static_heuristic | slab_alloc_error_check |
| `memory-opt-004` | memory-opt | static_analysis | thread_analyzer_header, thread_analyzer_config, thread_analyzer_print_called |
| `memory-opt-005` | memory-opt | static_analysis | app_memdomain_header, mem_domain_declared, mem_domain_init_called, partition_added_to_domain, thread_added_to_domain |
| `memory-opt-008` | memory-opt | static_analysis | cbprintf_nano_enabled, dynamic_thread_disabled |
| `memory-opt-012` | memory-opt | static_heuristic | no_large_string_literals |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `power-mgmt-001` | power-mgmt | static_heuristic | pm_action_run_called |
| `power-mgmt-002` | power-mgmt | static_heuristic | k_sleep_with_k_msec |
| `power-mgmt-005` | power-mgmt | static_analysis | pm_action_run_called |
| `sensor-driver-001` | sensor-driver | static_heuristic | sensor_error_handling, periodic_read_loop |
| `sensor-driver-003` | sensor-driver | static_heuristic | error_handling |
| `spi-i2c-005` | spi-i2c | static_heuristic | found_count_reported |
| `stm32-freertos-001` | threading | static_heuristic | different_task_priorities |
| `stm32-i2c-001` | spi-i2c | static_analysis | hal_i2c_mem_read_used |
| `stm32-uart-001` | networking | static_analysis | interrupt_receive_used |
| `storage-006` | storage | static_heuristic | success_printed |
| `storage-008` | storage | static_analysis | memcmp_verification |
| `threading-006` | threading | static_heuristic | lock_order_a_before_b, unlock_order_b_before_a |
| `threading-007` | threading | static_heuristic | volatile_on_initialized_flag |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `threading-011` | threading | static_heuristic | deadline_miss_detected, deadline_miss_action |
| `threading-012` | threading | static_heuristic | inter_thread_communication, priority_differentiation, uart_output_1s_interval |
| `threading-013` | threading | static_heuristic | shared_memory_struct |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-004` | timer | static_heuristic | main_waits_for_work |
| `timer-006` | timer | static_heuristic | alarm_value_is_volatile |
| `watchdog-004` | watchdog | static_heuristic | distinct_channel_timeouts |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `pm_action_run_called` | 2 | power-mgmt-001, power-mgmt-005 |
| `bt_enable_before_scan` | 1 | ble-008 |
| `pwm_polarity_specified` | 1 | device-tree-003 |
| `dma_config_called` | 1 | dma-002 |
| `cyclic_flag_set` | 1 | dma-003 |
| `dma_reload_called` | 1 | dma-003 |
| `dma_config_and_start` | 1 | dma-003 |
| `block_count_set` | 1 | dma-004 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `cache_flush_present` | 1 | dma-005 |
| `cache_invalidate_present` | 1 | dma-005 |
| `dma_header_included` | 1 | dma-006 |
| `channel_priority_field_used` | 1 | dma-007 |
| `two_dma_config_calls` | 1 | dma-007 |
| `error_flag_is_volatile` | 1 | dma-008 |
| `error_flag_checked_after_wait` | 1 | dma-008 |
| `callback_sets_flag_on_error_status` | 1 | dma-008 |
| `error_flag_causes_return` | 1 | dma-008 |
| `error_flag_read_after_sync` | 1 | dma-008 |
| `dma_start_called_twice` | 1 | dma-009 |
| `vtaskdelay_used` | 1 | esp-gpio-001 |
| `tick_conversion_macro` | 1 | esp-gpio-001 |
| `i2c_master_header` | 1 | esp-i2c-001 |
| `i2c_master_new_api` | 1 | esp-i2c-001 |
| `no_legacy_i2c_driver` | 1 | esp-i2c-001 |
| `no_printk_in_isr` | 1 | isr-concurrency-002 |
| `k_sleep_present` | 1 | isr-concurrency-003 |
| `no_forbidden_apis_in_isr` | 1 | isr-concurrency-003 |
| `work_handler_does_processing` | 1 | isr-concurrency-005 |
| `k_sleep_for_drain` | 1 | isr-concurrency-005 |
| `fifo_reserved_field` | 1 | isr-concurrency-006 |
| `memory_barrier_present` | 1 | isr-concurrency-008 |
| `barrier_between_data_and_index_update` | 1 | isr-concurrency-008 |
| `tls_credentials_enabled` | 1 | kconfig-005 |
| `of_match_table_sentinel` | 1 | linux-driver-002 |
| `sysfs_create_group_error_handled` | 1 | linux-driver-005 |
| `init_error_path_cleanup` | 1 | linux-driver-006 |
| `proc_create_failure_returns_error` | 1 | linux-driver-008 |
| `mem_slab_defined` | 1 | memory-opt-001 |
| `slab_alloc_called` | 1 | memory-opt-001 |
| `slab_free_called` | 1 | memory-opt-001 |
| `main_stack_size_defined` | 1 | memory-opt-002 |
| `minimal_libc_enabled` | 1 | memory-opt-002 |
| `slab_alloc_error_check` | 1 | memory-opt-003 |
| `thread_analyzer_header` | 1 | memory-opt-004 |
| `thread_analyzer_config` | 1 | memory-opt-004 |
| `thread_analyzer_print_called` | 1 | memory-opt-004 |
| `app_memdomain_header` | 1 | memory-opt-005 |
| `mem_domain_declared` | 1 | memory-opt-005 |
| `mem_domain_init_called` | 1 | memory-opt-005 |
| `partition_added_to_domain` | 1 | memory-opt-005 |
| `thread_added_to_domain` | 1 | memory-opt-005 |
| `cbprintf_nano_enabled` | 1 | memory-opt-008 |
| `dynamic_thread_disabled` | 1 | memory-opt-008 |
| `no_large_string_literals` | 1 | memory-opt-012 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `k_sleep_with_k_msec` | 1 | power-mgmt-002 |
| `sensor_error_handling` | 1 | sensor-driver-001 |
| `periodic_read_loop` | 1 | sensor-driver-001 |
| `error_handling` | 1 | sensor-driver-003 |
| `found_count_reported` | 1 | spi-i2c-005 |
| `different_task_priorities` | 1 | stm32-freertos-001 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `interrupt_receive_used` | 1 | stm32-uart-001 |
| `success_printed` | 1 | storage-006 |
| `memcmp_verification` | 1 | storage-008 |
| `lock_order_a_before_b` | 1 | threading-006 |
| `unlock_order_b_before_a` | 1 | threading-006 |
| `volatile_on_initialized_flag` | 1 | threading-007 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `deadline_miss_detected` | 1 | threading-011 |
| `deadline_miss_action` | 1 | threading-011 |
| `inter_thread_communication` | 1 | threading-012 |
| `priority_differentiation` | 1 | threading-012 |
| `uart_output_1s_interval` | 1 | threading-012 |
| `shared_memory_struct` | 1 | threading-013 |
| `counter_is_volatile` | 1 | timer-001 |
| `main_waits_for_work` | 1 | timer-004 |
| `alarm_value_is_volatile` | 1 | timer-006 |
| `distinct_channel_timeouts` | 1 | watchdog-004 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |

## TC Improvement Suggestions

