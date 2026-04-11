# EmbedEval Safe Guide for Embedded Engineers

*Auto-generated from benchmark results. Use this to decide when LLM-generated code needs human review.*

**Last updated:** 2026-04-11 12:18 UTC

## Models Tested

| Model | pass@1 | Cases |
|-------|--------|-------|
| haiku | 61.8% | 233 |
| sonnet | 73.4% | 233 |
| mock | 0.0% | 8 |

## CRITICAL — Do Not Trust

*LLM fails >50% of the time. Always write this code manually or review every line.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| boot | 100% | 100% | 0% |
| dma | 0% | 46% | - |
| threading | 33% | 40% | - |
| uart | 33% | 67% | - |
| memory-opt | 42% | 58% | - |
| isr-concurrency | 46% | 46% | - |

## CAUTION — Always Review

*LLM fails 20-50%. Use as starting point only. Expert review mandatory.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| security | 50% | 60% | - |
| storage | 54% | 54% | - |
| networking | 58% | 92% | - |
| ble | 64% | 82% | - |
| gpio-basic | 67% | 67% | - |
| ota | 67% | 75% | - |
| power-mgmt | 67% | 92% | - |
| sensor-driver | 67% | 75% | - |
| kconfig | 70% | 80% | - |
| linux-driver | 90% | 70% | - |
| spi-i2c | 71% | 79% | - |
| timer | 75% | 92% | - |

## MODERATE — Spot Check

*LLM is mostly correct (80-89%). Review safety-critical patterns (volatile, ISR, error paths).*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| watchdog | 80% | 80% | - |
| yocto | 80% | 100% | - |

## RELIABLE — Generally Safe

*LLM passes 90%+. Standard code review is sufficient.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| device-tree | 90% | 100% | - |
| adc | 100% | 100% | - |
| pwm | 100% | 100% | - |

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

