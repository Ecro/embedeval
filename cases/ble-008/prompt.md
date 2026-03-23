Write a Zephyr RTOS BLE central application that scans for a device, connects, and discovers services.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/conn.h, zephyr/bluetooth/gatt.h,
   zephyr/bluetooth/uuid.h, and zephyr/kernel.h
2. Define a target device name to scan for: "Zephyr Peripheral"
3. Implement a scan callback (struct bt_le_scan_cb or bt_le_scan_recv_t):
   - Parse the advertising data to look for the target device name
   - When found, stop scanning with bt_le_scan_stop()
   - Initiate connection with bt_conn_le_create()
4. Declare a static struct bt_conn *default_conn = NULL
5. When bt_conn_le_create succeeds, store the connection reference
6. Implement a connected callback:
   - Print "Connected to device"
   - Start GATT service discovery with bt_gatt_discover()
7. Implement a disconnected callback:
   - Print "Disconnected"
   - Call bt_conn_unref() to release the connection reference
   - Set default_conn = NULL
8. Implement a GATT discovery callback that prints discovered service UUIDs
9. Register connection callbacks using BT_CONN_CB_DEFINE
10. Call bt_enable(NULL) then bt_le_scan_start() in main to begin scanning
11. Do NOT use BLEDevice.connect() — that is Python, not Zephyr C
12. Do NOT use gap_connect() — that function does not exist in Zephyr

Output ONLY the complete C source file.
