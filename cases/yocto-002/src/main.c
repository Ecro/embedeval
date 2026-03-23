SUMMARY = "CMake-based application built with Yocto cmake class"
DESCRIPTION = "Example project demonstrating cmake class inheritance in Yocto"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=838c366f69b72c5df05c96dff79b35f2"

SRC_URI = "git://github.com/example/myapp.git;protocol=https;branch=main"

SRCREV = "abc123def456abc123def456abc123def456abc1"

S = "${WORKDIR}/git"

inherit cmake

EXTRA_OECMAKE = "-DBUILD_TESTS=OFF"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 ${B}/myapp ${D}${bindir}/myapp
}
