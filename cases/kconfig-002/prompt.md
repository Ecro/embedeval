Write a Zephyr RTOS Kconfig fragment (.conf) that enables BLE Mesh networking with provisioning and relay support.

Requirements:
1. Enable the full Bluetooth stack needed for BLE Mesh operation
2. Enable Mesh relay functionality so this node can forward messages
3. Ensure all dependency layers are enabled (HCI, base BT stack, etc.)
4. Do NOT enable Friend and Low Power features together (they are mutually exclusive in Zephyr's Mesh stack)

Output ONLY the Kconfig fragment as a plain text .conf file content.
