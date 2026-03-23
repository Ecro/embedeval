Write a Zephyr RTOS BLE observer application that scans for nearby devices.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h and zephyr/kernel.h
2. Implement a scan callback function device_found() with signature:
   void device_found(const bt_addr_le_t *addr, int8_t rssi, uint8_t type,
                     struct net_buf_simple *ad)
   - Print the device address and RSSI using bt_addr_le_to_str() and printk()
3. Define scan parameters using struct bt_le_scan_param with:
   - type: BT_LE_SCAN_TYPE_PASSIVE
   - options: BT_LE_SCAN_OPT_NONE
   - interval: BT_GAP_SCAN_FAST_INTERVAL
   - window: BT_GAP_SCAN_FAST_WINDOW
4. In main():
   - Call bt_enable(NULL) and check return value
   - Call bt_le_scan_start() with the scan params and device_found callback
   - Check bt_le_scan_start() return value
   - Print "Scanning started" on success
   - Sleep forever with k_sleep(K_FOREVER)

Output ONLY the complete C source file.
