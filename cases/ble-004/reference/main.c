#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>

static bool connected_flag;

static void connected(struct bt_conn *conn, uint8_t err)
{
	char addr[BT_ADDR_LE_STR_LEN];
	struct bt_conn_info info;

	if (err) {
		printk("Connection failed: %d\n", err);
		return;
	}

	bt_conn_get_info(conn, &info);
	bt_addr_le_to_str(info.le.dst, addr, sizeof(addr));
	printk("Connected to: %s\n", addr);
	connected_flag = true;
}

static void disconnected(struct bt_conn *conn, uint8_t reason)
{
	printk("Disconnected (reason %d)\n", reason);
	connected_flag = false;
}

static struct bt_conn_cb conn_callbacks = {
	.connected    = connected,
	.disconnected = disconnected,
};

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
};

int main(void)
{
	int err;

	err = bt_enable(NULL);
	if (err) {
		printk("Bluetooth init failed: %d\n", err);
		return err;
	}

	bt_conn_cb_register(&conn_callbacks);

	err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), NULL, 0);
	if (err) {
		printk("Advertising failed: %d\n", err);
		return err;
	}

	printk("Advertising\n");
	k_sleep(K_FOREVER);
	return 0;
}
