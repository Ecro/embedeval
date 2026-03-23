SUMMARY = "Custom embedded Linux image"
DESCRIPTION = "Minimal embedded image with SSH and development tools"

inherit core-image

IMAGE_FEATURES += "ssh-server-openssh debug-tweaks"

IMAGE_INSTALL += " \
    packagegroup-core-boot \
    busybox \
    openssh \
    openssh-sftp-server \
    "

IMAGE_ROOTFS_SIZE ?= "65536"
