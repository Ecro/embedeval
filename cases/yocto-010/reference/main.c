SUMMARY = "Application with runtime ptest support"
DESCRIPTION = "Demonstrates Yocto ptest integration for target runtime testing"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=838c366f69b72c5df05c96dff79b35f2"

SRC_URI = "file://main.c \
           file://test_main.c \
           file://run-ptest \
           file://COPYING \
           "

S = "${WORKDIR}"

inherit ptest

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o myapp ${S}/main.c
}

do_compile_ptest() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o test_myapp ${S}/test_main.c
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 myapp ${D}${bindir}/myapp
}

do_install_ptest() {
    install -d ${D}${PTEST_PATH}
    install -m 0755 test_myapp ${D}${PTEST_PATH}/test_myapp
    install -m 0755 ${S}/run-ptest ${D}${PTEST_PATH}/run-ptest
}

RDEPENDS:${PN}-ptest += "bash"
