Write a Yocto BitBake recipe (.bb file) for an application that installs a systemd service unit file.

Requirements:
1. Set SUMMARY, LICENSE = "MIT", LIC_FILES_CHKSUM with md5sum
2. Set SRC_URI to include both the application source and the .service file:
   - file://myapp.c
   - file://myapp.service
3. Set S = "${WORKDIR}"
4. Use "inherit systemd" to activate systemd integration
5. Set SYSTEMD_SERVICE:${PN} = "myapp.service"
6. Set SYSTEMD_AUTO_ENABLE:${PN} = "enable" so the service starts at boot
7. Implement do_compile() using ${CC} ${CFLAGS} ${LDFLAGS}
8. Implement do_install():
   - install -d ${D}${bindir} and install the binary
   - install -d ${D}${systemd_unitdir}/system/ and install the .service file
9. Set FILES:${PN} to include ${systemd_unitdir}/system/myapp.service

IMPORTANT: "inherit systemd" is required — without it SYSTEMD_SERVICE has no
effect. The .service file must be in SRC_URI. SYSTEMD_AUTO_ENABLE must use the
:${PN} override syntax (new Yocto variable override format).

Output ONLY the complete .bb recipe file content.
