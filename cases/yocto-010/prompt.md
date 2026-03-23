Write a Yocto BitBake recipe (.bb file) for an application that includes runtime tests using the ptest framework.

Requirements:
1. Set SUMMARY, LICENSE = "MIT", LIC_FILES_CHKSUM with md5 checksum
2. Set SRC_URI with source files
3. Inherit ptest class:
   inherit ptest
4. Implement do_compile_ptest() to build the test binaries:
   - Compile test executables with ${CC}
5. Implement do_install_ptest() to install tests to ${D}${PTEST_PATH}:
   - Create ${D}${PTEST_PATH} with install -d
   - Install test binaries with install -m 0755
   - Install a run-ptest script that executes the tests
6. Standard do_compile() and do_install() for the main application
7. RDEPENDS:${PN}-ptest should include "bash" if run-ptest is a shell script

CRITICAL: Do NOT use "make test" in do_install_ptest.
Yocto ptest works by installing a run-ptest script that is executed on the target device.
The test runner script (run-ptest) is what gets called — it should execute your test binaries.

Output ONLY the complete .bb recipe file content.
