# EmbedEval Safe Guide for Embedded Engineers

*Auto-generated from benchmark results. Use this to decide when LLM-generated code needs human review.*

**Last updated:** 2026-04-11 11:59 UTC

## Models Tested

| Model | pass@1 | Cases |
|-------|--------|-------|
| haiku | 47.6% | 63 |
| sonnet | 54.1% | 61 |
| mock | 0.0% | 8 |

## CRITICAL — Do Not Trust

*LLM fails >50% of the time. Always write this code manually or review every line.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| boot | 100% | 100% | 0% |
| dma | 0% | 50% | - |
| gpio-basic | 0% | 0% | - |
| sensor-driver | 0% | 25% | - |
| uart | 0% | 0% | - |
| watchdog | 0% | 0% | - |
| ota | 25% | 50% | - |
| power-mgmt | 25% | 75% | - |
| threading | 50% | 25% | - |
| ble | 33% | 33% | - |
| networking | 33% | 50% | - |
| security | 33% | 67% | - |
| isr-concurrency | 80% | 40% | - |

## CAUTION — Always Review

*LLM fails 20-50%. Use as starting point only. Expert review mandatory.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| kconfig | 50% | 50% | - |
| linux-driver | 100% | 50% | - |
| spi-i2c | 50% | 50% | - |
| storage | 75% | 50% | - |
| yocto | 50% | 100% | - |
| timer | 75% | 67% | - |

## RELIABLE — Generally Safe

*LLM passes 90%+. Standard code review is sufficient.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| device-tree | 100% | 100% | - |
| memory-opt | 100% | 100% | - |

## Most Common Failure Patterns

*These checks fail most often across all models and runs. Pay special attention to these patterns in LLM-generated code.*

| Pattern | Failures | What to Check |
|---------|----------|---------------|
| `west_build_docker` | 145 | Review LLM output against hardware/RTOS requirements |
| `output_validation` | 70 | Review LLM output against hardware/RTOS requirements |
| `init_error_path_cleanup` | 9 | Init error paths must free all previously acquired resources |
| `device_ready_check` | 9 | Review LLM output against hardware/RTOS requirements |
| `kconfig_format` | 8 | Review LLM output against hardware/RTOS requirements |
| `connect_error_handling` | 8 | Check return values of all API calls |
| `rollback_abort_on_download_error` | 7 | Review LLM output against hardware/RTOS requirements |
| `dma_header_included` | 6 | Review LLM output against hardware/RTOS requirements |
| `deadline_constant_not_magic` | 6 | Review LLM output against hardware/RTOS requirements |
| `mcuboot_enabled` | 5 | Review LLM output against hardware/RTOS requirements |
| `stm32_hal_header_included` | 5 | Review LLM output against hardware/RTOS requirements |
| `dma_reload_called` | 5 | Review LLM output against hardware/RTOS requirements |
| `kernel_header_included` | 5 | Review LLM output against hardware/RTOS requirements |
| `memory_barrier_present` | 5 | Data + index update needs compiler_barrier() or __dmb() |
| `barrier_between_data_and_index_update` | 5 | Review LLM output against hardware/RTOS requirements |
| `multiple_block_descriptors` | 5 | Review LLM output against hardware/RTOS requirements |
| `shared_variable_declared` | 5 | Review LLM output against hardware/RTOS requirements |
| `periodic_battery_check` | 4 | Review LLM output against hardware/RTOS requirements |
| `adc_read_error_checked` | 4 | Review LLM output against hardware/RTOS requirements |
| `will_configured_before_connect` | 4 | Review LLM output against hardware/RTOS requirements |

## Practical Recommendations

### When using LLM for embedded code:

1. **Always review** volatile qualifiers, memory barriers, and ISR-safe patterns
2. **Never trust** DMA configuration, memory domain setup, or lock ordering without verification
3. **Verify** error handling paths — LLMs often generate happy-path-only code
4. **Check** that Kconfig/prj.conf options match the APIs used in the code
5. **Test** on actual hardware or QEMU — static checks alone miss runtime issues

