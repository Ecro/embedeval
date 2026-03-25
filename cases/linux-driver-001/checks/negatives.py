"""Negative tests for Linux character device driver.

Reference: cases/linux-driver-001/reference/main.c
Checks:    cases/linux-driver-001/checks/behavior.py

The reference:
  - Uses copy_to_user() and copy_from_user() for all user-space data transfer
  - Has proper error-path cleanup in __init: on cdev_add failure calls
    unregister_chrdev_region; on class_create failure calls cdev_del then
    unregister_chrdev_region.

Mutation strategy
-----------------
* missing_cleanup      : removes the cdev_del call from error paths.
  extract_error_blocks() finds 'if (ret < 0)' / 'if (IS_ERR(...))' blocks;
  the check looks for 'cdev_del' or 'unregister_chrdev_region' inside those blocks.
  With cdev_del gone one error block contains only unregister_chrdev_region
  but the class_create error block has neither → init_error_path_cleanup fails.

* missing_copy_to_user : replaces copy_to_user with memcpy and copy_from_user with memcpy.
  Behavior check looks for the exact string 'copy_to_user' → copy_to_user_used fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_cleanup",
        "description": (
            "cdev_del() and unregister_chrdev_region() missing from all error paths — "
            "resource leak when cdev_add or class_create fails"
        ),
        # extract_error_blocks() finds 'if (<expr> < 0)' and 'if (IS_ERR(...))' blocks.
        # init_error_path_cleanup passes when ANY error block contains 'cdev_del' OR
        # 'unregister_chrdev_region'.  We must remove cleanup from every error block:
        #   - cdev_add block:    remove its 'unregister_chrdev_region' line
        #   - class_create block: remove both 'cdev_del' and 'unregister_chrdev_region' lines
        # After this no error block contains either symbol → check fails.
        "mutation": lambda code: (
            code
            # cdev_add error block: strip unregister_chrdev_region
            .replace(
                "\tif (ret < 0) {\n\t\tunregister_chrdev_region(dev_num, 1);\n\t\treturn ret;\n\t}",
                "\tif (ret < 0) {\n\t\treturn ret;\n\t}",
            )
            # class_create error block: strip both cdev_del and unregister
            .replace(
                "\t\tcdev_del(&my_cdev);\n\t\tunregister_chrdev_region(dev_num, 1);\n\t\treturn PTR_ERR(dev_class);",
                "\t\treturn PTR_ERR(dev_class);",
            )
        ),
        "must_fail": ["init_error_path_cleanup"],
    },
    {
        "name": "missing_copy_to_user",
        "description": "Direct memcpy to user pointer instead of copy_to_user — kernel security vulnerability",
        "mutation": lambda code: (
            code
            .replace("copy_to_user(buf,", "memcpy(buf,")
            .replace("copy_from_user(device_buf,", "memcpy(device_buf,")
        ),
        "must_fail": ["copy_to_user_used"],
    },
    # --- Subtle ---
    {
        "name": "unsafe_copy_to_user",
        "mutation": lambda code: code.replace("copy_to_user", "__copy_to_user").replace("copy_from_user", "__copy_from_user"),
        "should_fail": ["copy_to_user_used"],
        "bug_description": "__copy_to_user skips access_ok() check — kernel security vulnerability",
    },
    {
        "name": "partial_cleanup_only",
        "mutation": lambda code: code.replace("unregister_chrdev_region", "/* unregister_chrdev_region */"),
        "should_fail": ["init_error_path_cleanup"],
        "bug_description": "cdev_del called but chrdev_region not unregistered — partial cleanup leaks major number",
    },
    {
        "name": "error_check_no_return",
        "mutation": lambda code: code.replace(
            "return ret;",
            '/* return ret; */ printk("continuing despite error\\n");',
            1  # only first occurrence
        ),
        "should_fail": ["init_error_path_cleanup"],
        "bug_description": "Error detected and logged but execution continues — resources used in undefined state",
    },
]
