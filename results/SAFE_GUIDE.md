# EmbedEval Safe Guide for Embedded Engineers

*Auto-generated from benchmark results. Use this to decide when LLM-generated code needs human review.*

**Last updated:** 2026-09-08 15:13 UTC

## Models Tested

| Model | pass@1 | Cases |
|-------|--------|-------|
| claude-opus-5 | 61.8% | 267 |
| claude-sonnet-5 | 67.3% | 263 |
| haiku | 57.1% | 233 |
| sonnet | 67.4% | 233 |
| mock | 0.0% | 8 |

## CRITICAL — Do Not Trust

*LLM fails >50% of the time. Always write this code manually or review every line.*

| Category | claude-opus-5 | claude-sonnet-5 | haiku | sonnet | mock |
|----------|------|------|------|------|------|
| boot | 100% | 100% | 100% | 90% | 0% |
| dma | 38% | 38% | 8% | 31% | - |
| isr-concurrency | 31% | 38% | 38% | 23% | - |
| storage | 46% | 54% | 31% | 54% | - |
| memory-opt | 58% | 50% | 33% | 67% | - |
| threading | 40% | 53% | 33% | 33% | - |
| uart | 33% | 67% | 67% | 33% | - |
| security | 40% | 60% | 70% | 50% | - |
| ota | 44% | 61% | 58% | 67% | - |
| ble | 64% | 73% | 45% | 82% | - |

## CAUTION — Always Review

*LLM fails 20-50%. Use as starting point only. Expert review mandatory.*

| Category | claude-opus-5 | claude-sonnet-5 | haiku | sonnet | mock |
|----------|------|------|------|------|------|
| adc | 50% | 100% | 50% | 100% | - |
| linux-userspace | 50% | 75% | - | - | - |
| timer | 67% | 83% | 50% | 83% | - |
| networking | 53% | 59% | 75% | 75% | - |
| yocto | 79% | 58% | 70% | 80% | - |
| kconfig | 80% | 70% | 60% | 90% | - |
| watchdog | 70% | 80% | 60% | 90% | - |
| spi-i2c | 71% | 79% | 64% | 79% | - |
| gpio-basic | 83% | 83% | 83% | 67% | - |
| power-mgmt | 67% | 83% | 67% | 75% | - |
| sensor-driver | 75% | 67% | 67% | 75% | - |
| linux-driver | 72% | 69% | 70% | 70% | - |

## RELIABLE — Generally Safe

*LLM passes 90%+. Standard code review is sufficient.*

| Category | claude-opus-5 | claude-sonnet-5 | haiku | sonnet | mock |
|----------|------|------|------|------|------|
| device-tree | 100% | 100% | 100% | 100% | - |
| pwm | 100% | 100% | 100% | 100% | - |

## Most Common Failure Patterns

*These checks fail most often across all models and runs. Pay special attention to these patterns in LLM-generated code.*

| Pattern | Failures | What to Check |
|---------|----------|---------------|
| `west_build_docker` | 294 | Review LLM output against hardware/RTOS requirements |
| `output_validation` | 195 | Review LLM output against hardware/RTOS requirements |
| `stm32_hal_header_included` | 24 | Review LLM output against hardware/RTOS requirements |
| `init_error_path_cleanup` | 21 | Init error paths must free all previously acquired resources |
| `dma_reload_called` | 16 | Review LLM output against hardware/RTOS requirements |
| `dma_header_included` | 15 | Review LLM output against hardware/RTOS requirements |
| `rollback_abort_on_download_error` | 14 | Review LLM output against hardware/RTOS requirements |
| `connect_error_handling` | 14 | Check return values of all API calls |
| `summary_defined` | 13 | Review LLM output against hardware/RTOS requirements |
| `device_ready_check` | 13 | Review LLM output against hardware/RTOS requirements |
| `cyclic_flag_set` | 12 | Review LLM output against hardware/RTOS requirements |
| `adc_read_error_checked` | 12 | Review LLM output against hardware/RTOS requirements |
| `rollback_on_error` | 11 | Review LLM output against hardware/RTOS requirements |
| `spi_dma_enabled` | 11 | Review LLM output against hardware/RTOS requirements |
| `deadline_constant_not_magic` | 11 | Review LLM output against hardware/RTOS requirements |
| `k_sleep_present` | 10 | Review LLM output against hardware/RTOS requirements |
| `multiple_block_descriptors` | 10 | Review LLM output against hardware/RTOS requirements |
| `counter_is_volatile` | 10 | Variable shared with ISR/callback must be volatile |
| `window_min_greater_than_zero` | 10 | Review LLM output against hardware/RTOS requirements |
| `window_max_greater_than_zero` | 10 | Review LLM output against hardware/RTOS requirements |

## Practical Recommendations

### When using LLM for embedded code:

1. **Always review** volatile qualifiers, memory barriers, and ISR-safe patterns
2. **Never trust** DMA configuration, memory domain setup, or lock ordering without verification
3. **Verify** error handling paths — LLMs often generate happy-path-only code
4. **Check** that Kconfig/prj.conf options match the APIs used in the code
5. **Test** on actual hardware or QEMU — static checks alone miss runtime issues

