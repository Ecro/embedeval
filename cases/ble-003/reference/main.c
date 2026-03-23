#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gatt.h>

#define BT_UUID_SENSOR_SVC_VAL \
	BT_UUID_128_ENCODE(0xaabbccdd, 0x1234, 0x5678, 0x9abc, 0xdef012345678)
#define BT_UUID_SENSOR_CHRC_VAL \
	BT_UUID_128_ENCODE(0xaabbccdd, 0x1234, 0x5678, 0x9abc, 0xdef012345679)

static struct bt_uuid_128 svc_uuid = BT_UUID_INIT_128(BT_UUID_SENSOR_SVC_VAL);
static struct bt_uuid_128 chrc_uuid = BT_UUID_INIT_128(BT_UUID_SENSOR_CHRC_VAL);

static uint8_t sensor_value;
static struct bt_conn *current_conn;

static void ccc_changed(const struct bt_gatt_attr *attr, uint16_t value)
{
	bool notif_enabled = (value == BT_GATT_CCC_NOTIFY);

	printk("Notifications %s\n", notif_enabled ? "enabled" : "disabled");
}

BT_GATT_SERVICE_DEFINE(sensor_svc,
	BT_GATT_PRIMARY_SERVICE(&svc_uuid),
	BT_GATT_CHARACTERISTIC(&chrc_uuid.uuid,
				BT_GATT_CHRC_NOTIFY,
				BT_GATT_PERM_NONE,
				NULL, NULL, &sensor_value),
	BT_GATT_CCC(ccc_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
);

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_SENSOR_SVC_VAL),
};

static void connected(struct bt_conn *conn, uint8_t err)
{
	if (err) {
		printk("Connection failed: %d\n", err);
		return;
	}

	current_conn = bt_conn_ref(conn);
	printk("Connected\n");
}

static void disconnected(struct bt_conn *conn, uint8_t reason)
{
	printk("Disconnected (reason %d)\n", reason);
	bt_conn_unref(current_conn);
	current_conn = NULL;
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
	.connected    = connected,
	.disconnected = disconnected,
};

int main(void)
{
	int err;

	err = bt_enable(NULL);
	if (err) {
		printk("Bluetooth init failed: %d\n", err);
		return err;
	}

	err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), NULL, 0);
	if (err) {
		printk("Advertising failed: %d\n", err);
		return err;
	}

	printk("Advertising started\n");

	while (1) {
		k_sleep(K_SECONDS(1));
		sensor_value++;

		if (current_conn) {
			err = bt_gatt_notify(current_conn, &sensor_svc.attrs[2],
					     &sensor_value, sizeof(sensor_value));
			if (err) {
				printk("Notify failed: %d\n", err);
			}
		}
	}

	return 0;
}
