"""Negative tests for Yocto multi-license recipe.

Reference: cases/yocto-008/reference/main.c (the .bb recipe)
Checks:    cases/yocto-008/checks/behavior.py

The reference recipe:
  LICENSE = "MIT & GPL-2.0-only"
  — no RDEPENDS or FILES overrides present

The behavior checks used as mutation targets:
  correct_gpl_spdx_format  → must NOT contain 'GPLv2' or bare '"GPL-2.0"'
  colon_override_syntax    → must NOT have RDEPENDS_${PN} / FILES_${PN} etc.

Mutation strategy
-----------------
* wrong_gpl_spdx        : replace GPL-2.0-only with GPLv2 (pre-SPDX name)
  → correct_gpl_spdx_format fails
* deprecated_underscore_override : inject RDEPENDS_${PN} line (Yocto <3.4 syntax)
  → colon_override_syntax fails
"""

NEGATIVES = [
    {
        "name": "wrong_gpl_spdx",
        "description": (
            "GPL-2.0-only replaced with GPLv2 — non-SPDX identifier; "
            "Yocto 4.0+ rejects non-SPDX license names, breaking the build"
        ),
        "mutation": lambda code: code.replace("GPL-2.0-only", "GPLv2"),
        "must_fail": ["correct_gpl_spdx_format"],
    },
    {
        "name": "deprecated_underscore_override",
        "description": (
            "RDEPENDS_${PN} syntax injected (Yocto <3.4 style) — "
            "Yocto 4.0+ (kirkstone+) requires colon syntax RDEPENDS:${PN}, "
            "underscore causes a parse error or silent ignore"
        ),
        # Append a RDEPENDS line using the deprecated underscore override syntax.
        "mutation": lambda code: code + "\nRDEPENDS_${PN} = \"bash\"\n",
        "must_fail": ["colon_override_syntax"],
    },
]
