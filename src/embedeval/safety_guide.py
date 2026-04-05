"""LLM Embedded Code Safety Guide generator.

Produces a developer-facing report with:
1. LLM Capability Boundary (what LLMs can/cannot do)
2. Per-task risk assessment with checklists
3. Failure pattern statistics from benchmark data
4. Embedded Factor Competency Matrix (44 validated factors)
"""

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from embedeval.failure_taxonomy import classify_failure
from embedeval.models import EvalResult

logger = logging.getLogger(__name__)

# --- Static content: LLM Capability Boundary ---

CAPABILITY_BOUNDARY = """## LLM Capability Boundary for Embedded Development

### What LLMs Do Well (90%+ reliability)

- **Build configuration** — Kconfig fragments, prj.conf, CMakeLists.txt
- **Basic peripheral init** — GPIO, UART, SPI pin configuration
- **Thread creation** — K_THREAD_DEFINE, message queues, semaphores
- **Device Tree nodes** — compatible strings, reg properties, overlays
- **Boilerplate code** — module_init/exit, file_operations structs

### What LLMs Can Help With, But Require Review (60-85%)

- **ISR handlers** — may omit volatile, use mutex instead of spinlock,
  call blocking APIs
- **DMA configuration** — cache alignment errors, cyclic vs one-shot confusion
- **BLE stack setup** — connection lifecycle incomplete,
  characteristic setup partially wrong
- **Error handling** — happy path implemented, cleanup on failure paths missing
- **SPI/I2C protocols** — timing parameters may be wrong, error recovery incomplete

### What LLMs Cannot Do (benchmark scope boundary)

- **Board bring-up** — first boot, power rail verification, clock configuration
- **Signal integrity** — PCB trace routing, impedance matching, crosstalk analysis
- **EMC/EMI compliance** — antenna design, shielding, regulatory certification
- **Sensor calibration** — ADC offset/gain against physical reference
- **Real-time debugging** — JTAG/SWD, oscilloscope correlation,
  race condition reproduction
- **Safety certification** — IEC 61508, ISO 26262, DO-178C traceability
- **Production testing** — ICT fixtures, boundary scan, yield analysis
- **Field failure analysis** — component aging, environmental stress,
  intermittent faults
"""

# --- Static content: Per-task checklists ---

TASK_CHECKLISTS: dict[str, dict[str, Any]] = {
    "ISR / Interrupt Handlers": {
        "risk": "HIGH",
        "categories": ["isr-concurrency"],
        "reasoning_level": "L3 Cross-Domain",
        "checklist": [
            "Shared variables declared volatile?",
            "No blocking calls in ISR (mutex, sleep, printk, malloc)?",
            "Spinlock key captured from lock and passed to unlock?",
            "Both ISR and thread sides protected by same spinlock?",
            "Atomic operations used where needed (atomic_t)?",
        ],
        "common_failure": "LLM uses k_mutex_lock in ISR body → deadlock at runtime",
    },
    "Error Recovery Paths": {
        "risk": "HIGH",
        "categories": ["boot", "linux-driver", "ota", "storage"],
        "reasoning_level": "L4 System Reasoning",
        "checklist": [
            "Every init/alloc return value checked (ret < 0)?",
            "Error branch contains return or goto (not just log)?",
            "Cleanup calls in reverse order of initialization?",
            "All allocated resources freed on every error path?",
            "Cleanup is actual code, not commented out?",
        ],
        "common_failure": "3-step init, step 2 fails → step 1 resource leaked",
    },
    "DMA Transfers": {
        "risk": "HIGH",
        "categories": ["dma"],
        "reasoning_level": "L3 Cross-Domain",
        "checklist": [
            "Buffer aligned to cache line size (32B or 64B)?",
            "Cyclic mode: reload called in DMA callback?",
            "Ping-pong buffers for continuous transfer?",
            "dma_stop called on error or completion?",
            "Cache flush/invalidate around DMA regions?",
        ],
        "common_failure": (
            "No cache alignment → intermittent data corruption under load"
        ),
    },
    "Watchdog Timer": {
        "risk": "MEDIUM",
        "categories": ["watchdog"],
        "reasoning_level": "L4 System Reasoning",
        "checklist": [
            "WDT install before setup (correct API order)?",
            "Feed interval shorter than WDT timeout?",
            "Feed is conditional (only when system healthy)?",
            "Health flags are volatile or atomic?",
            "Reset flag set appropriately?",
        ],
        "common_failure": "Unconditional WDT feed → watchdog never triggers on hang",
    },
    "Linux Kernel Drivers": {
        "risk": "HIGH",
        "categories": ["linux-driver"],
        "reasoning_level": "L4 System Reasoning",
        "checklist": [
            "copy_to_user / copy_from_user (not __ variants)?",
            "Register and unregister balanced?",
            ".owner = THIS_MODULE in file_operations?",
            "All init errors have full rollback cleanup?",
            "No Zephyr/FreeRTOS API contamination?",
        ],
        "common_failure": (
            "Init allocates chrdev + cdev, error after cdev → chrdev leaked"
        ),
    },
    "Basic GPIO / UART / SPI": {
        "risk": "LOW",
        "categories": ["gpio-basic", "uart", "adc", "pwm", "spi-i2c"],
        "reasoning_level": "L1 API Recall",
        "checklist": [
            "device_is_ready() called before use?",
            "Pin configured with correct direction (input/output)?",
            "Interrupt edge type specified?",
        ],
        "common_failure": "Missing device_is_ready check (rare but possible)",
    },
}


