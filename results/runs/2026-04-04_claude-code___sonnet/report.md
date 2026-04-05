# Benchmark Report: claude-code://sonnet

**Date:** 2026-04-04 17:54 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | claude-code://sonnet |
| Total Cases | 109 |
| Passed | 89 |
| Failed | 20 |
| pass@1 | 81.7% |

## Failed Cases (20)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `boot-001` | boot | static_analysis | img_manager_enabled |
| `dma-003` | dma | static_heuristic | cyclic_enabled |
| `dma-009` | dma | static_heuristic | dma_config_after_stop, dma_start_called_twice |
| `gpio-basic-001` | gpio-basic | static_heuristic | device_ready_check |
| `isr-concurrency-003` | isr-concurrency | static_analysis | k_spinlock_used, k_spin_lock_called, spinlock_key_saved, k_spin_unlock_called, shared_variable_declared |
| `isr-concurrency-008` | isr-concurrency | runtime_execution | output_validation |
| `kconfig-001` | kconfig | static_analysis | spi_dma_enabled |
| `memory-opt-001` | memory-opt | compile_gate | west_build_docker |
| `memory-opt-005` | memory-opt | static_analysis | partition_added_to_domain |
| `memory-opt-008` | memory-opt | static_analysis | fpu_disabled |
| `memory-opt-012` | memory-opt | compile_gate | west_build_docker |
| `ota-005` | ota | static_heuristic | rollback_abort_on_download_error, rollback_on_error |
| `security-001` | security | runtime_execution | output_validation |
| `security-007` | security | static_heuristic | error_path_returns_early |
| `spi-i2c-004` | spi-i2c | static_heuristic | poll_loop_bounded |
| `storage-012` | storage | static_heuristic | write_rate_limited |
| `threading-001` | threading | runtime_execution | output_validation |
| `threading-007` | threading | runtime_execution | output_validation |
| `threading-008` | threading | static_heuristic | deadline_constant_not_magic |
| `watchdog-010` | watchdog | static_analysis | llm_call |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `output_validation` | 4 | isr-concurrency-008, security-001, threading-001, threading-007 |
| `west_build_docker` | 2 | memory-opt-001, memory-opt-012 |
| `img_manager_enabled` | 1 | boot-001 |
| `cyclic_enabled` | 1 | dma-003 |
| `dma_config_after_stop` | 1 | dma-009 |
| `dma_start_called_twice` | 1 | dma-009 |
| `device_ready_check` | 1 | gpio-basic-001 |
| `k_spinlock_used` | 1 | isr-concurrency-003 |
| `k_spin_lock_called` | 1 | isr-concurrency-003 |
| `spinlock_key_saved` | 1 | isr-concurrency-003 |
| `k_spin_unlock_called` | 1 | isr-concurrency-003 |
| `shared_variable_declared` | 1 | isr-concurrency-003 |
| `spi_dma_enabled` | 1 | kconfig-001 |
| `partition_added_to_domain` | 1 | memory-opt-005 |
| `fpu_disabled` | 1 | memory-opt-008 |
| `rollback_abort_on_download_error` | 1 | ota-005 |
| `rollback_on_error` | 1 | ota-005 |
| `error_path_returns_early` | 1 | security-007 |
| `poll_loop_bounded` | 1 | spi-i2c-004 |
| `write_rate_limited` | 1 | storage-012 |
| `deadline_constant_not_magic` | 1 | threading-008 |
| `llm_call` | 1 | watchdog-010 |

## Failure Classification

| Type | Count | Cases |
|------|-------|-------|
| Genuine code error | 19 | boot-001, dma-003, dma-009, gpio-basic-001, isr-concurrency-003 (+14 more) |
| LLM format failure (prose) | 1 | watchdog-010 |

*Adjusted pass@1 (excluding format failures): 82.4% (89/108)*


## TC Improvement Suggestions

