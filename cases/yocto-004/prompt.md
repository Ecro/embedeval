Write a Yocto BitBake recipe (.bb file) that correctly specifies build-time and runtime dependencies.

Requirements:
1. Set SUMMARY, LICENSE = "MIT", LIC_FILES_CHKSUM with md5sum
2. Set SRC_URI = "file://myapp.c" and S = "${WORKDIR}"
3. Set DEPENDS to list build-time (compile-time) libraries:
   - Include "libssl openssl" as build-time deps (link at compile time)
4. Set RDEPENDS:${PN} (with the :${PN} suffix!) to list runtime dependencies:
   - Include "libssl" as a runtime dep (needed at runtime on target)
5. Implement do_compile() using ${CC} ${CFLAGS} ${LDFLAGS} -lssl -lcrypto
6. Implement do_install() that installs the binary to ${D}${bindir}

IMPORTANT: Runtime dependencies MUST use RDEPENDS:${PN} with the package name
suffix. Using plain RDEPENDS (without :${PN}) is the old syntax and is ignored
in modern Yocto. DEPENDS is for build time only — libraries listed in DEPENDS
do not automatically appear on the target system.

Output ONLY the complete .bb recipe file content.
