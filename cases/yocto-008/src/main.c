SUMMARY = "Dual-licensed utility application"
DESCRIPTION = "Application licensed under both MIT and GPL-2.0-only"

LICENSE = "MIT & GPL-2.0-only"
LIC_FILES_CHKSUM = "file://COPYING.MIT;md5=838c366f69b72c5df05c96dff79b35f2 \
                    file://COPYING.GPL;md5=b234ee4d69f5fce4486a80fdaf4a4263"

SRC_URI = "file://main.c \
           file://COPYING.MIT \
           file://COPYING.GPL \
           "

S = "${WORKDIR}"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} -o myutil ${S}/main.c
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 myutil ${D}${bindir}/myutil
}
