Write a Zephyr RTOS BLE peripheral application with a custom GATT service.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/gatt.h, zephyr/bluetooth/uuid.h
2. Define a custom 128-bit service UUID
3. Define a custom 128-bit characteristic UUID
4. Create a static uint8_t variable to hold the characteristic value
5. Implement a read callback (bt_gatt_attr_read) that returns the current value
6. Implement a write callback that updates the value and prints the new value
7. Register the GATT service using BT_GATT_SERVICE_DEFINE with:
   - Primary service attribute
   - One characteristic with READ and WRITE permissions
8. Define advertising data with the device name and service UUID
9. In main():
   - Call bt_enable(NULL) and check return value
   - Start advertising with bt_le_adv_start() using BT_LE_ADV_CONN
   - Print "Advertising started"
   - Sleep forever with k_sleep(K_FOREVER)

Output ONLY the complete C source file.