# --- Factor Competency Matrix: validated embedded failure factors ---


@dataclass
class FactorDef:
    """Definition of an embedded failure factor for LLM competency assessment."""

    id: str
    name: str
    group: str
    strength: str  # High | Med | Low
    mapped_categories: list[str] = field(default_factory=list)
    mapped_checks: list[str] = field(default_factory=list)
    verdict_override: str | None = None  # "incapable" | "untested" | None
    description: str = ""


FACTOR_DEFINITIONS: list[FactorDef] = [
    # --- A. Hardware Awareness Gap ---
    FactorDef(
        "A1",
        "Register/MMIO access",
        "A. Hardware Awareness",
        "High",
        mapped_categories=["linux-driver"],
        mapped_checks=["register_unregister_balanced", "copy_to_user_not_raw_deref"],
        description="MMIO register address/bitfield hallucination",
    ),
    FactorDef(
        "A2",
        "Peripheral init ordering",
        "A. Hardware Awareness",
        "Med",
        mapped_categories=["dma", "watchdog", "ota"],
        mapped_checks=["dma_config_before_start", "wdt_install_before_setup"],
        description="Datasheet-mandated initialization sequence",
    ),
    FactorDef(
        "A4",
        "Pin muxing",
        "A. Hardware Awareness",
        "Med",
        mapped_categories=["device-tree"],
        mapped_checks=["pinctrl_binding_present", "pinctrl_names_default"],
        description="AF configuration, DT pinctrl bindings",
    ),
    FactorDef(
        "A5",
        "DMA channel mapping",
        "A. Hardware Awareness",
        "High",
        mapped_categories=["dma"],
        mapped_checks=["dma_config_before_start", "cache_aligned"],
        description="DMA channel-peripheral mapping, burst/circular",
    ),
    FactorDef(
        "A6",
        "Interrupt vector/priority",
        "A. Hardware Awareness",
        "Med",
        mapped_categories=["isr-concurrency"],
        mapped_checks=["spinlock_used_in_both_contexts", "irq_priority_configured"],
        description="NVIC priority group, preemption config",
    ),
    FactorDef(
        "A10",
        "Endianness",
        "A. Hardware Awareness",
        "Med",
        mapped_categories=["networking", "spi-i2c"],
        mapped_checks=["port_byte_order", "little_endian_reconstruction"],
        description="Mixed endian byte order handling",
    ),
    FactorDef(
        "A11",
        "Device Tree",
        "A. Hardware Awareness",
        "Med",
        mapped_categories=["device-tree"],
        mapped_checks=["compatible_string_valid", "status_okay_present"],
        description="DT bindings, overlays, compatible strings",
    ),
    # --- B. Temporal Constraints ---
    FactorDef(
        "B3",
        "Deadline miss",
        "B. Temporal Constraints",
        "Med",
        mapped_categories=["threading", "timer"],
        mapped_checks=[
            "deadline_miss_reported",
            "deadline_threshold_defined",
            "thread_is_periodic",
            "deadline_miss_detected",
            "deadline_miss_action",
        ],
        description="Hard real-time periodic deadline enforcement",
    ),
    FactorDef(
        "B5",
        "Timer accuracy",
        "B. Temporal Constraints",
        "Med",
        mapped_categories=["timer"],
        mapped_checks=["feed_interval_less_than_timeout", "timer_period_configured"],
        description="Prescaler/autoreload value calculation",
    ),
    # --- C. Resource Constraints ---
    FactorDef(
        "C1",
        "RAM budget",
        "C. Resource Constraints",
        "High",
        mapped_categories=["memory-opt"],
        mapped_checks=["no_oversized_buffer", "total_static_allocation_bounded"],
        description="KB-scale RAM; LLMs generate large buffers",
    ),
    FactorDef(
        "C2",
        "Stack overflow",
        "C. Resource Constraints",
        "High",
        mapped_categories=["threading", "isr-concurrency"],
        mapped_checks=[
            "stack_size_adequate",
            "stack_sizeof_macro_used",
            "stack_size_explicitly_defined",
            "stack_overflow_protection_configured",
        ],
        description="Fixed per-task stack; recursion/deep calls",
    ),
    FactorDef(
        "C3",
        "Heap fragmentation",
        "C. Resource Constraints",
        "Med",
        mapped_categories=["memory-opt"],
        mapped_checks=["no_malloc_free_in_loop"],
        description="Long-running malloc/free causes unusable memory",
    ),
    FactorDef(
        "C4",
        "Flash size",
        "C. Resource Constraints",
        "Med",
        mapped_categories=["memory-opt"],
        mapped_checks=["no_lookup_table", "no_stdio", "no_large_string_literals"],
        description="Code size constraint; LLMs generate verbose code",
    ),
    FactorDef(
        "C5",
        "No dynamic alloc",
        "C. Resource Constraints",
        "High",
        mapped_categories=["isr-concurrency"],
        mapped_checks=["no_forbidden_apis_in_isr", "no_malloc_in_callbacks"],
        description="MISRA/safety standards ban runtime malloc",
    ),
    FactorDef(
        "C6",
        "Memory alignment",
        "C. Resource Constraints",
        "Med",
        mapped_categories=["dma"],
        mapped_checks=["cache_aligned", "aligned_attribute_present"],
        description="Struct padding; Cortex-M0 unaligned = HardFault",
    ),
    FactorDef(
        "C7",
        "MPU configuration",
        "C. Resource Constraints",
        "Med",
        mapped_categories=["memory-opt"],
        mapped_checks=[
            "domain_init_before_add_partition",
            "appmem_partition_define_used",
            "thread_has_k_user_flag",
        ],
        description="MPU regions, access permissions, cache policy",
    ),
    FactorDef(
        "C8",
        "Linker script",
        "C. Resource Constraints",
        "High",
        mapped_categories=["memory-opt"],
        mapped_checks=["gcc_section_attribute_used", "buffer_in_named_section"],
        description=".text/.bss/.data placement, Flash/RAM partition",
    ),
    FactorDef(
        "C9",
        "volatile misuse",
        "C. Resource Constraints",
        "High",
        mapped_categories=["isr-concurrency", "watchdog"],
        mapped_checks=["volatile_shared", "volatile_health_flag"],
        description="Missing volatile on MMIO/shared variables",
    ),
    FactorDef(
        "C10",
        "Barrier vs fence",
        "C. Resource Constraints",
        "Med",
        mapped_categories=["dma"],
        mapped_checks=["cache_flush_before_dma", "cache_invalidate_after_dma"],
        description="Compiler barrier vs HW fence (__DSB/__DMB)",
    ),
    FactorDef(
        "C11",
        "Cache coherency",
        "C. Resource Constraints",
        "Med",
        mapped_categories=["dma"],
        mapped_checks=[
            "cache_flush_before_dma",
            "pre_invalidate_dest",
            "post_invalidate_dest",
        ],
        description="Missing DMA buffer cache flush/invalidate",
    ),
    FactorDef(
        "C12",
        "Power budget",
        "C. Resource Constraints",
        "High",
        mapped_categories=["power-mgmt"],
        mapped_checks=["multiple_sleep_depths"],
        description="Sleep modes, clock gating, retention RAM",
    ),
    # --- D. Concurrency & Safety ---
    FactorDef(
        "D1",
        "Race condition",
        "D. Concurrency & Safety",
        "High",
        mapped_categories=["isr-concurrency"],
        mapped_checks=["volatile_shared", "atomic_indices"],
        description="ISR-task shared variable contention",
    ),
    FactorDef(
        "D2",
        "Priority inversion",
        "D. Concurrency & Safety",
        "Med",
        mapped_categories=["threading"],
        mapped_checks=["three_distinct_priorities", "same_mutex_shared"],
        description="Mutex-holding task preempted by mid-priority",
    ),
    FactorDef(
        "D3",
        "Deadlock",
        "D. Concurrency & Safety",
        "Med",
        mapped_categories=["threading"],
        mapped_checks=["consistent_lock_order"],
        description="Multi-lock ordering error",
    ),
    FactorDef(
        "D4",
        "Critical section scope",
        "D. Concurrency & Safety",
        "Med",
        mapped_categories=["isr-concurrency"],
        mapped_checks=[
            "spinlock_used_in_both_contexts",
            "no_blocking_in_locked_region",
        ],
        description="Minimize interrupt disable duration",
    ),
    FactorDef(
        "D5",
        "Atomic operations",
        "D. Concurrency & Safety",
        "Med",
        mapped_categories=["isr-concurrency"],
        mapped_checks=["atomic_indices", "atomic_type_for_shared"],
        description="Non-atomic RMW causes register corruption",
    ),
    FactorDef(
        "D6",
        "ISR forbidden ops",
        "D. Concurrency & Safety",
        "High",
        mapped_categories=["isr-concurrency"],
        mapped_checks=["no_forbidden_apis_in_isr", "no_mutex_in_isr"],
        description="malloc/printk/blocking calls in ISR",
    ),
    FactorDef(
        "D7",
        "Watchdog management",
        "D. Concurrency & Safety",
        "Med",
        mapped_categories=["watchdog"],
        mapped_checks=["wdt_install_before_setup", "conditional_feed"],
        description="WDT across reset domains, bootloader handoff",
    ),
    FactorDef(
        "D9",
        "MISRA compliance",
        "D. Concurrency & Safety",
        "High",
        verdict_override="incapable",
        description="0/5 LLMs generate MISRA-compliant code (IEEE 2025)",
    ),
    FactorDef(
        "D10",
        "Static analysis clean",
        "D. Concurrency & Safety",
        "Med",
        verdict_override="incapable",
        description="Zero warnings from Polyspace/PC-lint/Coverity",
    ),
    FactorDef(
        "D11",
        "Defensive programming",
        "D. Concurrency & Safety",
        "Med",
        mapped_categories=["linux-driver", "boot", "ota"],
        mapped_checks=["error_handling", "init_error_path_cleanup"],
        description="LLMs favor happy path, skip error propagation",
    ),
    FactorDef(
        "D12",
        "Fault tolerance",
        "D. Concurrency & Safety",
        "Med",
        mapped_categories=["ota", "boot"],
        mapped_checks=["rollback_on_error", "self_test_before_confirm"],
        description="HardFault handler, safe-state entry",
    ),
    # --- E. Toolchain & Verification ---
    FactorDef(
        "E1",
        "Cross-compilation",
        "E. Toolchain & Verification",
        "High",
        description="arm-none-eabi-gcc, target triple; validated by L1",
    ),
    FactorDef(
        "E2",
        "SDK version deps",
        "E. Toolchain & Verification",
        "High",
        description="ESP-IDF/Zephyr API changes; validated by L1",
    ),
    FactorDef(
        "E3",
        "Build system",
        "E. Toolchain & Verification",
        "High",
        mapped_categories=["kconfig"],
        mapped_checks=["no_conflicting_configs", "dependency_chain_complete"],
        description="ESP-IDF component, Zephyr west, Yocto recipe",
    ),
    FactorDef(
        "E4",
        "API hallucination",
        "E. Toolchain & Verification",
        "High",
        mapped_checks=["no_cross_platform_apis", "no_hallucinated_apis"],
        description="Non-existent or deprecated API references",
    ),
    FactorDef(
        "E7",
        "OTA pipeline",
        "E. Toolchain & Verification",
        "Med",
        mapped_categories=["ota"],
        mapped_checks=["rollback_on_error"],
        description="Dual-slot, rollback, CRC, power-loss recovery",
    ),
    FactorDef(
        "E8",
        "Bootloader sequence",
        "E. Toolchain & Verification",
        "Med",
        mapped_categories=["boot"],
        mapped_checks=["signature_type_present"],
        description="MCUboot, secure boot, image signing",
    ),
    # --- F. Domain Knowledge ---
    FactorDef(
        "F1",
        "System architecture",
        "F. Domain Knowledge",
        "High",
        mapped_categories=["threading"],
        mapped_checks=[
            "multiple_threads",
            "inter_thread_communication",
            "priority_differentiation",
        ],
        description="Bare-metal vs RTOS, polling vs interrupt, task partition",
    ),
    FactorDef(
        "F2",
        "Power state machine",
        "F. Domain Knowledge",
        "High",
        mapped_categories=["power-mgmt"],
        mapped_checks=["suspend_resume_both_handled"],
        description="Sleep/Deep Sleep/Standby transitions, wakeup sources",
    ),
    FactorDef(
        "F3",
        "Protocol timing",
        "F. Domain Knowledge",
        "Med",
        mapped_categories=["spi-i2c", "networking"],
        mapped_checks=["spi_frequency_configured"],
        description="I2C clock stretching, SPI CPOL/CPHA, UART baud",
    ),
    FactorDef(
        "F6",
        "ADC/DAC conversion",
        "F. Domain Knowledge",
        "Low",
        mapped_categories=["sensor-driver"],
        mapped_checks=["raw_to_physical_conversion"],
        description="ADC raw to physical, calibration, non-linearity",
    ),
    FactorDef(
        "F10",
        "Long-term operation",
        "F. Domain Knowledge",
        "Med",
        mapped_categories=["storage"],
        mapped_checks=[
            "no_malloc_in_loop",
            "write_rate_limited",
            "unsigned_counter_type",
        ],
        description="10yr+ field operation; memory leaks, flash wear",
    ),
    FactorDef(
        "F12",
        "Multicore/heterogeneous",
        "F. Domain Knowledge",
        "Med",
        mapped_categories=["threading"],
        mapped_checks=[
            "volatile_on_shared_flags",
            "memory_barrier_present",
            "shared_memory_aligned",
        ],
        description="Cortex-M+A, PRU, DSP IPC/shared memory",
    ),
]

