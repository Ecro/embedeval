#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>

#define BT_UUID_CUSTOM_SERVICE_VAL \
	BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef0)
#define BT_UUID_CUSTOM_CHRC_VAL \
	BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x5678, 0x1234, 0x56789abcdef1)

static struct bt_uuid_128 svc_uuid = BT_UUID_INIT_128(BT_UUID_CUSTOM_SERVICE_VAL);
static struct bt_uuid_128 chrc_uuid = BT_UUID_INIT_128(BT_UUID_CUSTOM_CHRC_VAL);

static uint8_t chrc_value;

static ssize_t read_chrc(struct bt_conn *conn,
			  const struct bt_gatt_attr *attr,
			  void *buf, uint16_t len, uint16_t offset)
{
	return bt_gatt_attr_read(conn, attr, buf, len, offset,
				 &chrc_value, sizeof(chrc_value));
}

static ssize_t write_chrc(struct bt_conn *conn,
			   const struct bt_gatt_attr *attr,
			   const void *buf, uint16_t len,
			   uint16_t offset, uint8_t flags)
{
	if (offset + len > sizeof(chrc_value)) {
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
	}

	memcpy(&chrc_value + offset, buf, len);
	printk("Value written: 0x%02x\n", chrc_value);
	return len;
}

BT_GATT_SERVICE_DEFINE(custom_svc,
	BT_GATT_PRIMARY_SERVICE(&svc_uuid),
	BT_GATT_CHARACTERISTIC(&chrc_uuid.uuid,
				BT_GATT_CHRC_READ | BT_GATT_CHRC_WRITE,
				BT_GATT_PERM_READ | BT_GATT_PERM_WRITE,
				read_chrc, write_chrc, &chrc_value),
);

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_CUSTOM_SERVICE_VAL),
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
	k_sleep(K_FOREVER);
	return 0;
}
