Write a Zephyr RTOS BLE GATT service for secure firmware update (OTA DFU) with authentication.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/gatt.h, zephyr/bluetooth/conn.h,
   zephyr/bluetooth/uuid.h, and zephyr/kernel.h
2. Define a custom 128-bit UUID for the DFU service and a characteristic UUID
3. Track DFU state with a static bool: is_authenticated = false
4. Implement a GATT write handler for the DFU data characteristic:
   - Check is_authenticated before accepting firmware data
   - If not authenticated, return BT_GATT_ERR(BT_ATT_ERR_AUTHORIZATION)
   - If authenticated, copy data to a static firmware_buf[1024]
   - Print "DFU data received: N bytes"
5. Implement a GATT write handler for an authentication characteristic:
   - Accept a 4-byte PIN value
   - If PIN matches 0xDEADBEEF, set is_authenticated = true and return len
   - Otherwise return BT_GATT_ERR(BT_ATT_ERR_AUTHORIZATION)
6. Register the GATT service using BT_GATT_SERVICE_DEFINE with both characteristics
7. In the connected callback, call bt_conn_set_security() with BT_SECURITY_L2 or higher
8. After receiving all firmware data, validate the image before confirming:
   - Check firmware_buf[0] is not 0xFF (blank/erased flash guard)
   - Print "Image validation passed" or "Image validation failed"
9. Do NOT use ble_dfu_start(), ota_update(), or mcuboot_confirm() directly
10. Call bt_enable(NULL) and bt_le_adv_start() in main

Output ONLY the complete C source file.