# Group labels for rendering
FACTOR_GROUPS = [
    "A. Hardware Awareness",
    "B. Temporal Constraints",
    "C. Resource Constraints",
    "D. Concurrency & Safety",
    "E. Toolchain & Verification",
    "F. Domain Knowledge",
]


def _calculate_check_pass_rates(results: list[EvalResult]) -> dict[str, float]:
    """Calculate pass rate per check_name across all results.

    Scans all LayerResult.details for CheckDetail entries and computes
    per-check pass rates. Only includes checks that appear at least once.
    """
    check_stats: dict[str, list[bool]] = defaultdict(list)
    for r in results:
        for layer in r.layers:
            for detail in layer.details:
                check_stats[detail.check_name].append(detail.passed)
    return {
        name: sum(passes) / len(passes)
        for name, passes in check_stats.items()
        if passes
    }


def _compute_factor_verdict(
    factor: FactorDef,
    cat_rates: dict[str, float],
    check_rates: dict[str, float],
) -> tuple[float | None, str, str]:
    """Compute verdict for a single factor.

    Returns (rate_or_none, verdict_emoji_label, action).
    Priority: override > check-level rate > category-level rate > untested.
    """
    if factor.verdict_override == "incapable":
        return (None, "❌ Incapable", "Do not use LLM — write manually")
    if factor.verdict_override == "untested":
        return (None, "❓ Untested", "Not benchmarked — no assumptions")

    # Check-level rate (more precise)
    rate: float | None = None
    if factor.mapped_checks:
        matched = [check_rates[c] for c in factor.mapped_checks if c in check_rates]
        if matched:
            rate = sum(matched) / len(matched)

    # Fallback to category-level rate
    if rate is None and factor.mapped_categories:
        matched = [cat_rates[c] for c in factor.mapped_categories if c in cat_rates]
        if matched:
            rate = sum(matched) / len(matched)

    if rate is None:
        return (None, "❓ Untested", "Not benchmarked — no assumptions")
    if rate >= 0.9:
        return (rate, "✅ Verified", "LLM output usable — light review")
    if rate >= 0.6:
        return (rate, "⚠️ Caution", "Expert review required")
    return (rate, "❌ Incapable", "Do not use LLM — write manually")


