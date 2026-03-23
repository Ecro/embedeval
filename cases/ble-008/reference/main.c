#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>
#include <string.h>

#define TARGET_NAME "Zephyr Peripheral"

static struct bt_conn *default_conn;

static uint8_t discover_cb(struct bt_conn *conn,
			    const struct bt_gatt_attr *attr,
			    struct bt_gatt_discover_params *params)
{
	if (attr == NULL) {
		printk("GATT discovery complete\n");
		return BT_GATT_ITER_STOP;
	}

	printk("GATT service discovered at handle %u\n", attr->handle);
	return BT_GATT_ITER_CONTINUE;
}

static struct bt_gatt_discover_params discover_params = {
	.func  = discover_cb,
	.start_handle = BT_ATT_FIRST_ATTRIBUTE_HANDLE,
	.end_handle   = BT_ATT_LAST_ATTRIBUTE_HANDLE,
	.type  = BT_GATT_DISCOVER_PRIMARY,
};

static void connected(struct bt_conn *conn, uint8_t err)
{
	int ret;

	if (err) {
		printk("Connection failed: %d\n", err);
		bt_conn_unref(default_conn);
		default_conn = NULL;
		return;
	}

	printk("Connected to device\n");

	ret = bt_gatt_discover(conn, &discover_params);
	if (ret) {
		printk("GATT discover failed: %d\n", ret);
	}
}

static void disconnected(struct bt_conn *conn, uint8_t reason)
{
	printk("Disconnected (reason %d)\n", reason);

	if (default_conn == conn) {
		bt_conn_unref(default_conn);
		default_conn = NULL;
	}
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
	.connected    = connected,
	.disconnected = disconnected,
};

static bool parse_ad_name(struct bt_data *data, void *user_data)
{
	bool *found = user_data;

	if (data->type == BT_DATA_NAME_COMPLETE ||
	    data->type == BT_DATA_NAME_SHORTENED) {
		if (data->data_len == strlen(TARGET_NAME) &&
		    memcmp(data->data, TARGET_NAME, data->data_len) == 0) {
			*found = true;
			return false;
		}
	}

	return true;
}

static void scan_recv(const struct bt_le_scan_recv_info *info,
		      struct net_buf_simple *buf)
{
	bool found = false;
	int err;

	if (default_conn != NULL) {
		return;
	}

	bt_data_parse(buf, parse_ad_name, &found);

	if (!found) {
		return;
	}

	printk("Target device found, stopping scan and connecting\n");

	bt_le_scan_stop();

	err = bt_conn_le_create(info->addr, BT_CONN_LE_CREATE_CONN,
				BT_LE_CONN_PARAM_DEFAULT, &default_conn);
	if (err) {
		printk("bt_conn_le_create failed: %d\n", err);
		default_conn = NULL;
	}
}

static struct bt_le_scan_cb scan_callbacks = {
	.recv = scan_recv,
};

int main(void)
{
	int err;

	err = bt_enable(NULL);
	if (err) {
		printk("Bluetooth init failed: %d\n", err);
		return err;
	}

	bt_le_scan_cb_register(&scan_callbacks);

	err = bt_le_scan_start(BT_LE_SCAN_ACTIVE, NULL);
	if (err) {
		printk("Scanning failed: %d\n", err);
		return err;
	}

	printk("Scanning for \"%s\"\n", TARGET_NAME);
	k_sleep(K_FOREVER);
	return 0;
}
