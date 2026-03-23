Write a Zephyr RTOS BLE application that manages bonded devices.

Requirements:
1. Include zephyr/bluetooth/bluetooth.h, zephyr/bluetooth/conn.h,
   zephyr/settings/settings.h, and zephyr/kernel.h
2. Implement a bond listing callback for bt_foreach_bond:
   static void bond_cb(const struct bt_bond_info *info, void *user_data)
   - Increment a bond count in user_data
   - Print each bonded device address
3. Call bt_enable(NULL) first — bonds cannot be accessed without it
4. After bt_enable, call settings_load() to restore persistent bonds from flash
5. Call bt_foreach_bond(BT_ID_DEFAULT, bond_cb, &bond_count) to list bonds
6. Print the total number of bonds found
7. Implement a function remove_all_bonds() that calls bt_unpair(BT_ID_DEFAULT, NULL)
   to remove all bonds for the default identity
8. In main, list bonds first, then offer to remove all bonds
9. Call bt_le_adv_start() after bond management to allow new connections
10. Handle errors at each step with printk and return

Output ONLY the complete C source file.
