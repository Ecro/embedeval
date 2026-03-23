Write a Yocto BitBake recipe (.bb file) for an out-of-tree Linux kernel module.

Requirements:
1. Set SUMMARY, LICENSE = "GPL-2.0-only", LIC_FILES_CHKSUM with md5sum
2. Set SRC_URI to include the module source files:
   - file://mymodule.c
   - file://Makefile
3. Set S = "${WORKDIR}"
4. Use "inherit module" to activate kernel module build support
5. Set KERNEL_MODULE_AUTOLOAD += "mymodule" so the module loads at boot
6. The Makefile in SRC_URI must use KBUILD-style syntax:
   - obj-m += mymodule.o
   - The build target must use $(MAKE) -C $(KERNEL_SRC) M=$(PWD) modules
7. The mymodule.c source in SRC_URI must include:
   - #include <linux/module.h> and #include <linux/init.h>
   - MODULE_LICENSE("GPL") — required, missing it taints the kernel
   - module_init() and module_exit() macros
8. Do NOT write custom do_compile() — the module class handles this via KERNEL_SRC

IMPORTANT: "inherit module" is required for out-of-tree kernel modules. The
Makefile MUST use $(KERNEL_SRC) (the Yocto variable), not a hardcoded kernel
path. MODULE_LICENSE("GPL") in the C source is mandatory — the kernel will log
a "tainted kernel" warning without it.

Output ONLY the complete .bb recipe file content (not the C source or Makefile).
