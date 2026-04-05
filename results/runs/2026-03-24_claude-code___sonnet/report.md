# Benchmark Report: claude-code://sonnet

**Date:** 2026-03-24 05:00 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 200 |
| Passed | 179 |
| Failed | 21 |
| pass@1 | 89.5% |

## Failed Cases (21)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `dma-003` | dma | behavioral_assertion | cyclic_enabled |
| `gpio-basic-001` | gpio-basic | behavioral_assertion | device_ready_check |
| `isr-concurrency-004` | isr-concurrency | behavioral_assertion | k_sleep_present |
| `linux-driver-001` | linux-driver | behavioral_assertion | init_error_path_cleanup |
| `linux-driver-004` | linux-driver | behavioral_assertion | init_error_path_cleanup |
| `linux-driver-006` | linux-driver | behavioral_assertion | init_error_path_cleanup |
| `memory-opt-001` | memory-opt | behavioral_assertion | block_size_defined |
| `memory-opt-003` | memory-opt | behavioral_assertion | heap_alloc_free_balanced, slab_alloc_free_balanced |
| `networking-001` | networking | behavioral_assertion | connect_error_handling |
| `networking-008` | networking | behavioral_assertion | connect_error_handling |
| `ota-003` | ota | behavioral_assertion | init_error_handling, write_error_handling |
| `ota-005` | ota | behavioral_assertion | rollback_abort_on_download_error |
| `power-mgmt-001` | power-mgmt | behavioral_assertion | pm_error_handling |
| `power-mgmt-009` | power-mgmt | behavioral_assertion | periodic_battery_check |
| `security-007` | security | behavioral_assertion | error_path_returns_early |
| `sensor-driver-003` | sensor-driver | behavioral_assertion | periodic_loop |
| `storage-002` | storage | behavioral_assertion | init_before_save_load, register_before_load, save_before_load |
| `storage-009` | storage | static_analysis | offset_plus_size_boundary_check |
| `threading-005` | threading | behavioral_assertion | stack_size_adequate |
| `timer-007` | timer | behavioral_assertion | timer_period_less_than_wdt_timeout |
| `watchdog-007` | watchdog | behavioral_assertion | device_ready_check |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `init_error_path_cleanup` | 3 | linux-driver-001, linux-driver-004, linux-driver-006 |
| `device_ready_check` | 2 | gpio-basic-001, watchdog-007 |
| `connect_error_handling` | 2 | networking-001, networking-008 |
| `cyclic_enabled` | 1 | dma-003 |
| `k_sleep_present` | 1 | isr-concurrency-004 |
| `block_size_defined` | 1 | memory-opt-001 |
| `heap_alloc_free_balanced` | 1 | memory-opt-003 |
| `slab_alloc_free_balanced` | 1 | memory-opt-003 |
| `init_error_handling` | 1 | ota-003 |
| `write_error_handling` | 1 | ota-003 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `pm_error_handling` | 1 | power-mgmt-001 |
| `periodic_battery_check` | 1 | power-mgmt-009 |
| `error_path_returns_early` | 1 | security-007 |
| `periodic_loop` | 1 | sensor-driver-003 |
| `init_before_save_load` | 1 | storage-002 |
| `register_before_load` | 1 | storage-002 |
| `save_before_load` | 1 | storage-002 |
| `offset_plus_size_boundary_check` | 1 | storage-009 |
| `stack_size_adequate` | 1 | threading-005 |
| `timer_period_less_than_wdt_timeout` | 1 | timer-007 |

## TC Improvement Suggestions

