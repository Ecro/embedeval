---
name: New case contribution
about: Propose a new test case for EmbedEval
title: "[case] <category>: <short description>"
labels: ["enhancement", "case-contribution"]
assignees: []
---

## Category

<!-- One of: gpio-basic, uart, adc, pwm, spi-i2c, dma, isr-concurrency, threading, timer,
     sensor-driver, networking, ble, security, storage, kconfig, device-tree, boot, ota,
     power-mgmt, watchdog, yocto, linux-driver, memory-opt -->

**Category:**
**Difficulty:** <!-- easy / medium / hard -->
**Platform:** <!-- native_sim, qemu_arm, esp_idf, stm32_hal, docker_only, yocto_build -->

## What the case tests

<!-- What domain knowledge does the LLM need to write correct code here? -->

## Why this matters

<!-- A failure mode you saw in production? A common LLM mistake? -->

## Reference solution

- [ ] I have a verified reference solution that compiles
- [ ] I have a reference solution that runs to expected output
- [ ] I need help writing the reference

## Checks

EmbedEval cases need machine-checkable verification:

- [ ] L0 static checks (`checks/static.py`) — required APIs, headers, struct shapes
- [ ] L3 heuristic checks (`checks/behavior.py`) — domain-specific safety patterns
- [ ] L4 mutation tests (`checks/negatives.py`) — optional but appreciated

See [`docs/CONTRIBUTING.md`](../docs/CONTRIBUTING.md) for the case authoring workflow.

## Preventing benchmark gaming

- [ ] My case prompt describes **what** to build, not **how** (no safety hints in the prompt)
- [ ] I am happy for this case to live in the public set (or, mark it for the private held-out set)