def _factor_competency_matrix(
    results: list[EvalResult],
    cat_rates: dict[str, float] | None = None,
) -> list[str]:
    """Generate the Embedded Factor Competency Matrix section."""
    n = len(FACTOR_DEFINITIONS)
    lines = [
        "## Embedded Factor Competency Matrix",
        "",
        f"> LLM competency assessment across {n} validated embedded failure factors.",
        "> Auto-computed from benchmark results."
        " ❓ = not covered by current benchmark.",
        "",
    ]

    if cat_rates is None:
        cat_rates = _calculate_category_pass_rates(results)
    check_rates = _calculate_check_pass_rates(results)

    # Collect verdicts for summary
    summary: dict[str, list[str]] = {
        "✅ Verified": [],
        "⚠️ Caution": [],
        "❌ Incapable": [],
        "❓ Untested": [],
    }

    for group_key in FACTOR_GROUPS:
        group_factors = [f for f in FACTOR_DEFINITIONS if f.group == group_key]
        if not group_factors:
            continue

        lines.append(f"### {group_key}")
        lines.append("")
        lines.append("| # | Factor | Strength | Pass Rate | Verdict | Action |")
        lines.append("|---|--------|----------|-----------|---------|--------|")

        for f in group_factors:
            rate, verdict, action = _compute_factor_verdict(
                f,
                cat_rates,
                check_rates,
            )
            rate_str = f"{rate:.0%}" if rate is not None else "—"
            row = (
                f"| {f.id} | {f.name} | {f.strength}"
                f" | {rate_str} | {verdict} | {action} |"
            )
            lines.append(row)
            summary[verdict].append(f.id)

        lines.append("")

    # Summary table
    lines.append("### Summary")
    lines.append("")
    lines.append("| Verdict | Count | Factors |")
    lines.append("|---------|-------|---------|")
    for verdict_label in ["✅ Verified", "⚠️ Caution", "❌ Incapable", "❓ Untested"]:
        ids = summary[verdict_label]
        ids_str = ", ".join(ids) if ids else "—"
        lines.append(f"| {verdict_label} | {len(ids)} | {ids_str} |")
    lines.append("")

    return lines


