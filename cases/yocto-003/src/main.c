SUMMARY = "Application with systemd service integration"
DESCRIPTION = "Example app that installs and enables a systemd service unit"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=838c366f69b72c5df05c96dff79b35f2"

SRC_URI = "file://myapp.c \
           file://myapp.service \
           file://COPYING \
           "

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "myapp.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o myapp ${S}/myapp.c
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 myapp ${D}${bindir}/myapp

    install -d ${D}${systemd_unitdir}/system/
    install -m 0644 ${WORKDIR}/myapp.service ${D}${systemd_unitdir}/system/myapp.service
}

FILES:${PN} += "${systemd_unitdir}/system/myapp.service"
