# Benchmark Report: mock

**Date:** 2026-03-29 13:25 UTC

## Summary

| Metric | Value |
|--------|-------|
| Model | mock |
| Total Cases | 8 |
| Passed | 0 |
| Failed | 8 |
| pass@1 | 0.0% |

## Failed Cases (8)

| Case | Difficulty | Failed Layer | Failed Checks |
|------|-----------|-------------|--------------|
| `boot-001` | boot | static_analysis | kconfig_format, mcuboot_enabled, img_manager_enabled, flash_enabled |
| `boot-002` | boot | static_analysis | kconfig_format, boot_delay_set, cmd_env_enabled |
| `boot-003` | boot | static_analysis | kconfig_format, mcuboot_enabled, rsa_signature_type, signature_key_file, flash_enabled |
| `boot-004` | boot | static_analysis | kconfig_format, mcuboot_enabled, swap_using_move_enabled, max_img_sectors_set |
| `boot-005` | boot | static_analysis | kconfig_format, mcuboot_enabled, boot_image_number_2, pcd_app_enabled |
| `boot-006` | boot | static_analysis | kconfig_format, boot_encrypt_image_enabled, boot_encrypt_rsa_enabled, boot_signature_type_rsa_enabled |
| `boot-007` | boot | static_analysis | kconfig_format, mcuboot_serial_enabled, boot_serial_cdc_acm_enabled, usb_device_stack_enabled |
| `boot-008` | boot | static_analysis | kconfig_format, mcuboot_enabled, boot_version_cmp_build_number_enabled, boot_validate_slot0_enabled |

## Failure Patterns

| Check Name | Failures | Cases |
|-----------|----------|-------|
| `kconfig_format` | 8 | boot-001, boot-002, boot-003, boot-004, boot-005 (+3 more) |
| `mcuboot_enabled` | 5 | boot-001, boot-003, boot-004, boot-005, boot-008 |
| `flash_enabled` | 2 | boot-001, boot-003 |
| `img_manager_enabled` | 1 | boot-001 |
| `boot_delay_set` | 1 | boot-002 |
| `cmd_env_enabled` | 1 | boot-002 |
| `rsa_signature_type` | 1 | boot-003 |
| `signature_key_file` | 1 | boot-003 |
| `swap_using_move_enabled` | 1 | boot-004 |
| `max_img_sectors_set` | 1 | boot-004 |
| `boot_image_number_2` | 1 | boot-005 |
| `pcd_app_enabled` | 1 | boot-005 |
| `boot_encrypt_image_enabled` | 1 | boot-006 |
| `boot_encrypt_rsa_enabled` | 1 | boot-006 |
| `boot_signature_type_rsa_enabled` | 1 | boot-006 |
| `mcuboot_serial_enabled` | 1 | boot-007 |
| `boot_serial_cdc_acm_enabled` | 1 | boot-007 |
| `usb_device_stack_enabled` | 1 | boot-007 |
| `boot_version_cmp_build_number_enabled` | 1 | boot-008 |
| `boot_validate_slot0_enabled` | 1 | boot-008 |

## TC Improvement Suggestions