def generate_safety_guide(
    results: list[EvalResult],
    output: Path,
    model: str | None = None,
) -> None:
    """Generate LLM Embedded Code Safety Guide from benchmark results.

    Args:
        results: Benchmark EvalResult list.
        output: Path to write the Safety Guide markdown.
        model: Model name for the report header. Auto-detected if None.
    """
    if model is None:
        model = results[0].model if results else "Unknown"

    lines: list[str] = []

    # Header
    lines.append("# LLM Embedded Code Safety Guide")
    lines.append("")
    lines.append(f"**Model:** {model}")
    lines.append(f"**Cases evaluated:** {len(set(r.case_id for r in results))}")
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    if total:
        lines.append(f"**Overall pass@1:** {passed}/{total} ({passed / total:.1%})")
    else:
        lines.append("")
    lines.append("")

    # Section 1: Capability Boundary
    lines.append(CAPABILITY_BOUNDARY)

    # Section 2: Reasoning Type Risk Assessment (dynamic)
    lines.extend(_reasoning_risk_table(results))
    lines.append("")

    # Pre-compute category pass rates (shared by sections 3 and 6)
    cat_rates = _calculate_category_pass_rates(results)

    # Section 3: Task-specific checklists (static + dynamic stats)
    lines.extend(_task_checklists(results, cat_rates))
    lines.append("")

    # Section 4: Failure Pattern Statistics (dynamic)
    lines.extend(_failure_statistics(results))
    lines.append("")

    # Section 5: Engineer Guidelines
    lines.extend(_engineer_guidelines(results))
    lines.append("")

    # Section 6: Factor Competency Matrix (dynamic)
    lines.extend(_factor_competency_matrix(results, cat_rates))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Safety Guide written to %s", output)


