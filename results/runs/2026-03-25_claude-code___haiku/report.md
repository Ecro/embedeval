# Benchmark Report: claude-code://haiku

**Date:** 2026-03-25 04:24 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 210 |
| Passed | 164 |
| Failed | 46 |
| pass@1 | 78.1% |

## Failed Cases (46)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-001` | ble | static_heuristic | read_write_characteristic |
| `ble-008` | ble | static_heuristic | conn_cleanup_on_failed_connect |
| `ble-009` | ble | static_heuristic | bt_enable_before_bond_ops, settings_load_before_foreach_bond, bond_count_tracked |
| `device-tree-001` | device-tree | static_heuristic | interrupt_gpio_present |
| `device-tree-003` | device-tree | static_heuristic | pwm_polarity_specified |
| `device-tree-005` | device-tree | static_analysis | sufficient_node_count |
| `device-tree-010` | device-tree | static_heuristic | gpio_leds_compatible, gpio_keys_compatible |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-006` | dma | static_heuristic | both_src_dst_buffers_present |
| `dma-008` | dma | static_heuristic | error_flag_checked_after_wait, callback_sets_flag_on_error_status, error_flag_read_after_sync |
| `esp-adc-001` | sensor-driver | static_heuristic | calibration_before_raw_to_voltage, adc_read_error_checked |
| `esp-i2c-001` | spi-i2c | static_heuristic | transmit_receive_used |
| `esp-ota-001` | ota | static_heuristic | rollback_on_failure, firmware_validation |
| `gpio-basic-004` | gpio-basic | static_heuristic | duty_cycle_varies |
| `gpio-basic-007` | gpio-basic | static_heuristic | rx_buffer_nonzero |
| `gpio-basic-008` | gpio-basic | static_heuristic | periodic_read_with_sleep |
| `isr-concurrency-001` | isr-concurrency | static_analysis | no_printk |
| `isr-concurrency-003` | isr-concurrency | static_analysis | shared_variable_declared |
| `isr-concurrency-006` | isr-concurrency | static_heuristic | k_fifo_get_not_in_isr |
| `isr-concurrency-008` | isr-concurrency | static_heuristic | memory_barrier_present, barrier_between_data_and_index_update |
| `linux-driver-002` | linux-driver | static_heuristic | of_match_table_sentinel |
| `linux-driver-005` | linux-driver | static_heuristic | sysfs_create_group_error_handled |
| `memory-opt-001` | memory-opt | static_heuristic | block_size_defined |
| `memory-opt-007` | memory-opt | static_heuristic | bounds_check_in_free |
| `networking-007` | networking | static_heuristic | timeout_not_infinite |
| `networking-008` | networking | static_heuristic | will_configured_before_connect, connect_error_handling |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error |
| `power-mgmt-001` | power-mgmt | static_heuristic | pm_error_handling |
| `power-mgmt-004` | power-mgmt | static_heuristic | return_values_checked |
| `power-mgmt-009` | power-mgmt | static_heuristic | battery_level_printed, periodic_battery_check |
| `security-002` | security | static_heuristic | hash_length_captured |
| `sensor-driver-001` | sensor-driver | static_heuristic | sensor_error_handling |
| `sensor-driver-003` | sensor-driver | static_heuristic | periodic_loop, error_handling |
| `spi-i2c-004` | spi-i2c | static_heuristic | write_enable_before_write, poll_loop_bounded |
| `spi-i2c-005` | spi-i2c | static_heuristic | found_count_reported |
| `spi-i2c-006` | spi-i2c | static_heuristic | error_message_printed |
| `spi-i2c-009` | spi-i2c | static_heuristic | different_cs_pins_per_device |
| `storage-001` | storage | static_heuristic | nvs_error_handling |
| `storage-004` | storage | static_heuristic | error_handling |
| `storage-008` | storage | static_analysis | memcmp_verification |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `timer-001` | timer | static_heuristic | counter_is_volatile |
| `timer-002` | timer | static_heuristic | main_sleeps_after_start |
| `timer-006` | timer | static_heuristic | alarm_value_is_volatile, counter_stopped_after_use |
| `timer-007` | timer | static_heuristic | timer_period_less_than_wdt_timeout |
| `yocto-007` | yocto | static_heuristic | rootfs_size_uses_weak_assignment |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `error_handling` | 2 | sensor-driver-003, storage-004 |
| `read_write_characteristic` | 1 | ble-001 |
| `conn_cleanup_on_failed_connect` | 1 | ble-008 |
| `bt_enable_before_bond_ops` | 1 | ble-009 |
| `settings_load_before_foreach_bond` | 1 | ble-009 |
| `bond_count_tracked` | 1 | ble-009 |
| `interrupt_gpio_present` | 1 | device-tree-001 |
| `pwm_polarity_specified` | 1 | device-tree-003 |
| `sufficient_node_count` | 1 | device-tree-005 |
| `gpio_leds_compatible` | 1 | device-tree-010 |
| `gpio_keys_compatible` | 1 | device-tree-010 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `both_src_dst_buffers_present` | 1 | dma-006 |
| `error_flag_checked_after_wait` | 1 | dma-008 |
| `callback_sets_flag_on_error_status` | 1 | dma-008 |
| `error_flag_read_after_sync` | 1 | dma-008 |
| `calibration_before_raw_to_voltage` | 1 | esp-adc-001 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `transmit_receive_used` | 1 | esp-i2c-001 |
| `rollback_on_failure` | 1 | esp-ota-001 |
| `firmware_validation` | 1 | esp-ota-001 |
| `duty_cycle_varies` | 1 | gpio-basic-004 |
| `rx_buffer_nonzero` | 1 | gpio-basic-007 |
| `periodic_read_with_sleep` | 1 | gpio-basic-008 |
| `no_printk` | 1 | isr-concurrency-001 |
| `shared_variable_declared` | 1 | isr-concurrency-003 |
| `k_fifo_get_not_in_isr` | 1 | isr-concurrency-006 |
| `memory_barrier_present` | 1 | isr-concurrency-008 |
| `barrier_between_data_and_index_update` | 1 | isr-concurrency-008 |
| `of_match_table_sentinel` | 1 | linux-driver-002 |
| `sysfs_create_group_error_handled` | 1 | linux-driver-005 |
| `block_size_defined` | 1 | memory-opt-001 |
| `bounds_check_in_free` | 1 | memory-opt-007 |
| `timeout_not_infinite` | 1 | networking-007 |
| `will_configured_before_connect` | 1 | networking-008 |
| `connect_error_handling` | 1 | networking-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `pm_error_handling` | 1 | power-mgmt-001 |
| `return_values_checked` | 1 | power-mgmt-004 |
| `battery_level_printed` | 1 | power-mgmt-009 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `hash_length_captured` | 1 | security-002 |
| `sensor_error_handling` | 1 | sensor-driver-001 |
| `periodic_loop` | 1 | sensor-driver-003 |
| `write_enable_before_write` | 1 | spi-i2c-004 |
| `poll_loop_bounded` | 1 | spi-i2c-004 |
| `found_count_reported` | 1 | spi-i2c-005 |
| `error_message_printed` | 1 | spi-i2c-006 |
| `different_cs_pins_per_device` | 1 | spi-i2c-009 |
| `nvs_error_handling` | 1 | storage-001 |
| `memcmp_verification` | 1 | storage-008 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `counter_is_volatile` | 1 | timer-001 |
| `main_sleeps_after_start` | 1 | timer-002 |
| `alarm_value_is_volatile` | 1 | timer-006 |
| `counter_stopped_after_use` | 1 | timer-006 |
| `timer_period_less_than_wdt_timeout` | 1 | timer-007 |
| `rootfs_size_uses_weak_assignment` | 1 | yocto-007 |

## TC Improvement Suggestions

