# Contributing to EmbedEval

Thank you for contributing to the embedded firmware LLM benchmark. This guide covers how to add new evaluation cases.

## Case Directory Structure

Each case lives in `cases/<case-id>/` with the following structure:

```
cases/<category>-<number>/
  metadata.yaml        # Case metadata (required)
  prompt.md            # LLM prompt (required)
  reference/
    main.c             # Verified reference solution (required)
  checks/
    static.py          # Layer 0 static checks (required)
    behavior.py        # Layer 3 behavioral checks (required)
  context/             # Additional context files (optional)
  src/
    main.c             # Skeleton/template code (optional)
```

**Case ID format:** `<category>-<3-digit-number>`, e.g., `kconfig-001`, `isr-concurrency-002`.

## metadata.yaml Schema

Every case requires a `metadata.yaml` file with the following fields:

```yaml
id: "kconfig-001"                 # Unique case ID (must match directory name)
category: "kconfig"               # One of the 20 supported categories
difficulty: "easy"                 # easy | medium | hard
title: "Short descriptive title"  # Human-readable title
description: "Detailed task description for documentation"
tags: [zephyr, kconfig, spi, dma] # Searchable tags
platform: "native_sim"            # native_sim | qemu_arm | babblesim | docker_only | qemu_freertos | esp_idf | qemu_linux | yocto_build
estimated_tokens: 200             # Expected output token count
sdk_version: "4.1.0"              # Target SDK/framework version
```

**Supported categories (20):**

Platform-agnostic: `gpio-basic`, `spi-i2c`, `dma`, `isr-concurrency`, `threading`, `timer`, `sensor-driver`, `networking`, `ble`, `security`, `storage`

System-level: `kconfig`, `device-tree`, `boot`, `ota`, `power-mgmt`, `watchdog`

Platform-specific: `yocto`, `linux-driver`, `memory-opt`

**Difficulty guidelines:**

| Tier | Criteria |
|------|----------|
| easy | Single concept, minimal context, straightforward implementation |
| medium | Multi-concept, requires understanding dependency chains |
| hard | Deep domain reasoning, subtle correctness requirements |

## Writing prompt.md

The prompt file is sent directly to the LLM. Follow these guidelines:

1. **Be specific and unambiguous.** State exactly what the LLM should produce.
2. **Include necessary context.** Board name, Zephyr version, relevant existing code.
3. **Specify output format.** "Write a Kconfig fragment" vs "Write a C source file."
4. **State constraints explicitly.** "Do not use deprecated APIs," "Must be ISR-safe."
5. **Do not include the answer.** The prompt should describe the task, not the solution.

Example structure:

```markdown
# Task

Write a Zephyr Kconfig fragment that enables SPI with DMA mode.

## Requirements

- Enable SPI controller support
- Enable DMA support (required dependency for SPI DMA)
- Enable SPI DMA mode
- Do not enable SPI slave mode

## Target

- Board: native_sim
- Zephyr: 4.1.0

## Output Format

Output only the Kconfig fragment (CONFIG_xxx=y lines), one per line.
```

## Reference Solution Requirements

Every case must include a verified reference solution at `reference/main.c`.

Requirements:

1. **Must pass all evaluation layers.** Run `embedeval validate --cases cases/` to verify.
2. **Must be a correct, complete solution** to the task described in `prompt.md`.
3. **Must be minimal.** Include only what is necessary to solve the task.
4. **Must follow coding conventions** for the relevant subsystem and platform.
5. **Must not contain comments explaining the evaluation** (the LLM should produce clean code).

## Writing checks/static.py

The static check module implements Layer 0 verification. It receives the raw generated code as a string and returns a list of `CheckDetail` objects.

**Required signature:**

```python
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate the generated code against static rules."""
    details: list[CheckDetail] = []

    # Example: check that a required pattern is present
    has_required_config = "CONFIG_SPI=y" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_enabled",
            passed=has_required_config,
            expected="CONFIG_SPI=y",
            actual="present" if has_required_config else "missing",
            check_type="exact_match",
        )
    )

    return details
```

**CheckDetail fields:**

| Field | Type | Description |
|-------|------|-------------|
| `check_name` | `str` | Unique name for this check within the case |
| `passed` | `bool` | Whether the check passed |
| `expected` | `str \| None` | What was expected |
| `actual` | `str \| None` | What was found |
| `check_type` | `str` | One of: `exact_match`, `contains`, `regex`, `constraint` |

**Guidelines:**

- Check structural requirements (format, required symbols, forbidden patterns)
- Do not duplicate behavioral checks (those belong in `behavior.py`)
- Aim for 3-8 checks per case
- Each check should test one specific property

## Writing checks/behavior.py

The behavioral check module implements Layer 3 verification. Same signature as `static.py`.

**Required signature:**

```python
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Example: metamorphic property check
    # If SPI_DMA is enabled, SPI must also be enabled
    # ...

    return details
```

**Guidelines:**

- Focus on **domain invariants** and **metamorphic properties**
- Test dependency chains (if X is enabled, Y must also be enabled)
- Test mutual exclusions (X and Y cannot both be enabled)
- Test value constraints (buffer size must be power of 2)
- Behavioral checks should catch "compiles but wrong" bugs

## PR Checklist

Before submitting a pull request for a new case, verify:

- [ ] `metadata.yaml` follows the schema above with a unique case ID
- [ ] Case ID matches the directory name
- [ ] `prompt.md` is clear, specific, and does not contain the answer
- [ ] `reference/main.c` exists and is a correct, complete solution
- [ ] `checks/static.py` has 3+ checks with meaningful assertions
- [ ] `checks/behavior.py` has 2+ metamorphic property checks
- [ ] `embedeval validate --cases cases/` passes for the new case
- [ ] Difficulty tier is justified (see guidelines above)
- [ ] `estimated_tokens` is reasonable for the expected output length
- [ ] No TODO, FIXME, or placeholder comments in check files
- [ ] Code formatted with `ruff format`
- [ ] Type checks pass with `mypy --strict`