def _reasoning_risk_table(results: list[EvalResult]) -> list[str]:
    """Generate reasoning-type risk assessment from results."""
    lines = [
        "## LLM Risk by Reasoning Type",
        "",
        "| Reasoning Level | Success Rate | Verdict | Action |",
        "|-----------------|-------------|---------|--------|",
    ]

    by_type: dict[str, list[bool]] = defaultdict(list)
    for r in results:
        for rt in r.reasoning_types:
            rt_name = rt.value if hasattr(rt, "value") else str(rt)
            by_type[rt_name].append(r.passed)

    labels = {
        "api_recall": ("L1 API Recall", "Trust"),
        "rule_application": ("L2 Rule Application", "Verify"),
        "cross_domain": ("L3 Cross-Domain", "Review"),
        "system_reasoning": ("L4 System Reasoning", "Rewrite"),
    }

    for rt_name in [
        "api_recall",
        "rule_application",
        "cross_domain",
        "system_reasoning",
    ]:
        if rt_name not in by_type:
            continue
        passes = by_type[rt_name]
        rate = sum(passes) / len(passes) if passes else 0.0
        label, default_action = labels.get(rt_name, (rt_name, "Review"))

        if rate >= 0.9:
            verdict = "Reliable"
            action = "Light review"
        elif rate >= 0.75:
            verdict = "Mostly reliable"
            action = "Standard review"
        elif rate >= 0.6:
            verdict = "Unreliable"
            action = "Expert review required"
        else:
            verdict = "Do not trust"
            action = "Write manually"

        lines.append(f"| {label} | {rate:.0%} | {verdict} | {action} |")

    return lines


