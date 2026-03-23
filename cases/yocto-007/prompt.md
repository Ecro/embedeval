Write a Yocto image recipe (.bb file) that creates a custom embedded Linux image.

Requirements:
1. Set SUMMARY and DESCRIPTION for the image
2. Inherit the correct image class:
   inherit core-image
3. Set IMAGE_FEATURES to include at least:
   - "ssh-server-openssh" for remote access
   - "debug-tweaks" for development
4. Set IMAGE_INSTALL using += to add packages:
   - Include at least: packagegroup-core-boot, busybox, openssh
   - Use IMAGE_INSTALL:append or IMAGE_INSTALL += syntax
5. Optionally set IMAGE_ROOTFS_SIZE to specify filesystem size in KB
6. Do NOT include a do_compile or do_install function (image recipes don't have these)

IMPORTANT:
- Use "inherit core-image" or "inherit image" (NOT inherit package)
- Use IMAGE_INSTALL += to add packages (not =, which would override)
- IMAGE_FEATURES must be set as a space-separated list

Output ONLY the complete .bb image recipe file content.
