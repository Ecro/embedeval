# Benchmark Report: claude-code://sonnet

**Date:** 2026-03-29 03:28 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 179 |
| Passed | 152 |
| Failed | 27 |
| pass@1 | 84.9% |

## Failed Cases (27)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `dma-003` | dma | static_analysis | cyclic_flag_set |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `gpio-basic-001` | gpio-basic | static_heuristic | device_ready_check |
| `isr-concurrency-002` | isr-concurrency | static_heuristic | message_struct_defined, no_forbidden_apis_in_isr |
| `isr-concurrency-003` | isr-concurrency | static_analysis | k_spinlock_used, k_spin_lock_called, spinlock_key_saved, k_spin_unlock_called, shared_variable_declared |
| `isr-concurrency-005` | isr-concurrency | static_heuristic | isr_submits_work, work_handler_does_processing, atomic_counter_in_isr, k_sleep_for_drain |
| `isr-concurrency-008` | isr-concurrency | static_heuristic | memory_barrier_present, barrier_between_data_and_index_update |
| `isr-concurrency-011` | isr-concurrency | static_heuristic | isr_signals_via_semaphore |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `linux-driver-004` | linux-driver | static_heuristic | init_error_path_cleanup |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `memory-opt-005` | memory-opt | static_analysis | partition_added_to_domain |
| `memory-opt-012` | memory-opt | static_heuristic | no_large_string_literals |
| `networking-008` | networking | static_heuristic | will_configured_before_connect, connect_error_handling |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `stm32-freertos-001` | threading | static_analysis | stm32_hal_header_included |
| `stm32-spi-001` | spi-i2c | static_heuristic | spi_clock_before_init |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, verify_before_commit, delete_after_commit |
| `threading-001` | threading | static_heuristic | different_thread_priorities, queue_capacity_positive |
| `threading-004` | threading | static_heuristic | mutex_holder_sleeps_while_locked |
| `threading-007` | threading | static_heuristic | volatile_on_initialized_flag |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `threading-012` | threading | static_heuristic | inter_thread_communication, priority_differentiation, periodic_sensor_read, uart_output_1s_interval |
| `threading-013` | threading | static_heuristic | volatile_on_shared_flags, handshake_mechanism, flag_cleared_after_read, data_before_flag |
| `timer-002` | timer | static_heuristic | main_sleeps_after_start |
| `watchdog-004` | watchdog | static_heuristic | distinct_channel_timeouts |
| `watchdog-007` | watchdog | static_heuristic | device_ready_check |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `device_ready_check` | 2 | gpio-basic-001, watchdog-007 |
| `init_error_path_cleanup` | 2 | linux-driver-004, linux-driver-006 |
| `cyclic_flag_set` | 1 | dma-003 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `message_struct_defined` | 1 | isr-concurrency-002 |
| `no_forbidden_apis_in_isr` | 1 | isr-concurrency-002 |
| `k_spinlock_used` | 1 | isr-concurrency-003 |
| `k_spin_lock_called` | 1 | isr-concurrency-003 |
| `spinlock_key_saved` | 1 | isr-concurrency-003 |
| `k_spin_unlock_called` | 1 | isr-concurrency-003 |
| `shared_variable_declared` | 1 | isr-concurrency-003 |
| `isr_submits_work` | 1 | isr-concurrency-005 |
| `work_handler_does_processing` | 1 | isr-concurrency-005 |
| `atomic_counter_in_isr` | 1 | isr-concurrency-005 |
| `k_sleep_for_drain` | 1 | isr-concurrency-005 |
| `memory_barrier_present` | 1 | isr-concurrency-008 |
| `barrier_between_data_and_index_update` | 1 | isr-concurrency-008 |
| `isr_signals_via_semaphore` | 1 | isr-concurrency-011 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `partition_added_to_domain` | 1 | memory-opt-005 |
| `no_large_string_literals` | 1 | memory-opt-012 |
| `will_configured_before_connect` | 1 | networking-008 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `stm32_hal_header_included` | 1 | stm32-freertos-001 |
| `spi_clock_before_init` | 1 | stm32-spi-001 |
| `write_verify_commit_order` | 1 | storage-008 |
| `verify_before_commit` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `different_thread_priorities` | 1 | threading-001 |
| `queue_capacity_positive` | 1 | threading-001 |
| `mutex_holder_sleeps_while_locked` | 1 | threading-004 |
| `volatile_on_initialized_flag` | 1 | threading-007 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `inter_thread_communication` | 1 | threading-012 |
| `priority_differentiation` | 1 | threading-012 |
| `periodic_sensor_read` | 1 | threading-012 |
| `uart_output_1s_interval` | 1 | threading-012 |
| `volatile_on_shared_flags` | 1 | threading-013 |
| `handshake_mechanism` | 1 | threading-013 |
| `flag_cleared_after_read` | 1 | threading-013 |
| `data_before_flag` | 1 | threading-013 |
| `main_sleeps_after_start` | 1 | timer-002 |
| `distinct_channel_timeouts` | 1 | watchdog-004 |

## TC Improvement Suggestions

