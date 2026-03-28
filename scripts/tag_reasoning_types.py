#!/usr/bin/env python3
"""Auto-tag TCs with reasoning_types based on behavior.py check names.

Maps each check_name to a reasoning level (L1-L4), then assigns the
highest-level reasoning types found in each TC.

Usage:
    uv run python scripts/tag_reasoning_types.py
    uv run python scripts/tag_reasoning_types.py --dry-run
"""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CASES_DIR = ROOT / "cases"

# Check name → reasoning type mapping
CHECK_REASONING_MAP: dict[str, str] = {
    # L1: API Recall — single API usage patterns
    "led_configured_output": "api_recall",
    "button_configured_input": "api_recall",
    "interrupt_edge_triggered": "api_recall",
    "led_toggle_in_callback": "api_recall",
    "k_sleep_present": "api_recall",
    "reader_thread_defined": "api_recall",
    "fops_read_write": "api_recall",
    "this_module_owner": "api_recall",
    "bt_enable_error_check": "api_recall",
    "primary_service_attribute": "api_recall",
    "custom_128bit_uuid": "api_recall",
    "producer_sleeps_between_sends": "api_recall",
    "consumer_blocking_get": "api_recall",
    "queue_capacity_positive": "api_recall",
    "different_thread_priorities": "api_recall",
    "all_required_configs_enabled": "api_recall",
    "flash_dependency": "api_recall",

    # L2: Rule Application — known embedded rules
    "no_forbidden_apis_in_isr": "rule_application",
    "no_cross_platform_apis": "rule_application",
    "no_cross_platform_ble_apis": "rule_application",
    "no_mutex_in_isr": "rule_application",
    "no_zephyr_apis_in_linux_driver": "rule_application",
    "no_freertos_apis": "rule_application",
    "no_hallucinated_config_options": "rule_application",
    "no_deprecated_gpio_request": "rule_application",
    "no_hallucinated_apis": "rule_application",
    "device_ready_check": "rule_application",
    "dependency_chain_consistent": "rule_application",
    "dma_dependency_chain": "rule_application",
    "no_newlib_minimal_libc_conflict": "rule_application",
    "no_upgrade_only": "rule_application",
    "no_single_slot": "rule_application",
    "write_offset_bounds_check": "rule_application",
    "write_attribute_len_validated": "rule_application",

    # L3: Cross-Domain — combining C + RTOS + HW knowledge
    "spinlock_balanced": "cross_domain",
    "key_passed_to_unlock": "cross_domain",
    "spinlock_used_in_both_contexts": "cross_domain",
    "isr_modifies_shared": "cross_domain",
    "thread_reads_under_lock": "cross_domain",
    "volatile_shared": "cross_domain",
    "worker_flag_volatile": "cross_domain",
    "health_flag_not_plain_int": "cross_domain",
    "cache_aligned": "cross_domain",
    "cyclic_enabled": "cross_domain",
    "reload_in_callback": "cross_domain",
    "ping_pong_buffers": "cross_domain",
    "copy_to_user_used": "cross_domain",
    "copy_from_user_used": "cross_domain",
    "enable_before_advertise": "cross_domain",
    "callback_before_sleep": "cross_domain",
    "timer_period_less_than_wdt_timeout": "cross_domain",
    "reset_soc_flag": "cross_domain",

    # L4: System Reasoning — backward/whole-system thinking
    "init_error_handling": "system_reasoning",
    "init_error_path_cleanup": "system_reasoning",
    "init_cleanup_no_comments": "system_reasoning",
    "error_path_returns": "system_reasoning",
    "dma_error_handling": "system_reasoning",
    "dma_stop_called": "system_reasoning",
    "register_unregister_balanced": "system_reasoning",
    "wdt_feed_is_conditional": "system_reasoning",
    "flag_reset_after_check": "system_reasoning",
    "worker_sets_flag_in_loop": "system_reasoning",
    "install_before_setup": "system_reasoning",
    "wdt_setup_before_timer_start": "system_reasoning",
    "img_manager_dependency": "system_reasoning",
    "no_upgrade_only_swap_conflict": "system_reasoning",
    "no_single_slot_swap_conflict": "system_reasoning",
    "message_struct_with_data": "system_reasoning",
    "read_uses_attr_read": "system_reasoning",
}

