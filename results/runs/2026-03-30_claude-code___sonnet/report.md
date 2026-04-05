# Benchmark Report: claude-code://sonnet

**Date:** 2026-03-30 11:14 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 120 |
| Passed | 27 |
| Failed | 93 |
| pass@1 | 22.5% |

## Failed Cases (93)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `adc-001` | adc | compile_gate | west_build_docker |
| `adc-002` | adc | compile_gate | west_build_docker |
| `ble-001` | ble | runtime_execution | output_validation |
| `ble-002` | ble | compile_gate | west_build_docker |
| `ble-003` | ble | runtime_execution | output_validation |
| `ble-004` | ble | runtime_execution | output_validation |
| `ble-005` | ble | compile_gate | west_build_docker |
| `ble-006` | ble | compile_gate | west_build_docker |
| `ble-007` | ble | runtime_execution | output_validation |
| `ble-008` | ble | compile_gate | west_build_docker |
| `dma-001` | dma | compile_gate | west_build_docker |
| `dma-002` | dma | compile_gate | west_build_docker |
| `dma-003` | dma | runtime_execution | output_validation |
| `dma-004` | dma | static_analysis | multiple_block_descriptors |
| `dma-007` | dma | static_analysis | channel_priority_field_used |
| `dma-008` | dma | compile_gate | west_build_docker |
| `dma-009` | dma | compile_gate | west_build_docker |
| `gpio-basic-001` | gpio-basic | static_heuristic | device_ready_check |
| `isr-concurrency-003` | isr-concurrency | static_analysis | k_spinlock_used, k_spin_lock_called, spinlock_key_saved, k_spin_unlock_called, shared_variable_declared |
| `isr-concurrency-004` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-005` | isr-concurrency | runtime_execution | output_validation |
| `isr-concurrency-006` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-007` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-008` | isr-concurrency | compile_gate | west_build_docker |
| `isr-concurrency-011` | isr-concurrency | runtime_execution | output_validation |
| `memory-opt-001` | memory-opt | runtime_execution | output_validation |
| `memory-opt-003` | memory-opt | runtime_execution | output_validation |
| `memory-opt-004` | memory-opt | compile_gate | west_build_docker |
| `memory-opt-005` | memory-opt | static_analysis | partition_added_to_domain |
| `memory-opt-006` | memory-opt | compile_gate | west_build_docker |
| `memory-opt-007` | memory-opt | runtime_execution | output_validation |
| `memory-opt-011` | memory-opt | runtime_execution | output_validation |
| `memory-opt-012` | memory-opt | runtime_execution | output_validation |
| `networking-001` | networking | runtime_execution | output_validation |
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
| `power-mgmt-004` | power-mgmt | compile_gate | west_build_docker |
| `power-mgmt-008` | power-mgmt | compile_gate | west_build_docker |
| `security-001` | security | runtime_execution | output_validation |
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
| `spi-i2c-007` | spi-i2c | compile_gate | west_build_docker |
| `storage-001` | storage | runtime_execution | output_validation |
| `storage-002` | storage | runtime_execution | output_validation |
| `storage-003` | storage | compile_gate | west_build_docker |
| `storage-004` | storage | runtime_execution | output_validation |
| `storage-005` | storage | runtime_execution | output_validation |
| `storage-007` | storage | compile_gate | west_build_docker |
| `storage-008` | storage | static_heuristic | write_verify_commit_order, verify_before_commit, delete_after_commit |
| `storage-012` | storage | compile_gate | west_build_docker |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-002` | threading | runtime_execution | output_validation |
| `threading-006` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-008` | threading | runtime_execution | output_validation |
| `threading-011` | threading | runtime_execution | output_validation |
| `threading-012` | threading | compile_gate | west_build_docker |
| `threading-013` | threading | compile_gate | west_build_docker |
| `timer-002` | timer | static_heuristic | main_sleeps_after_start |
| `timer-003` | timer | compile_gate | west_build_docker |
| `timer-005` | timer | runtime_execution | output_validation |
| `timer-006` | timer | compile_gate | west_build_docker |
| `timer-007` | timer | compile_gate | west_build_docker |
| `watchdog-002` | watchdog | compile_gate | west_build_docker |
| `watchdog-004` | watchdog | static_heuristic | distinct_channel_timeouts |
| `watchdog-005` | watchdog | compile_gate | west_build_docker |
| `watchdog-007` | watchdog | static_heuristic | device_ready_check |
| `watchdog-010` | watchdog | compile_gate | west_build_docker |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `west_build_docker` | 51 | adc-001, adc-002, ble-002, ble-005, ble-006 (+46 more) |
| `output_validation` | 33 | ble-001, ble-003, ble-004, ble-007, dma-003 (+28 more) |
| `device_ready_check` | 2 | gpio-basic-001, watchdog-007 |
| `multiple_block_descriptors` | 1 | dma-004 |
| `channel_priority_field_used` | 1 | dma-007 |
| `k_spinlock_used` | 1 | isr-concurrency-003 |
| `k_spin_lock_called` | 1 | isr-concurrency-003 |
| `spinlock_key_saved` | 1 | isr-concurrency-003 |
| `k_spin_unlock_called` | 1 | isr-concurrency-003 |
| `shared_variable_declared` | 1 | isr-concurrency-003 |
| `partition_added_to_domain` | 1 | memory-opt-005 |
| `write_verify_commit_order` | 1 | storage-008 |
| `verify_before_commit` | 1 | storage-008 |
| `delete_after_commit` | 1 | storage-008 |
| `main_sleeps_after_start` | 1 | timer-002 |
| `distinct_channel_timeouts` | 1 | watchdog-004 |

## TC Improvement Suggestions

