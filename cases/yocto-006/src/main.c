SUMMARY = "Application with patch applied"
DESCRIPTION = "Demonstrates Yocto patch application via SRC_URI"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://COPYING;md5=b234ee4d69f5fce4486a80fdaf4a4263"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI = "git://github.com/example/myapp.git;branch=main;protocol=https \
           file://fix-build.patch \
           "

SRCREV = "abc1234def5678901234567890abcdef12345678"

S = "${WORKDIR}/git"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o myapp ${S}/main.c
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 myapp ${D}${bindir}/myapp
}
