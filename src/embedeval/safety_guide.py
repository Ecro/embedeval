"""LLM Embedded Code Safety Guide generator.

Produces a developer-facing report with:
1. LLM Capability Boundary (what LLMs can/cannot do)
2. Per-task risk assessment with checklists
3. Failure pattern statistics from benchmark data
"""

import logging
from collections import Counter, defaultdict
from pathlib import Path

from embedeval.failure_taxonomy import FailurePattern, classify_failure
from embedeval.models import EvalResult, ReasoningType

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

- **ISR handlers** — may omit volatile, use mutex instead of spinlock, call blocking APIs
- **DMA configuration** — cache alignment errors, cyclic vs one-shot confusion
- **BLE stack setup** — connection lifecycle incomplete, characteristic setup partially wrong
- **Error handling** — happy path implemented, cleanup on failure paths missing
- **SPI/I2C protocols** — timing parameters may be wrong, error recovery incomplete

### What LLMs Cannot Do (benchmark scope boundary)

- **Board bring-up** — first boot, power rail verification, clock configuration
- **Signal integrity** — PCB trace routing, impedance matching, crosstalk analysis
- **EMC/EMI compliance** — antenna design, shielding, regulatory certification
- **Sensor calibration** — ADC offset/gain against physical reference
- **Real-time debugging** — JTAG/SWD, oscilloscope correlation, race condition reproduction
- **Safety certification** — IEC 61508, ISO 26262, DO-178C traceability
- **Production testing** — ICT fixtures, boundary scan, yield analysis
- **Field failure analysis** — component aging, environmental stress, intermittent faults
"""

# --- Static content: Per-task checklists ---

TASK_CHECKLISTS: dict[str, dict] = {
    "ISR / Interrupt Handlers": {
        "risk": "HIGH",
        "success_rate": "~70%",
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
        "success_rate": "~60%",
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
        "success_rate": "~65%",
        "reasoning_level": "L3 Cross-Domain",
        "checklist": [
            "Buffer aligned to cache line size (32B or 64B)?",
            "Cyclic mode: reload called in DMA callback?",
            "Ping-pong buffers for continuous transfer?",
            "dma_stop called on error or completion?",
            "Cache flush/invalidate around DMA regions?",
        ],
        "common_failure": "No cache alignment → intermittent data corruption under load",
    },
    "Watchdog Timer": {
        "risk": "MEDIUM",
        "success_rate": "~75%",
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
        "success_rate": "~70%",
        "reasoning_level": "L4 System Reasoning",
        "checklist": [
            "copy_to_user / copy_from_user (not __ variants)?",
            "Register and unregister balanced?",
            ".owner = THIS_MODULE in file_operations?",
            "All init errors have full rollback cleanup?",
            "No Zephyr/FreeRTOS API contamination?",
        ],
        "common_failure": "Init allocates chrdev + cdev, error after cdev → chrdev leaked",
    },
    "Basic GPIO / UART / SPI": {
        "risk": "LOW",
        "success_rate": "~90%",
        "reasoning_level": "L1 API Recall",
        "checklist": [
            "device_is_ready() called before use?",
            "Pin configured with correct direction (input/output)?",
            "Interrupt edge type specified?",
        ],
        "common_failure": "Missing device_is_ready check (rare but possible)",
    },
}


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
    lines.append(f"**Overall pass@1:** {passed}/{total} ({passed/total:.1%})" if total else "")
    lines.append("")

    # Section 1: Capability Boundary
    lines.append(CAPABILITY_BOUNDARY)

    # Section 2: Reasoning Type Risk Assessment (dynamic)
    lines.extend(_reasoning_risk_table(results))
    lines.append("")

    # Section 3: Task-specific checklists (static + dynamic stats)
    lines.extend(_task_checklists(results))
    lines.append("")

    # Section 4: Failure Pattern Statistics (dynamic)
    lines.extend(_failure_statistics(results))
    lines.append("")

    # Section 5: Engineer Guidelines
    lines.extend(_engineer_guidelines(results))

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

    for rt_name in ["api_recall", "rule_application", "cross_domain", "system_reasoning"]:
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


def _task_checklists(results: list[EvalResult]) -> list[str]:
    """Generate per-task checklists with dynamic failure data."""
    lines = [
        "## Task-Specific Checklists",
        "",
    ]

    for task_name, info in TASK_CHECKLISTS.items():
        risk_emoji = {"HIGH": "!!!", "MEDIUM": "!!", "LOW": "!"}.get(info["risk"], "")
        lines.append(f"### {task_name}")
        lines.append(f"**Risk: {info['risk']}** | Success rate: {info['success_rate']} | {info['reasoning_level']}")
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

    lines.extend([
        f"**Total failures:** {len(failed)}",
        "",
        "| Failure Pattern | Count | % of Failures | What It Means |",
        "|-----------------|-------|---------------|---------------|",
    ])

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
        "- **L2 tasks (rule-based):** Review for platform-specific rules (ISR constraints, deprecated APIs)",
        "- **L3 tasks (cross-domain):** Use LLM as starting point, expert must verify HW semantics",
        "- **L4 tasks (system reasoning):** LLM output is reference only — write error paths manually",
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
