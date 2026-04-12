# EmbedEval Safe Guide for Embedded Engineers

*Auto-generated from benchmark results. Use this to decide when LLM-generated code needs human review.*

**Last updated:** 2026-04-12 10:19 UTC

## Models Tested

| Model | pass@1 | Cases |
|-------|--------|-------|
| haiku | 57.1% | 233 |
| sonnet | 73.4% | 233 |
| mock | 0.0% | 8 |

## CRITICAL — Do Not Trust

*LLM fails >50% of the time. Always write this code manually or review every line.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| boot | 100% | 100% | 0% |
| dma | 8% | 46% | - |
| storage | 31% | 54% | - |
| memory-opt | 33% | 58% | - |
| threading | 33% | 40% | - |
| isr-concurrency | 38% | 46% | - |
| ble | 45% | 82% | - |

## CAUTION — Always Review

*LLM fails 20-50%. Use as starting point only. Expert review mandatory.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| adc | 50% | 100% | - |
| timer | 50% | 92% | - |
| ota | 58% | 75% | - |
| kconfig | 60% | 80% | - |
| security | 70% | 60% | - |
| watchdog | 60% | 80% | - |
| spi-i2c | 64% | 79% | - |
| gpio-basic | 83% | 67% | - |
| power-mgmt | 67% | 92% | - |
| sensor-driver | 67% | 75% | - |
| uart | 67% | 67% | - |
| linux-driver | 70% | 70% | - |
| yocto | 70% | 100% | - |
| networking | 75% | 92% | - |

## RELIABLE — Generally Safe

*LLM passes 90%+. Standard code review is sufficient.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| device-tree | 100% | 100% | - |
| pwm | 100% | 100% | - |

## Most Common Failure Patterns

*These checks fail most often across all models and runs. Pay special attention to these patterns in LLM-generated code.*

| Pattern | Failures | What to Check |
|---------|----------|---------------|
| `west_build_docker` | 191 | Review LLM output against hardware/RTOS requirements |
| `output_validation` | 87 | Review LLM output against hardware/RTOS requirements |
| `stm32_hal_header_included` | 21 | Review LLM output against hardware/RTOS requirements |
| `dma_header_included` | 15 | Review LLM output against hardware/RTOS requirements |
| `init_error_path_cleanup` | 11 | Init error paths must free all previously acquired resources |
| `rollback_abort_on_download_error` | 10 | Review LLM output against hardware/RTOS requirements |
| `connect_error_handling` | 9 | Check return values of all API calls |
| `dma_reload_called` | 9 | Review LLM output against hardware/RTOS requirements |
| `device_ready_check` | 9 | Review LLM output against hardware/RTOS requirements |
| `kconfig_format` | 8 | Review LLM output against hardware/RTOS requirements |
| `slab_alloc_called` | 8 | Review LLM output against hardware/RTOS requirements |
| `slab_free_called` | 8 | Review LLM output against hardware/RTOS requirements |
| `deadline_constant_not_magic` | 8 | Review LLM output against hardware/RTOS requirements |
| `rollback_on_error` | 7 | Review LLM output against hardware/RTOS requirements |
| `multiple_block_descriptors` | 7 | Review LLM output against hardware/RTOS requirements |
| `counter_is_volatile` | 7 | Variable shared with ISR/callback must be volatile |
| `dma_config_called` | 7 | Use correct Zephyr DMA API (dma_config, not dma_configure) |
| `memory_barrier_present` | 7 | Data + index update needs compiler_barrier() or __dmb() |
| `barrier_between_data_and_index_update` | 7 | Review LLM output against hardware/RTOS requirements |
| `mcuboot_enabled` | 6 | Review LLM output against hardware/RTOS requirements |

## Practical Recommendations

### When using LLM for embedded code:

1. **Always review** volatile qualifiers, memory barriers, and ISR-safe patterns
2. **Never trust** DMA configuration, memory domain setup, or lock ordering without verification
3. **Verify** error handling paths — LLMs often generate happy-path-only code
4. **Check** that Kconfig/prj.conf options match the APIs used in the code
5. **Test** on actual hardware or QEMU — static checks alone miss runtime issues

