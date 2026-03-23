SUMMARY = "Application with build-time and runtime dependencies"
DESCRIPTION = "Demonstrates correct use of DEPENDS and RDEPENDS in Yocto"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=838c366f69b72c5df05c96dff79b35f2"

SRC_URI = "file://myapp.c \
           file://COPYING \
           "

S = "${WORKDIR}"

DEPENDS = "libssl openssl"

RDEPENDS:${PN} = "libssl"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -lssl -lcrypto -o myapp ${S}/myapp.c
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 myapp ${D}${bindir}/myapp
}
