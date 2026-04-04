"""Negative tests for MCUboot Kconfig fragment.

Reference: cases/boot-001/reference/main.c  (actually a prj.conf Kconfig fragment)
Checks:    cases/boot-001/checks/behavior.py  +  static.py

The reference prj.conf contains:
    CONFIG_BOOTLOADER_MCUBOOT=y
    CONFIG_MCUBOOT_IMG_MANAGER=y
    CONFIG_IMG_MANAGER=y
    CONFIG_FLASH=y
    CONFIG_STREAM_FLASH=y
    CONFIG_IMG_BLOCK_BUF_SIZE=512

Mutation strategy
-----------------
* missing_img_manager : removes CONFIG_IMG_MANAGER=y.
  The static check img_manager_enabled will fail.
  The behavior check img_manager_dependency will also fail because
  MCUBOOT_IMG_MANAGER=y is present but IMG_MANAGER is absent.

* missing_flash : removes CONFIG_FLASH=y.
  The static check flash_enabled will fail.
  The behavior check flash_dependency will also fail.
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_img_manager",
        "description": (
            "CONFIG_IMG_MANAGER=y removed — CONFIG_MCUBOOT_IMG_MANAGER depends on "
            "CONFIG_IMG_MANAGER; Kconfig dependency unsatisfied, build will error"
        ),
        "mutation": lambda code: _remove_lines(code, "CONFIG_IMG_MANAGER=y"),
        "must_fail": ["img_manager_enabled"],
    },
    {
        "name": "missing_flash",
        "description": (
            "CONFIG_FLASH=y removed — MCUboot requires flash driver for image "
            "storage and swap; linker will fail with undefined flash API symbols"
        ),
        "mutation": lambda code: _remove_lines(code, "CONFIG_FLASH=y"),
        "must_fail": ["flash_enabled"],
    },
]
