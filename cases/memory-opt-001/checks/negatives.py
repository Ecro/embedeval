"""Negative tests for memory slab allocation.

Reference: cases/memory-opt-001/reference/main.c
Checks:    cases/memory-opt-001/checks/behavior.py

The reference:
  - Calls k_mem_slab_alloc (once) then k_mem_slab_free (once).
    balanced_alloc_free: free_count >= alloc_count → passes.
  - Uses only slab APIs; no malloc/calloc/k_malloc → no_heap_behavioral passes.

Mutation strategy
-----------------
* missing_free : removes the k_mem_slab_free call line. After removal
  alloc_count=1 > free_count=0 → balanced_alloc_free fails.

* add_heap_malloc : injects a malloc() call. The no_heap_behavioral check
  looks for 'malloc(' in stripped code → the check fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_free",
        "description": (
            "k_mem_slab_free() call removed — allocated slab block is never "
            "returned, exhausting the fixed slab pool over repeated calls"
        ),
        # Reference: "\tk_mem_slab_free(&my_slab, block);\n"
        # Removing this line leaves alloc_count=1, free_count=0 → fails balanced_alloc_free.
        "mutation": lambda code: _remove_lines(code, "k_mem_slab_free"),
        "must_fail": ["balanced_alloc_free"],
    },
    {
        "name": "add_heap_malloc",
        "description": (
            "malloc() call injected into the program — heap allocation used "
            "alongside the slab, defeating the deterministic memory layout"
        ),
        # Append a malloc call inside main before the return statement.
        # 'malloc(' is in the heap_funcs list checked by no_heap_behavioral.
        "mutation": lambda code: code.replace(
            "\treturn 0;\n}",
            "\tvoid *heap_ptr = malloc(16); /* accidental heap use */\n\treturn 0;\n}",
        ),
        "must_fail": ["no_heap_behavioral"],
    },
    # --- Subtle ---
    {
        "name": "free_before_alloc",
        "mutation": lambda code: code.replace(
            "\treturn ret;\n\t}\n\n\tmemset(block",
            "\treturn ret;\n\t}\n\n\tk_mem_slab_free(&my_slab, block); /* premature free */\n\tmemset(block",
        ),
        "should_fail": ["alloc_before_free"],
        "bug_description": "Block freed before use — use-after-free when memset and printk access the now-released block",
    },
]
