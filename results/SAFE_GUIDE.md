# EmbedEval Safe Guide for Embedded Engineers

*Auto-generated from benchmark results. Use this to decide when LLM-generated code needs human review.*

**Last updated:** 2026-09-09 04:30 UTC

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
| dma | 46% | 38% | 8% | 31% | - |
| isr-concurrency | 31% | 38% | 38% | 23% | - |
| security | 30% | 60% | 70% | 50% | - |
| storage | 46% | 54% | 31% | 54% | - |
| memory-opt | 58% | 50% | 33% | 67% | - |
| threading | 40% | 53% | 33% | 33% | - |
| uart | 33% | 67% | 67% | 33% | - |
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
| power-mgmt | 58% | 83% | 67% | 75% | - |
| yocto | 71% | 58% | 70% | 80% | - |
| kconfig | 90% | 70% | 60% | 90% | - |
| watchdog | 70% | 80% | 60% | 90% | - |
| spi-i2c | 71% | 79% | 64% | 79% | - |
| gpio-basic | 83% | 83% | 83% | 67% | - |
| sensor-driver | 83% | 67% | 67% | 75% | - |
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
| `output_validation` | 38 | Review LLM output against hardware/RTOS requirements |
| `west_build_docker` | 32 | Review LLM output against hardware/RTOS requirements |
| `hardware_compatibility_list_nonempty` | 6 | Review LLM output against hardware/RTOS requirements |
| `init_error_path_cleanup` | 3 | Init error paths must free all previously acquired resources |
| `module_platform_driver_macro` | 2 | Review LLM output against hardware/RTOS requirements |
| `free_irq_before_cancel_work` | 2 | Review LLM output against hardware/RTOS requirements |
| `is_err_guards_reset_control_get` | 2 | Review LLM output against hardware/RTOS requirements |
| `nonzero_exit_on_error` | 2 | Review LLM output against hardware/RTOS requirements |
| `exit_cancels_work_then_purges_queue` | 2 | Review LLM output against hardware/RTOS requirements |
| `input_cb_sends_netlink_unicast` | 2 | Review LLM output against hardware/RTOS requirements |
| `genl_family_has_name_field` | 2 | Review LLM output against hardware/RTOS requirements |
| `no_custom_do_compile` | 2 | Review LLM output against hardware/RTOS requirements |
| `rootfs_size_uses_weak_assignment` | 2 | Review LLM output against hardware/RTOS requirements |
| `i2c_master_header` | 2 | Review LLM output against hardware/RTOS requirements |
| `i2c_master_new_api` | 2 | Review LLM output against hardware/RTOS requirements |
| `no_legacy_i2c_driver` | 2 | Review LLM output against hardware/RTOS requirements |
| `nvs_initialized_before_wifi` | 2 | Review LLM output against hardware/RTOS requirements |
| `i2c_address_left_shifted` | 2 | Review LLM output against hardware/RTOS requirements |
| `cs_deasserted_after_transfer` | 2 | Review LLM output against hardware/RTOS requirements |
| `receive_it_rearmed_in_callback` | 2 | Review LLM output against hardware/RTOS requirements |

## Practical Recommendations

### When using LLM for embedded code:

1. **Always review** volatile qualifiers, memory barriers, and ISR-safe patterns
2. **Never trust** DMA configuration, memory domain setup, or lock ordering without verification
3. **Verify** error handling paths — LLMs often generate happy-path-only code
4. **Check** that Kconfig/prj.conf options match the APIs used in the code
5. **Test** on actual hardware or QEMU — static checks alone miss runtime issues

