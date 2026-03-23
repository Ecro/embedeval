Write a Yocto BitBake recipe (.bb file) for a project that uses CMake as its build system.

Requirements:
1. Set SUMMARY to a short description
2. Set LICENSE to "MIT"
3. Set LIC_FILES_CHKSUM pointing to a COPYING file with md5sum
4. Set SRC_URI to a git:// repository URL with protocol=https
5. Set SRCREV to a specific git commit hash (use a placeholder like "abc123...")
6. Set S to "${WORKDIR}/git" (standard for git fetched sources)
7. Use "inherit cmake" to activate the cmake class (do NOT write do_compile manually)
8. Optionally set EXTRA_OECMAKE if any cmake options are needed (e.g., -DBUILD_TESTS=OFF)
9. Implement do_install() that:
   - Creates the destination directory with install -d ${D}${bindir}
   - Installs the binary with install -m 0755

IMPORTANT: You MUST use "inherit cmake" — do NOT write custom do_compile() with
cmake commands. The cmake class already handles configure/compile. Missing
SRCREV when using git:// is an error. Never hardcode /usr/bin — use ${bindir}.

Output ONLY the complete .bb recipe file content.
