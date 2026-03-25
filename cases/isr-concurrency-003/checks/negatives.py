"""Negative tests for spinlock-protected shared state between ISR and thread.

Reference: cases/isr-concurrency-003/reference/main.c
Checks:    cases/isr-concurrency-003/checks/behavior.py

The reference uses:
  - K_SPINLOCK_DEFINE / k_spin_lock / k_spin_unlock / k_spinlock_key_t
  - isr_handler() as the simulated ISR body
  - reader_thread() as the consumer thread

Mutation strategy
-----------------
* mutex_instead_of_spinlock : replaces spinlock primitives with k_mutex variants.
  find_isr_bodies() matches 'isr_handler' (contains 'handler') and checks for k_mutex
  inside that body → no_mutex_in_isr fails.
  Also, k_spin_lock count becomes 0 → spinlock_balanced fails.

* missing_unlock : removes all k_spin_unlock lines → lock_count != unlock_count
  → spinlock_balanced fails.

* printk_in_isr : injects a printk call inside isr_handler body.
  find_isr_bodies() extracts the isr_handler body (matches 'handler' pattern),
  check_no_isr_forbidden() finds 'printk' in it → no_forbidden_apis_in_isr fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "mutex_instead_of_spinlock",
        "description": "k_mutex used in ISR body — will deadlock because mutex can sleep",
        "mutation": lambda code: (
            code
            .replace("K_SPINLOCK_DEFINE(counter_lock)", "K_MUTEX_DEFINE(counter_lock)")
            .replace("k_spinlock_key_t key;", "int key;")
            .replace("key = k_spin_lock(&counter_lock);", "k_mutex_lock(&counter_lock, K_FOREVER);")
            .replace("k_spin_unlock(&counter_lock, key);", "k_mutex_unlock(&counter_lock);")
        ),
        "must_fail": ["no_mutex_in_isr"],
    },
    {
        "name": "missing_unlock",
        "description": "Spinlock acquired but never released — deadlock on next lock attempt",
        "mutation": lambda code: _remove_lines(code, "k_spin_unlock"),
        "must_fail": ["spinlock_balanced"],
    },
    {
        "name": "printk_in_isr",
        "description": "printk() called inside ISR body — blocking I/O in interrupt context",
        # isr_handler body contains 'shared_counter++'; insert printk before it.
        # find_isr_bodies() matches functions with 'handler' in name, so isr_handler qualifies.
        "mutation": lambda code: code.replace(
            "\tshared_counter++;",
            '\tprintk("ISR fired\\n");\n\tshared_counter++;',
        ),
        "must_fail": ["no_forbidden_apis_in_isr"],
    },
    # --- Subtle mutations ---
    {
        "name": "irq_lock_instead_of_spinlock",
        "mutation": lambda code: code.replace(
            "k_spin_lock(&counter_lock)", "irq_lock()"
        ).replace(
            "k_spin_unlock(&counter_lock, key)", "irq_unlock(key)"
        ).replace("k_spinlock_key_t", "unsigned int"),
        "should_fail": ["no_mutex_in_isr"],
        "bug_description": "irq_lock disables ALL interrupts globally — worse than spinlock but passes mutex check",
    },
    {
        "name": "spinlock_key_hardcoded_zero",
        "mutation": lambda code: code.replace(
            "key = k_spin_lock(&counter_lock);",
            "k_spin_lock(&counter_lock); k_spinlock_key_t key = {0};"
        ),
        "should_fail": ["key_passed_to_unlock"],
        "bug_description": "Spinlock key not saved from k_spin_lock — interrupt state not restored on unlock",
    },
]