def _calculate_category_pass_rates(
    results: list[EvalResult],
) -> dict[str, float]:
    """Calculate pass rate per category from results."""
    by_cat: dict[str, list[bool]] = defaultdict(list)
    for r in results:
        cat = r.category.value if r.category else r.case_id.rsplit("-", 1)[0]
        by_cat[cat].append(r.passed)
    return {cat: sum(passes) / len(passes) for cat, passes in by_cat.items() if passes}


def _task_success_rate(
    categories: list[str],
    cat_rates: dict[str, float],
) -> str:
    """Compute weighted success rate for a task from its mapped categories.

    Returns a formatted string like '72%' or 'N/A' if no data.
    """
    rates = [cat_rates[c] for c in categories if c in cat_rates]
    if not rates:
        return "N/A (no benchmark data)"
    weighted = sum(rates) / len(rates)
    return f"{weighted:.0%}"


def _task_checklists(
    results: list[EvalResult],
    cat_rates: dict[str, float] | None = None,
) -> list[str]:
    """Generate per-task checklists with dynamic failure data."""
    lines = [
        "## Task-Specific Checklists",
        "",
    ]

    if cat_rates is None:
        cat_rates = _calculate_category_pass_rates(results)

    for task_name, info in TASK_CHECKLISTS.items():
        categories = info["categories"]
        success_rate = _task_success_rate(categories, cat_rates)
        lines.append(f"### {task_name}")
        lines.append(
            f"**Risk: {info['risk']}** | Success rate: {success_rate}"
            f" | {info['reasoning_level']}"
        )
        lines.append("")
        for item in info["checklist"]:
            lines.append(f"- [ ] {item}")
        lines.append("")
        lines.append(f"*Common failure:* {info['common_failure']}")
        lines.append("")

    return lines


