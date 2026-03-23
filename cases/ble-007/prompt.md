Write a Zephyr RTOS BLE application that advertises with manufacturer-specific data.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h and zephyr/kernel.h
2. Define a company ID as two bytes: 0x59, 0x00 (Nordic Semiconductor)
3. Define manufacturer-specific payload bytes after the company ID (e.g., firmware version: 0x01, 0x00)
4. Build the advertising data (struct bt_data ad[]) with:
   - BT_DATA_BYTES(BT_DATA_FLAGS, ...) as the first entry
   - BT_DATA_BYTES(BT_DATA_MANUFACTURER_DATA, company_id_lsb, company_id_msb, payload...)
     as the second entry
5. The total advertising data payload must not exceed 31 bytes
6. Call bt_enable(NULL) in main and check the return value
7. Call bt_le_adv_start() with BT_LE_ADV_NCONN (non-connectable) for beacon-style advertising
8. Check the return value of bt_le_adv_start
9. Print "Advertising with manufacturer data" after successful start
10. Use k_sleep(K_FOREVER) to keep the application running

Output ONLY the complete C source file.
