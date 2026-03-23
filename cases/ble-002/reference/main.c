#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>

static void device_found(const bt_addr_le_t *addr, int8_t rssi, uint8_t type,
			 struct net_buf_simple *ad)
{
	char addr_str[BT_ADDR_LE_STR_LEN];

	bt_addr_le_to_str(addr, addr_str, sizeof(addr_str));
	printk("Device found: %s (RSSI %d)\n", addr_str, rssi);
}

int main(void)
{
	int err;
	struct bt_le_scan_param scan_param = {
		.type     = BT_LE_SCAN_TYPE_PASSIVE,
		.options  = BT_LE_SCAN_OPT_NONE,
		.interval = BT_GAP_SCAN_FAST_INTERVAL,
		.window   = BT_GAP_SCAN_FAST_WINDOW,
	};

	err = bt_enable(NULL);
	if (err) {
		printk("Bluetooth init failed: %d\n", err);
		return err;
	}

	err = bt_le_scan_start(&scan_param, device_found);
	if (err) {
		printk("Scanning failed to start: %d\n", err);
		return err;
	}

	printk("Scanning started\n");
	k_sleep(K_FOREVER);
	return 0;
}