def _failure_statistics(results: list[EvalResult]) -> list[str]:
    """Generate failure pattern statistics from benchmark data."""
    lines = [
        "## Failure Pattern Statistics",
        "",
    ]

    failed = [r for r in results if not r.passed]
    if not failed:
        lines.append("No failures detected in this benchmark run.")
        return lines

    pattern_counts: Counter[str] = Counter()
    for r in failed:
        fc = classify_failure(r)
        if fc:
            pattern_counts[fc.pattern.value] += 1

    total_failures = sum(pattern_counts.values())
    if total_failures == 0:
        lines.append("No classifiable failure patterns.")
        return lines

    lines.extend(
        [
            f"**Total failures:** {len(failed)}",
            "",
            "| Failure Pattern | Count | % of Failures | What It Means |",
            "|-----------------|-------|---------------|---------------|",
        ]
    )

    descriptions = {
        "happy_path_bias": "Error cleanup paths missing or incomplete",
        "semantic_mismatch": "Code compiles but has wrong HW semantics",
        "resource_imbalance": "Alloc without free, register without unregister",
        "order_violation": "Init/setup/use sequence incorrect",
        "cross_platform": "Wrong platform API used (e.g., FreeRTOS in Zephyr)",
        "api_hallucination": "Non-existent API or CONFIG called",
        "missing_safety": "Forbidden API in ISR, missing safety guard",
        "unknown": "Unclassified failure",
    }

    for pattern, count in pattern_counts.most_common():
        pct = count / total_failures * 100
        desc = descriptions.get(pattern, "")
        lines.append(f"| {pattern} | {count} | {pct:.0f}% | {desc} |")

    return lines


def _engineer_guidelines(results: list[EvalResult]) -> list[str]:
    """Generate actionable guidelines for engineers."""
    return [
        "## Engineer Guidelines",
        "",
        "### When to Trust LLM Output",
        "",
        "- **L1 tasks (Kconfig, basic GPIO):** Use LLM output as-is with light review",
        "- **L2 tasks (rule-based):** Review for platform-specific rules"
        " (ISR constraints, deprecated APIs)",
        "- **L3 tasks (cross-domain):** Use LLM as starting point,"
        " expert must verify HW semantics",
        "- **L4 tasks (system reasoning):** LLM output is reference only"
        " — write error paths manually",
        "",
        "### Recommended Workflow",
        "",
        "1. Generate code with LLM",
        "2. Check the task-specific checklist above",
        "3. Run static analysis (check_utils from EmbedEval)",
        "4. Compile with target SDK (west build / idf.py build)",
        "5. Test on real hardware for timing-critical code",
        "",
        "### What LLMs Will Never Replace",
        "",
        "- Oscilloscope/logic analyzer debugging",
        "- Board bring-up and power sequencing",
        "- EMC/EMI compliance testing",
        "- Safety certification (IEC 61508, ISO 26262)",
        "- Production test fixture design",
        "- Field failure root cause analysis",
    ]
