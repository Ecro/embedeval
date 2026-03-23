SUMMARY = "Out-of-tree kernel module recipe"
DESCRIPTION = "BitBake recipe for building a Linux kernel module out-of-tree"
LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://COPYING;md5=b234ee4d69f5fce4486a80fdaf4a4263"

SRC_URI = "file://mymodule.c \
           file://Makefile \
           file://COPYING \
           "

S = "${WORKDIR}"

inherit module

KERNEL_MODULE_AUTOLOAD += "mymodule"
