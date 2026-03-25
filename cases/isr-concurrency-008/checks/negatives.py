"""Negative tests for lock-free SPSC ring queue.

Reference: cases/isr-concurrency-008/reference/main.c
Checks:    cases/isr-concurrency-008/checks/static.py  (memory_barrier_present,
            bitwise_mask_not_modulo, atomic_t_for_indices)

The reference uses:
  - compiler_barrier() between data write and atomic_set (index advance)
  - QUEUE_MASK = (QUEUE_SIZE - 1)  with  buf[w & QUEUE_MASK]  (bitwise mask)
  - atomic_t write_idx / read_idx  with  atomic_get / atomic_set

Mutation strategy
-----------------
* missing_barrier     : removes all 'compiler_barrier' lines.
  static check scans for any barrier keyword → memory_barrier_present fails.

* modulo_instead_of_mask : replaces the QUEUE_MASK define and all '& QUEUE_MASK' usages
  with '% QUEUE_SIZE'.  Static check looks for '& (SIZE-1)' or '& *MASK*' — both absent
  → bitwise_mask_not_modulo fails.

* plain_int_indices   : replaces 'atomic_t' declarations with 'uint32_t' and rewrites
  atomic_get / atomic_set to plain reads/writes.
  Static check looks for 'atomic_t' keyword → atomic_t_for_indices fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_barrier",
        "description": "No memory barrier before index advance — consumer may read stale data",
        "mutation": lambda code: _remove_lines(code, "compiler_barrier"),
        "must_fail": ["memory_barrier_present"],
    },
    {
        "name": "modulo_instead_of_mask",
        "description": "Modulo % used instead of bitwise & mask — slower and semantically fragile",
        # Replace the QUEUE_MASK define so it no longer looks like a mask constant,
        # then replace all '& QUEUE_MASK' usages with '% QUEUE_SIZE'.
        "mutation": lambda code: (
            code
            .replace("#define QUEUE_MASK (QUEUE_SIZE - 1)", "#define QUEUE_MOD QUEUE_SIZE")
            .replace("& QUEUE_MASK", "% QUEUE_SIZE")
        ),
        "must_fail": ["bitwise_mask_not_modulo"],
    },
    {
        "name": "plain_int_indices",
        "description": "Plain uint32_t indices instead of atomic_t — data race between ISR and thread",
        "mutation": lambda code: (
            code
            # Replace atomic_t field declarations with plain uint32_t
            .replace("\tatomic_t   write_idx;", "\tuint32_t   write_idx;")
            .replace("\tatomic_t   read_idx;", "\tuint32_t   read_idx;")
            # Replace atomic_get() reads with plain dereference
            .replace("atomic_val_t w = atomic_get(&q->write_idx);", "uint32_t w = q->write_idx;")
            .replace("atomic_val_t r = atomic_get(&q->read_idx);", "uint32_t r = q->read_idx;")
            # Replace atomic_set() writes with plain assignment
            .replace("atomic_set(&q->write_idx, w + 1);", "q->write_idx = w + 1;")
            .replace("atomic_set(&q->read_idx, r + 1);", "q->read_idx = r + 1;")
            # Replace the initialization atomic_set calls in main
            .replace("atomic_set(&q.write_idx, 0);", "q.write_idx = 0;")
            .replace("atomic_set(&q.read_idx, 0);", "q.read_idx = 0;")
        ),
        "must_fail": ["atomic_t_for_indices"],
    },
    # --- Subtle ---
    {
        "name": "volatile_instead_of_atomic",
        "mutation": lambda code: code.replace("atomic_t", "volatile uint32_t").replace(
            "atomic_get(&", "(").replace("atomic_set(&", "*(").replace(
            ", w + 1)", " = w + 1)").replace(", r + 1)", " = r + 1)").replace(
            ", 0)", " = 0)"),
        "should_fail": ["atomic_t_for_indices"],
        "bug_description": "volatile is NOT atomic — read-modify-write race on multi-core or with optimizing compiler",
    },
]
