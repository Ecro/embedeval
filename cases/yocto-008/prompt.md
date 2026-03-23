Write a Yocto BitBake recipe (.bb file) for a package that is dual-licensed under MIT and GPL-2.0-only.

Requirements:
1. Set SUMMARY and DESCRIPTION
2. Set LICENSE using SPDX identifier format with & separator:
   LICENSE = "MIT & GPL-2.0-only"
3. Set LIC_FILES_CHKSUM with SEPARATE entries for each license file:
   - MIT license: point to COPYING.MIT with its md5 checksum
   - GPL license: point to COPYING.GPL with its md5 checksum
   Each entry must have its own "file://...;md5=..." clause
4. Set SRC_URI (use file:// or git://)
5. Set S = "${WORKDIR}" or appropriate path
6. Implement do_compile() using ${CC}
7. Implement do_install() using ${D}${bindir}

CRITICAL RULES:
- Use SPDX identifiers: "MIT" not "mit", "GPL-2.0-only" not "GPLv2" or "GPL-2.0"
- Use & separator between licenses: "MIT & GPL-2.0-only" NOT "MIT, GPL-2.0-only"
- LIC_FILES_CHKSUM MUST have a separate entry for EACH license file
- Each entry MUST have md5= or sha256= checksum — missing any one causes parse failure

Output ONLY the complete .bb recipe file content.
