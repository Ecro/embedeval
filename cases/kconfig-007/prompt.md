Write a Zephyr Kconfig fragment that enables both WiFi and Bluetooth Low Energy (BLE) with coexistence management.

Requirements:
1. Enable CONFIG_WIFI=y (WiFi driver stack)
2. Enable CONFIG_NET_L2_WIFI_MGMT=y (WiFi management layer, depends on WIFI)
3. Enable CONFIG_NETWORKING=y (required base networking stack)
4. Enable CONFIG_BT=y (Bluetooth subsystem)
5. Enable CONFIG_BT_COEX=y (Bluetooth/WiFi coexistence manager)
6. Do NOT enable CONFIG_WIFI_BLE_COEX=y
7. Do NOT enable CONFIG_NET_L2_WIFI_MGMT without CONFIG_WIFI=y

Output ONLY the Kconfig fragment as a plain text .conf file content.
