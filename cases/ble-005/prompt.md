Write a Zephyr RTOS BLE peripheral application with secure pairing using MITM protection.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/conn.h, zephyr/bluetooth/gap.h, and zephyr/kernel.h
2. Implement the following auth callback functions:
   - passkey_display(struct bt_conn *conn, unsigned int passkey): print the 6-digit passkey with printk()
   - passkey_confirm(struct bt_conn *conn, unsigned int passkey): call bt_conn_auth_passkey_confirm(conn)
   - cancel(struct bt_conn *conn): print "Pairing cancelled"
   - pairing_complete(struct bt_conn *conn, bool bonded): print "Pairing complete, bonded=%d"
   - pairing_failed(struct bt_conn *conn, enum bt_security_err reason): print "Pairing failed: reason=%d"
3. Define a static const struct bt_conn_auth_cb auth_callbacks with all above callbacks assigned
4. Define a static const struct bt_conn_auth_info_cb auth_info_callbacks with pairing_complete and pairing_failed
5. In main():
   - Call bt_enable(NULL) and check return value
   - Register auth callbacks with bt_conn_auth_cb_register(&auth_callbacks) BEFORE advertising
   - Register info callbacks with bt_conn_auth_info_cb_register(&auth_info_callbacks)
   - Start advertising with bt_le_adv_start() using BT_LE_ADV_CONN
   - In the connected callback (registered with BT_CONN_CB_DEFINE):
     - Call bt_conn_set_security(conn, BT_SECURITY_L3) to require MITM protection
6. Check all return values

Output ONLY the complete C source file.
