# Benchmark Report: claude-code://haiku

**Date:** 2026-04-11 09:59 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://haiku |
| Total Cases | 63 |
| Passed | 30 |
| Failed | 33 |
| pass@1 | 47.6% |

## Failed Cases (33)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `ble-009` | ble | compile_gate | west_build_docker |
| `ble-010` | ble | static_analysis | bt_l2cap_chan_send_used |
| `dma-010` | dma | static_analysis | dma_reload_called |
| `dma-011` | dma | static_analysis | block_count_three |
| `dma-012` | dma | static_analysis | dma_header_included, cache_flush_before_dma |
| `esp-adc-001` | sensor-driver | static_heuristic | calibration_before_raw_to_voltage, adc_read_error_checked |
| `esp-ota-001` | ota | static_heuristic | rollback_on_failure, firmware_validation, error_handling_present |
| `esp-sleep-001` | power-mgmt | static_analysis | esp_sleep_header, app_main_defined, deep_sleep_used, gpio_wakeup_configured |
| `gpio-basic-010` | gpio-basic | compile_gate | west_build_docker |
| `isr-concurrency-009` | isr-concurrency | compile_gate | west_build_docker |
| `kconfig-010` | kconfig | static_analysis | mbedtls_builtin_enabled, mbedtls_psa_crypto_enabled, hw_cc3xx_enabled |
| `networking-008` | networking | static_heuristic | connect_error_handling |
| `networking-009` | networking | compile_gate | west_build_docker |
| `ota-010` | ota | compile_gate | west_build_docker |
| `ota-011` | ota | static_heuristic | self_test_failure_branch |
| `power-mgmt-009` | power-mgmt | static_heuristic | battery_level_printed, periodic_battery_check, multiple_sleep_depths |
| `security-002` | security | runtime_execution | runtime_started |
| `security-004` | security | runtime_execution | output_validation |
| `security-008` | security | runtime_execution | output_validation |
| `security-009` | security | static_analysis | return_value_checked |
| `sensor-driver-009` | sensor-driver | compile_gate | west_build_docker |
| `sensor-driver-010` | sensor-driver | compile_gate | west_build_docker |
| `spi-i2c-009` | spi-i2c | compile_gate | west_build_docker |
| `stm32-adc-001` | sensor-driver | static_analysis | stm32_hal_header_included, adc_handle_typedef_used, dma_handle_typedef_used, adc_started_with_dma, adc_12bit_resolution |
| `stm32-dma-001` | dma | static_analysis | stm32_hal_header_included, dma_handle_typedef_used, dma2_stream0_used, m2m_direction_configured, dma_start_it_used |
| `stm32-lowpower-001` | power-mgmt | static_analysis | stm32_hal_header_included, stop_mode_api_used, rtc_handle_typedef_used, rtc_alarm_interrupt_used, wfi_entry_mode_specified |
| `stm32-timer-001` | timer | static_analysis | stm32_hal_header_included, tim_handle_typedef_used, tim3_instance_used, pwm_start_called, timer_clock_enabled |
| `storage-009` | storage | static_analysis | zero_size_check |
| `threading-001` | threading | static_heuristic | different_thread_priorities |
| `threading-014` | threading | static_analysis | explicit_memory_barrier, shared_flag_volatile, consumer_waits_for_flag |
| `uart-003` | uart | compile_gate | west_build_docker |
| `watchdog-009` | watchdog | static_analysis | window_min_greater_than_zero, window_max_greater_than_zero, window_min_less_than_max, wdt_configured |
| `yocto-009` | yocto | static_analysis | machine_features_defined, kernel_devicetree_defined, serial_consoles_defined, kernel_imagetype_defined |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 9 | ble-009, gpio-basic-010, isr-concurrency-009, networking-009, ota-010 (+4 more) |
| `stm32_hal_header_included` | 4 | stm32-adc-001, stm32-dma-001, stm32-lowpower-001, stm32-timer-001 |
| `output_validation` | 2 | security-004, security-008 |
| `dma_handle_typedef_used` | 2 | stm32-adc-001, stm32-dma-001 |
| `block_count_three` | 1 | dma-011 |
| `dma_header_included` | 1 | dma-012 |
| `cache_flush_before_dma` | 1 | dma-012 |
| `connect_error_handling` | 1 | networking-008 |
| `self_test_failure_branch` | 1 | ota-011 |
| `runtime_started` | 1 | security-002 |
| `different_thread_priorities` | 1 | threading-001 |
| `explicit_memory_barrier` | 1 | threading-014 |
| `shared_flag_volatile` | 1 | threading-014 |
| `consumer_waits_for_flag` | 1 | threading-014 |
| `bt_l2cap_chan_send_used` | 1 | ble-010 |
| `dma_reload_called` | 1 | dma-010 |
| `calibration_before_raw_to_voltage` | 1 | esp-adc-001 |
| `adc_read_error_checked` | 1 | esp-adc-001 |
| `rollback_on_failure` | 1 | esp-ota-001 |
| `firmware_validation` | 1 | esp-ota-001 |
| `error_handling_present` | 1 | esp-ota-001 |
| `esp_sleep_header` | 1 | esp-sleep-001 |
| `app_main_defined` | 1 | esp-sleep-001 |
| `deep_sleep_used` | 1 | esp-sleep-001 |
| `gpio_wakeup_configured` | 1 | esp-sleep-001 |
| `mbedtls_builtin_enabled` | 1 | kconfig-010 |
| `mbedtls_psa_crypto_enabled` | 1 | kconfig-010 |
| `hw_cc3xx_enabled` | 1 | kconfig-010 |
| `battery_level_printed` | 1 | power-mgmt-009 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `multiple_sleep_depths` | 1 | power-mgmt-009 |
| `return_value_checked` | 1 | security-009 |
| `adc_handle_typedef_used` | 1 | stm32-adc-001 |
| `adc_started_with_dma` | 1 | stm32-adc-001 |
| `adc_12bit_resolution` | 1 | stm32-adc-001 |
| `dma2_stream0_used` | 1 | stm32-dma-001 |
| `m2m_direction_configured` | 1 | stm32-dma-001 |
| `dma_start_it_used` | 1 | stm32-dma-001 |
| `stop_mode_api_used` | 1 | stm32-lowpower-001 |
| `rtc_handle_typedef_used` | 1 | stm32-lowpower-001 |
| `rtc_alarm_interrupt_used` | 1 | stm32-lowpower-001 |
| `wfi_entry_mode_specified` | 1 | stm32-lowpower-001 |
| `tim_handle_typedef_used` | 1 | stm32-timer-001 |
| `tim3_instance_used` | 1 | stm32-timer-001 |
| `pwm_start_called` | 1 | stm32-timer-001 |
| `timer_clock_enabled` | 1 | stm32-timer-001 |
| `zero_size_check` | 1 | storage-009 |
| `window_min_greater_than_zero` | 1 | watchdog-009 |
| `window_max_greater_than_zero` | 1 | watchdog-009 |
| `window_min_less_than_max` | 1 | watchdog-009 |
| `wdt_configured` | 1 | watchdog-009 |
| `machine_features_defined` | 1 | yocto-009 |
| `kernel_devicetree_defined` | 1 | yocto-009 |
| `serial_consoles_defined` | 1 | yocto-009 |
| `kernel_imagetype_defined` | 1 | yocto-009 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 27 | dma-011, dma-012, networking-008, ota-011, security-002 (+22 more) |
| LLM format failure (prose) | 6 | esp-sleep-001, stm32-adc-001, stm32-dma-001, stm32-lowpower-001, stm32-timer-001, yocto-009 |

*Adjusted pass@1 (excluding format failures): 52.6% (30/57)*


## TC Improvement Suggestions

