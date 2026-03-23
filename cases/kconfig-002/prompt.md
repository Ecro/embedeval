Write a Zephyr Kconfig fragment that enables BLE Mesh with relay support. The fragment should:
1. Enable CONFIG_BT=y (Bluetooth base stack)
2. Enable CONFIG_BT_HCI=y (required by BT)
3. Enable CONFIG_BT_MESH=y (depends on BT)
4. Enable CONFIG_BT_MESH_RELAY=y (relay feature for mesh)
5. NOT enable CONFIG_BT_MESH_FRIEND and CONFIG_BT_MESH_LOW_POWER together (they are mutually exclusive)

Output ONLY the Kconfig fragment as a plain text .conf file content.
