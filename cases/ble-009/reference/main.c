#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/settings/settings.h>

static void bond_cb(const struct bt_bond_info *info, void *user_data)
{
	int *count = user_data;
	char addr_str[BT_ADDR_LE_STR_LEN];

	bt_addr_le_to_str(&info->addr, addr_str, sizeof(addr_str));
	printk("  Bond %d: %s\n", *count, addr_str);
	(*count)++;
}

static void remove_all_bonds(void)
{
	int err;

	err = bt_unpair(BT_ID_DEFAULT, NULL);
	if (err) {
		printk("Failed to remove bonds: %d\n", err);
	} else {
		printk("All bonds removed\n");
	}
}

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
};

int main(void)
{
	int err;
	int bond_count = 0;

	/* bt_enable must come before any bond operations */
	err = bt_enable(NULL);
	if (err) {
		printk("Bluetooth init failed: %d\n", err);
		return err;
	}

	/* Load persistent bonds from settings (flash) */
	err = settings_load();
	if (err) {
		printk("Settings load failed: %d\n", err);
		return err;
	}

	/* List current bonds */
	printk("Listing bonded devices:\n");
	bt_foreach_bond(BT_ID_DEFAULT, bond_cb, &bond_count);
	printk("Total bonds: %d\n", bond_count);

	/* Remove all bonds if there are any */
	if (bond_count > 0) {
		remove_all_bonds();
	}

	/* Start advertising to allow new connections and bonding */
	err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), NULL, 0);
	if (err) {
		printk("Advertising failed: %d\n", err);
		return err;
	}

	printk("BLE advertising started\n");
	k_sleep(K_FOREVER);
	return 0;
}
