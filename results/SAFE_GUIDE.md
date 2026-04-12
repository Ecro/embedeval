# EmbedEval Safe Guide for Embedded Engineers

*Auto-generated from benchmark results. Use this to decide when LLM-generated code needs human review.*

**Last updated:** 2026-04-12 23:09 UTC

## Models Tested

| Model | pass@1 | Cases |
|-------|--------|-------|
| haiku | 57.1% | 233 |
| sonnet | 67.4% | 233 |
| mock | 0.0% | 8 |

## CRITICAL — Do Not Trust

*LLM fails >50% of the time. Always write this code manually or review every line.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| boot | 100% | 90% | 0% |
| dma | 8% | 31% | - |
| isr-concurrency | 38% | 23% | - |
| storage | 31% | 54% | - |
| memory-opt | 33% | 67% | - |
| threading | 33% | 33% | - |
| uart | 67% | 33% | - |
| ble | 45% | 82% | - |

## CAUTION — Always Review

*LLM fails 20-50%. Use as starting point only. Expert review mandatory.*

| Category | haiku | sonnet | mock |
|----------|------|------|------|
| adc | 50% | 100% | - |
| security | 70% | 50% | - |
| timer | 50% | 83% | - |
| ota | 58% | 67% | - |
| kconfig | 60% | 90% | - |
| watchdog | 60% | 90% | - |
| spi-i2c | 64% | 79% | - |
| gpio-basic | 83% | 67% | - |
| power-mgmt | 67% | 75% | - |
| sensor-driver | 67% | 75% | - |
| linux-driver | 70% | 70% | - |
| yocto | 70% | 80% | - |
| networking | 75% | 75% | - |

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
| `west_build_docker` | 241 | Review LLM output against hardware/RTOS requirements |
| `output_validation` | 142 | Review LLM output against hardware/RTOS requirements |
| `stm32_hal_header_included` | 24 | Review LLM output against hardware/RTOS requirements |
| `init_error_path_cleanup` | 17 | Init error paths must free all previously acquired resources |
| `dma_header_included` | 15 | Review LLM output against hardware/RTOS requirements |
| `rollback_abort_on_download_error` | 13 | Review LLM output against hardware/RTOS requirements |
| `dma_reload_called` | 13 | Review LLM output against hardware/RTOS requirements |
| `device_ready_check` | 13 | Review LLM output against hardware/RTOS requirements |
| `connect_error_handling` | 12 | Check return values of all API calls |
| `deadline_constant_not_magic` | 11 | Review LLM output against hardware/RTOS requirements |
| `rollback_on_error` | 10 | Review LLM output against hardware/RTOS requirements |
| `cyclic_flag_set` | 9 | Review LLM output against hardware/RTOS requirements |
| `kconfig_format` | 8 | Review LLM output against hardware/RTOS requirements |
| `adc_read_error_checked` | 8 | Review LLM output against hardware/RTOS requirements |
| `spi_dma_enabled` | 8 | Review LLM output against hardware/RTOS requirements |
| `hal_i2c_mem_read_used` | 8 | Review LLM output against hardware/RTOS requirements |
| `rootfs_size_uses_weak_assignment` | 8 | Review LLM output against hardware/RTOS requirements |
| `multiple_block_descriptors` | 8 | Review LLM output against hardware/RTOS requirements |
| `slab_alloc_called` | 8 | Review LLM output against hardware/RTOS requirements |
| `slab_free_called` | 8 | Review LLM output against hardware/RTOS requirements |

## Practical Recommendations

### When using LLM for embedded code:

1. **Always review** volatile qualifiers, memory barriers, and ISR-safe patterns
2. **Never trust** DMA configuration, memory domain setup, or lock ordering without verification
3. **Verify** error handling paths — LLMs often generate happy-path-only code
4. **Check** that Kconfig/prj.conf options match the APIs used in the code
5. **Test** on actual hardware or QEMU — static checks alone miss runtime issues

