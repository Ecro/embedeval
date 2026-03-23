Write a Yocto BitBake recipe (.bb file) that builds a C application and applies a patch to the source.

Requirements:
1. Set SUMMARY, DESCRIPTION, LICENSE (use "GPL-2.0-only")
2. Set LIC_FILES_CHKSUM pointing to COPYING file with md5 checksum
3. Set FILESEXTRAPATHS to prepend a local files directory:
   FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
4. In SRC_URI:
   - Add a git:// or file:// source entry
   - Add the patch file: SRC_URI += "file://fix-build.patch"
5. Set S (source directory) appropriately
6. Implement do_compile() using ${CC} ${CFLAGS} ${LDFLAGS}
7. Implement do_install() that installs the binary to ${D}${bindir}

CRITICAL: Do NOT call "git apply" or "patch" manually in do_compile.
Yocto automatically applies patches listed in SRC_URI before do_compile runs.
The patch file must be listed in SRC_URI with the file:// scheme.

Output ONLY the complete .bb recipe file content.
