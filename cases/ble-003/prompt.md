Write a Zephyr RTOS BLE peripheral that sends notifications from a GATT characteristic.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/gatt.h, and zephyr/kernel.h
2. Define a 128-bit service UUID and a 128-bit characteristic UUID
3. Declare a static uint8_t sensor_value = 0 to hold the notifiable value
4. Declare a static struct bt_conn *current_conn = NULL to track the connection
5. Implement connection callbacks (struct bt_conn_cb) with connected and disconnected handlers:
   - connected: save connection reference with bt_conn_ref(), set current_conn
   - disconnected: clear current_conn, call bt_conn_unref()
6. Register the GATT service using BT_GATT_SERVICE_DEFINE with:
   - Primary service attribute
   - One characteristic with BT_GATT_CHRC_NOTIFY property and BT_GATT_PERM_NONE permissions
   - A Client Characteristic Configuration Descriptor (CCC) using BT_GATT_CCC macro
7. In main():
   - Call bt_enable(NULL) and check return value
   - Register connection callbacks with bt_conn_cb_register()
   - Start advertising with bt_le_adv_start() using BT_LE_ADV_CONN
   - In a loop, increment sensor_value every second and call bt_gatt_notify() if current_conn is non-NULL
   - Check bt_gatt_notify() return value

Output ONLY the complete C source file.
