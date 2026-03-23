Write a Zephyr RTOS BLE application that registers connection and disconnection callbacks.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/conn.h, and zephyr/kernel.h
2. Declare a static bool connected_flag = false to track connection state
3. Implement a connected() callback:
   - Parameters: struct bt_conn *conn, uint8_t err
   - If err is non-zero, print error and return
   - Get the peer address with bt_conn_get_info() or bt_addr_le_to_str()
   - Print the peer address string
   - Set connected_flag = true
4. Implement a disconnected() callback:
   - Parameters: struct bt_conn *conn, uint8_t reason
   - Print the disconnect reason
   - Set connected_flag = false
5. Define a static struct bt_conn_cb conn_callbacks with .connected and .disconnected fields
6. In main():
   - Call bt_enable(NULL) and check return value
   - Register callbacks with bt_conn_cb_register(&conn_callbacks)
   - Start advertising with bt_le_adv_start() using BT_LE_ADV_CONN and simple ad data
   - Print "Advertising" and sleep forever with k_sleep(K_FOREVER)

Output ONLY the complete C source file.
