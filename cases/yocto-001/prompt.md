Write a Yocto BitBake recipe (.bb file) for building and installing a simple C hello-world application.

Requirements:
1. Set SUMMARY to a short description
2. Set LICENSE to "MIT"
3. Set LIC_FILES_CHKSUM to point to a COPYING file with the correct md5sum format
4. Set SRC_URI to a local file:// source or git:// repository
5. Set S (source directory) to "${WORKDIR}" or appropriate path
6. Inherit the correct class (e.g., no special class needed for simple Makefile, or use cmake if CMakeLists.txt)
7. Implement do_compile() that compiles the C source with ${CC} and ${CFLAGS}/${LDFLAGS}
8. Implement do_install() that:
   - Creates the destination directory with install -d ${D}${bindir}
   - Installs the binary with install -m 0755
9. Use proper Yocto variable references: ${D}, ${bindir}, ${CC}, ${CFLAGS}, ${LDFLAGS}
10. Do NOT hardcode paths like /usr/bin — use ${bindir}

Output ONLY the complete .bb recipe file content.
