"""Negative tests for Yocto BitBake recipe.

Reference: cases/yocto-001/reference/main.c  (actually a .bb recipe)
Checks:    cases/yocto-001/checks/behavior.py

The reference recipe:
  - do_install uses ${D}${bindir}  (staging directory prefix)
  - do_compile uses ${CC} for cross-compilation

Mutation strategy
-----------------
* no_d_prefix : replaces ${D}${bindir} with /usr/bin (hardcoded absolute path).
  The check install_uses_d_prefix looks for "${D}" — will fail.
  The check uses_bindir_variable also fails because has_hardcoded becomes True.

* no_cc_variable : replaces ${CC} with gcc (native compiler).
  The check uses_cc_variable looks for "${CC}" — will fail.
"""

NEGATIVES = [
    {
        "name": "no_d_prefix",
        "description": (
            "do_install uses hardcoded /usr/bin instead of ${D}${bindir} — "
            "files are installed into the host rootfs, not the staging sysroot; "
            "BitBake package QA will flag this as a staging error"
        ),
        "mutation": lambda code: code.replace("${D}${bindir}", "/usr/bin"),
        "must_fail": ["install_uses_d_prefix"],
    },
    {
        "name": "no_cc_variable",
        "description": (
            "${CC} replaced with bare gcc — recipe uses the host native compiler "
            "instead of the Yocto cross-compiler; produces wrong-architecture binaries"
        ),
        "mutation": lambda code: code.replace("${CC}", "gcc"),
        "must_fail": ["uses_cc_variable"],
    },
]
