# Benchmark Report: claude-code://haiku

**Date:** 2026-03-29 15:17 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 179 |
| Passed | 61 |
| Failed | 118 |
| pass@1 | 34.1% |

## Failed Cases (118)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `adc-001` | adc | compile_gate | west_build_docker |
| `adc-002` | adc | compile_gate | west_build_docker |
| `ble-001` | ble | runtime_execution | output_validation |
| `ble-002` | ble | compile_gate | west_build_docker |
| `ble-003` | ble | compile_gate | west_build_docker |
| `ble-004` | ble | compile_gate | west_build_docker |
| `ble-005` | ble | compile_gate | west_build_docker |
| `ble-006` | ble | compile_gate | west_build_docker |
| `ble-007` | ble | runtime_execution | output_validation |
| `ble-008` | ble | compile_gate | west_build_docker |
| `device-tree-003` | device-tree | static_heuristic | pwm_polarity_specified |
| `dma-001` | dma | static_analysis | dma_header_included, dma_config_called |
| `dma-002` | dma | static_analysis | dma_config_called |
| `dma-003` | dma | static_analysis | cyclic_flag_set, dma_reload_called, dma_config_and_start |
| `dma-004` | dma | static_analysis | dma_header_included, multiple_block_descriptors |
| `dma-005` | dma | static_analysis | cache_flush_present, cache_invalidate_present, dst_buffer_aligned |
| `dma-006` | dma | compile_gate | west_build_docker |
| `dma-007` | dma | static_analysis | channel_priority_field_used |
| `dma-008` | dma | compile_gate | west_build_docker |
| `dma-009` | dma | compile_gate | west_build_docker |
| `esp-i2c-001` | spi-i2c | static_analysis | i2c_master_header, i2c_master_new_api, no_legacy_i2c_driver, no_zephyr_apis |
| `isr-concurrency-001` | isr-concurrency | static_analysis | zephyr_headers_included |
| `isr-concurrency-002` | isr-concurrency | static_analysis | no_printk_in_isr |
| `isr-concurrency-003` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-004` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-005` | isr-concurrency | static_analysis | init_before_isr_call |
| `isr-concurrency-006` | isr-concurrency | static_analysis | fifo_reserved_field |
| `isr-concurrency-007` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `kconfig-003` | kconfig | static_analysis | uart_line_ctrl_enabled |
| `linux-driver-002` | linux-driver | static_heuristic | of_match_table_sentinel |
| `linux-driver-006` | linux-driver | static_heuristic | init_error_path_cleanup |
| `memory-opt-001` | memory-opt | static_analysis | mem_slab_defined, slab_alloc_called, slab_free_called |
| `memory-opt-002` | memory-opt | compile_gate | west_build_docker |
| `memory-opt-003` | memory-opt | static_analysis | slab_defined, slab_alloc_called, slab_free_called |
| `memory-opt-004` | memory-opt | static_analysis | thread_analyzer_header, thread_analyzer_print_called |
| `memory-opt-005` | memory-opt | static_analysis | app_memdomain_header, partition_defined |
| `memory-opt-006` | memory-opt | compile_gate | west_build_docker |
| `memory-opt-007` | memory-opt | runtime_execution | output_validation |
| `memory-opt-008` | memory-opt | static_analysis | cbprintf_nano_enabled, dynamic_thread_disabled |
| `memory-opt-011` | memory-opt | runtime_execution | output_validation |
| `memory-opt-012` | memory-opt | compile_gate | west_build_docker |
| `networking-001` | networking | compile_gate | west_build_docker |
| `networking-002` | networking | runtime_execution | output_validation |
| `networking-003` | networking | runtime_execution | output_validation |
| `networking-004` | networking | compile_gate | west_build_docker |
| `networking-005` | networking | compile_gate | west_build_docker |
| `networking-006` | networking | runtime_execution | output_validation |
| `networking-007` | networking | compile_gate | west_build_docker |
| `networking-008` | networking | compile_gate | west_build_docker |
| `ota-003` | ota | compile_gate | west_build_docker |
| `ota-004` | ota | compile_gate | west_build_docker |
| `ota-005` | ota | compile_gate | west_build_docker |
| `ota-006` | ota | compile_gate | west_build_docker |
| `ota-007` | ota | compile_gate | west_build_docker |
| `ota-008` | ota | compile_gate | west_build_docker |
| `power-mgmt-002` | power-mgmt | static_heuristic | k_sleep_with_k_msec, multiple_printk_calls |
| `power-mgmt-003` | power-mgmt | compile_gate | west_build_docker |
| `power-mgmt-004` | power-mgmt | compile_gate | west_build_docker |
| `power-mgmt-005` | power-mgmt | static_analysis | pm_action_run_called |
| `power-mgmt-008` | power-mgmt | compile_gate | west_build_docker |
| `pwm-001` | pwm | compile_gate | west_build_docker |
| `security-001` | security | compile_gate | west_build_docker |
| `security-002` | security | runtime_execution | output_validation |
| `security-004` | security | runtime_execution | output_validation |
| `security-005` | security | compile_gate | west_build_docker |
| `security-006` | security | runtime_execution | output_validation |
| `security-007` | security | compile_gate | west_build_docker |
| `security-008` | security | runtime_execution | output_validation |
| `sensor-driver-001` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-002` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-003` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-004` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-005` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-006` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-007` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-008` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-002` | spi-i2c | compile_gate | west_build_docker |
| `spi-i2c-004` | spi-i2c | compile_gate | west_build_docker |
| `spi-i2c-005` | spi-i2c | static_heuristic | found_count_reported |
| `spi-i2c-007` | spi-i2c | compile_gate | west_build_docker |
| `stm32-i2c-001` | spi-i2c | static_analysis | hal_i2c_mem_read_used |
| `stm32-uart-001` | networking | static_analysis | interrupt_receive_used |
| `storage-001` | storage | runtime_execution | output_validation |
| `storage-002` | storage | runtime_execution | runtime_started |
| `storage-003` | storage | compile_gate | west_build_docker |
| `storage-004` | storage | runtime_execution | output_validation |
| `storage-005` | storage | compile_gate | west_build_docker |
| `storage-006` | storage | static_heuristic | success_printed |
| `storage-007` | storage | compile_gate | west_build_docker |
| `storage-008` | storage | compile_gate | west_build_docker |
| `storage-012` | storage | compile_gate | west_build_docker |
| `threading-001` | threading | static_heuristic | different_thread_priorities |
| `threading-002` | threading | runtime_execution | output_validation |
| `threading-004` | threading | compile_gate | west_build_docker |
| `threading-005` | threading | compile_gate | west_build_docker |
| `threading-006` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-008` | threading | runtime_execution | output_validation |
| `threading-011` | threading | compile_gate | west_build_docker |
| `threading-012` | threading | static_analysis | kernel_header_included, thread_created, has_main_function |
| `threading-013` | threading | static_analysis | kernel_header_included, main_function_present, struct_definition_present |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-002` | timer | static_heuristic | main_sleeps_after_start |
| `timer-003` | timer | compile_gate | west_build_docker |
| `timer-005` | timer | runtime_execution | output_validation |
| `timer-006` | timer | compile_gate | west_build_docker |
| `timer-007` | timer | compile_gate | west_build_docker |
| `uart-001` | uart | compile_gate | west_build_docker |
| `uart-002` | uart | compile_gate | west_build_docker |
| `watchdog-001` | watchdog | compile_gate | west_build_docker |
| `watchdog-002` | watchdog | compile_gate | west_build_docker |
| `watchdog-004` | watchdog | compile_gate | west_build_docker |
| `watchdog-005` | watchdog | static_analysis | health_flag_is_volatile |
| `watchdog-006` | watchdog | compile_gate | west_build_docker |
| `watchdog-010` | watchdog | static_analysis | kernel_header_included, watchdog_header_included, persistent_storage_header_included, printk_present |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 61 | adc-001, adc-002, ble-002, ble-003, ble-004 (+56 more) |
| `output_validation` | 22 | ble-001, ble-007, isr-concurrency-003, isr-concurrency-004, isr-concurrency-008 (+17 more) |
| `kernel_header_included` | 3 | threading-012, threading-013, watchdog-010 |
| `dma_header_included` | 2 | dma-001, dma-004 |
| `dma_config_called` | 2 | dma-001, dma-002 |
| `slab_alloc_called` | 2 | memory-opt-001, memory-opt-003 |
| `slab_free_called` | 2 | memory-opt-001, memory-opt-003 |
| `pwm_polarity_specified` | 1 | device-tree-003 |
| `cyclic_flag_set` | 1 | dma-003 |
| `dma_reload_called` | 1 | dma-003 |
| `dma_config_and_start` | 1 | dma-003 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `cache_flush_present` | 1 | dma-005 |
| `cache_invalidate_present` | 1 | dma-005 |
| `dst_buffer_aligned` | 1 | dma-005 |
| `channel_priority_field_used` | 1 | dma-007 |
| `i2c_master_header` | 1 | esp-i2c-001 |
| `i2c_master_new_api` | 1 | esp-i2c-001 |
| `no_legacy_i2c_driver` | 1 | esp-i2c-001 |
| `no_zephyr_apis` | 1 | esp-i2c-001 |
| `zephyr_headers_included` | 1 | isr-concurrency-001 |
| `no_printk_in_isr` | 1 | isr-concurrency-002 |
| `init_before_isr_call` | 1 | isr-concurrency-005 |
| `fifo_reserved_field` | 1 | isr-concurrency-006 |
| `uart_line_ctrl_enabled` | 1 | kconfig-003 |
| `of_match_table_sentinel` | 1 | linux-driver-002 |
| `init_error_path_cleanup` | 1 | linux-driver-006 |
| `mem_slab_defined` | 1 | memory-opt-001 |
| `slab_defined` | 1 | memory-opt-003 |
| `thread_analyzer_header` | 1 | memory-opt-004 |
| `thread_analyzer_print_called` | 1 | memory-opt-004 |
| `app_memdomain_header` | 1 | memory-opt-005 |
| `partition_defined` | 1 | memory-opt-005 |
| `cbprintf_nano_enabled` | 1 | memory-opt-008 |
| `dynamic_thread_disabled` | 1 | memory-opt-008 |
| `k_sleep_with_k_msec` | 1 | power-mgmt-002 |
| `multiple_printk_calls` | 1 | power-mgmt-002 |
| `pm_action_run_called` | 1 | power-mgmt-005 |
| `found_count_reported` | 1 | spi-i2c-005 |
| `hal_i2c_mem_read_used` | 1 | stm32-i2c-001 |
| `interrupt_receive_used` | 1 | stm32-uart-001 |
| `runtime_started` | 1 | storage-002 |
| `success_printed` | 1 | storage-006 |
| `different_thread_priorities` | 1 | threading-001 |
| `thread_created` | 1 | threading-012 |
| `has_main_function` | 1 | threading-012 |
| `main_function_present` | 1 | threading-013 |
| `struct_definition_present` | 1 | threading-013 |
| `counter_is_volatile` | 1 | timer-001 |
| `main_sleeps_after_start` | 1 | timer-002 |
| `health_flag_is_volatile` | 1 | watchdog-005 |
| `watchdog_header_included` | 1 | watchdog-010 |
| `persistent_storage_header_included` | 1 | watchdog-010 |
| `printk_present` | 1 | watchdog-010 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |

## TC Improvement Suggestions

