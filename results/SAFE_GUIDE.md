# EmbedEval Safe Guide for Embedded Engineers

*Auto-generated from benchmark results. Use this to decide when LLM-generated code needs human review.*

**Last updated:** 2026-04-04 17:54 UTC

## Models Tested

| Model | pass@1 | Cases |
|-------|--------|-------|
| haiku | 66.7% | 6 |
| sonnet | 81.7% | 109 |
| mock | 0.0% | 8 |

## CRITICAL — Do Not Trust

*LLM fails >50% of the time. Always write this code manually or review every line.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| boot | - | 0% | 0% |
| kconfig | - | 0% | - |
| timer | 0% | 100% | - |
| security | - | 33% | - |
| threading | - | 40% | - |

## CAUTION — Always Review

*LLM fails 20-50%. Use as starting point only. Expert review mandatory.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| dma | - | 50% | - |
| isr-concurrency | 100% | 50% | - |
| memory-opt | 50% | 56% | - |
| gpio-basic | - | 75% | - |

## MODERATE — Spot Check

*LLM is mostly correct (80-89%). Review safety-critical patterns (volatile, ISR, error paths).*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| storage | - | 80% | - |
| ota | - | 88% | - |
| spi-i2c | - | 88% | - |
| watchdog | - | 89% | - |

## RELIABLE — Generally Safe

*LLM passes 90%+. Standard code review is sufficient.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| adc | - | 100% | - |
| ble | 100% | 100% | - |
| device-tree | - | 100% | - |
| linux-driver | - | 100% | - |
| networking | - | 100% | - |
| power-mgmt | - | 100% | - |
| pwm | - | 100% | - |
| sensor-driver | - | 100% | - |
| uart | - | 100% | - |
| yocto | - | 100% | - |

## Most Common Failure Patterns

*These checks fail most often across all models and runs. Pay special attention to these patterns in LLM-generated code.*

| Pattern | Failures | What to Check |
|---------|----------|---------------|
| `west_build_docker` | 122 | Review LLM output against hardware/RTOS requirements |
| `output_validation` | 61 | Review LLM output against hardware/RTOS requirements |
| `init_error_path_cleanup` | 9 | Init error paths must free all previously acquired resources |
| `device_ready_check` | 9 | Review LLM output against hardware/RTOS requirements |
| `kconfig_format` | 8 | Review LLM output against hardware/RTOS requirements |
| `connect_error_handling` | 7 | Check return values of all API calls |
| `rollback_abort_on_download_error` | 7 | Review LLM output against hardware/RTOS requirements |
| `deadline_constant_not_magic` | 6 | Review LLM output against hardware/RTOS requirements |
| `mcuboot_enabled` | 5 | Review LLM output against hardware/RTOS requirements |
| `kernel_header_included` | 5 | Review LLM output against hardware/RTOS requirements |
| `dma_header_included` | 5 | Review LLM output against hardware/RTOS requirements |
| `memory_barrier_present` | 5 | Data + index update needs compiler_barrier() or __dmb() |
| `barrier_between_data_and_index_update` | 5 | Review LLM output against hardware/RTOS requirements |
| `multiple_block_descriptors` | 5 | Review LLM output against hardware/RTOS requirements |
| `shared_variable_declared` | 5 | Review LLM output against hardware/RTOS requirements |
| `will_configured_before_connect` | 4 | Review LLM output against hardware/RTOS requirements |
| `rollback_on_error` | 4 | Review LLM output against hardware/RTOS requirements |
| `cyclic_flag_set` | 4 | Review LLM output against hardware/RTOS requirements |
| `counter_is_volatile` | 4 | Variable shared with ISR/callback must be volatile |
| `slab_alloc_called` | 4 | Review LLM output against hardware/RTOS requirements |

## Practical Recommendations

### When using LLM for embedded code:

1. **Always review** volatile qualifiers, memory barriers, and ISR-safe patterns
2. **Never trust** DMA configuration, memory domain setup, or lock ordering without verification
3. **Verify** error handling paths — LLMs often generate happy-path-only code
4. **Check** that Kconfig/prj.conf options match the APIs used in the code
5. **Test** on actual hardware or QEMU — static checks alone miss runtime issues