# Keyword fallback for unmapped check names
KEYWORD_REASONING: list[tuple[list[str], str]] = [
    (["error", "cleanup", "rollback", "free", "unregister", "stop", "release"], "system_reasoning"),
    (["volatile", "barrier", "align", "cache", "spinlock", "atomic", "cyclic", "copy_to", "copy_from"], "cross_domain"),
    (["no_", "forbidden", "deprecated", "hallucin", "cross_platform", "device_ready"], "rule_application"),
    (["configured", "present", "defined", "enabled", "dependency"], "api_recall"),
]


def extract_check_names(behavior_py: Path) -> list[str]:
    """Extract check_name values from a behavior.py file."""
    content = behavior_py.read_text(encoding="utf-8")
    return re.findall(r'check_name="([^"]+)"', content)


def classify_check(check_name: str) -> str:
    """Classify a single check name into a reasoning type."""
    if check_name in CHECK_REASONING_MAP:
        return CHECK_REASONING_MAP[check_name]

    name_lower = check_name.lower()
    for keywords, reasoning_type in KEYWORD_REASONING:
        if any(kw in name_lower for kw in keywords):
            return reasoning_type

    return "api_recall"  # default


def tag_case(case_dir: Path) -> list[str]:
    """Determine reasoning_types for a case based on its checks."""
    behavior_py = case_dir / "checks" / "behavior.py"
    if not behavior_py.is_file():
        return []

    check_names = extract_check_names(behavior_py)
    types_found: set[str] = set()
    for check_name in check_names:
        types_found.add(classify_check(check_name))

    # Return sorted by reasoning level (L4 first for emphasis)
    order = ["system_reasoning", "cross_domain", "rule_application", "api_recall"]
    return [t for t in order if t in types_found]


def apply_reasoning_types(cases_dir: Path, dry_run: bool = False) -> int:
    """Tag all cases with reasoning_types in metadata.yaml."""
    updated = 0

    for case_dir in sorted(cases_dir.iterdir()):
        meta_file = case_dir / "metadata.yaml"
        if not case_dir.is_dir() or not meta_file.is_file():
            continue

        types = tag_case(case_dir)
        if not types:
            continue

        content = meta_file.read_text(encoding="utf-8")

        # Format as YAML list
        types_yaml = "[" + ", ".join(types) + "]"

        existing = re.search(r"^reasoning_types:.*$", content, re.MULTILINE)
        if existing:
            new_line = f"reasoning_types: {types_yaml}"
            if existing.group(0).strip() == f"reasoning_types: {types_yaml}":
                continue
            new_content = re.sub(
                r"^reasoning_types:.*$", new_line, content, flags=re.MULTILINE
            )
        else:
            new_content = content.rstrip() + f"\nreasoning_types: {types_yaml}\n"

        if not dry_run:
            meta_file.write_text(new_content, encoding="utf-8")
        updated += 1

    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Tag TCs with reasoning types")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Tagging reasoning types...")

    # Stats
    from collections import Counter
    type_counts: Counter[str] = Counter()
    for case_dir in sorted(CASES_DIR.iterdir()):
        if not case_dir.is_dir():
            continue
        types = tag_case(case_dir)
        for t in types:
            type_counts[t] += 1

    print(f"\n  Cases with each reasoning type:")
    print(f"    L1 api_recall:       {type_counts.get('api_recall', 0)}")
    print(f"    L2 rule_application: {type_counts.get('rule_application', 0)}")
    print(f"    L3 cross_domain:     {type_counts.get('cross_domain', 0)}")
    print(f"    L4 system_reasoning: {type_counts.get('system_reasoning', 0)}")

    if args.dry_run:
        print("\n  [DRY RUN] No files modified")
    else:
        updated = apply_reasoning_types(CASES_DIR)
        print(f"\n  Updated {updated} metadata.yaml files")


if __name__ == "__main__":
    main()
