Write a Yocto machine configuration file (.conf fragment) for an ARM Cortex-A53 based board.

Requirements:
1. Set MACHINE_FEATURES to include at least:
   - "usbhost" for USB host support
   - "ethernet" for network
   - "ext2" for filesystem support
2. Set KERNEL_DEVICETREE to the device tree blob filename(s):
   - Must end with .dtb extension (e.g., "myboard.dtb")
   - Can list multiple separated by spaces
3. Set SERIAL_CONSOLES in the format "baudrate;device":
   - e.g., SERIAL_CONSOLES = "115200;ttyAMA0"
   - Use standard Linux serial device names (ttyAMA0, ttyS0, ttyUSB0, etc.)
4. Set DEFAULTTUNE or TUNE_FEATURES for ARM Cortex-A53 (e.g., "cortexa53")
5. Set KERNEL_IMAGETYPE to "Image" or "zImage" or "uImage"

IMPORTANT FORMAT RULES:
- KERNEL_DEVICETREE must end in .dtb (not .dts which is the source file)
- SERIAL_CONSOLES format is strictly "baudrate;device" with semicolon
- MACHINE_FEATURES is a space-separated list of feature strings

Output ONLY the complete machine .conf file content.
