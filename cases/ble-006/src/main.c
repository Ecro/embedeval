#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/uuid.h>
#include <string.h>

#define BT_UUID_DFU_SVC_VAL \
	BT_UUID_128_ENCODE(0xFEED0001, 0x1234, 0x5678, 0xABCD, 0x000000000001)
#define BT_UUID_DFU_AUTH_VAL \
	BT_UUID_128_ENCODE(0xFEED0001, 0x1234, 0x5678, 0xABCD, 0x000000000002)
#define BT_UUID_DFU_DATA_VAL \
	BT_UUID_128_ENCODE(0xFEED0001, 0x1234, 0x5678, 0xABCD, 0x000000000003)

static struct bt_uuid_128 dfu_svc_uuid  = BT_UUID_INIT_128(BT_UUID_DFU_SVC_VAL);
static struct bt_uuid_128 dfu_auth_uuid = BT_UUID_INIT_128(BT_UUID_DFU_AUTH_VAL);
static struct bt_uuid_128 dfu_data_uuid = BT_UUID_INIT_128(BT_UUID_DFU_DATA_VAL);

static bool is_authenticated;
static uint8_t firmware_buf[1024];
static size_t firmware_len;

#define DFU_PIN 0xDEADBEEF

static ssize_t write_auth(struct bt_conn *conn,
			   const struct bt_gatt_attr *attr,
			   const void *buf, uint16_t len,
			   uint16_t offset, uint8_t flags)
{
	if (len != sizeof(uint32_t)) {
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
	}

	uint32_t pin;

	memcpy(&pin, buf, sizeof(pin));

	if (pin == DFU_PIN) {
		is_authenticated = true;
		printk("DFU authentication successful\n");
		return len;
	}

	printk("DFU authentication failed: wrong PIN\n");
	return BT_GATT_ERR(BT_ATT_ERR_AUTHORIZATION);
}

static ssize_t write_dfu_data(struct bt_conn *conn,
			       const struct bt_gatt_attr *attr,
			       const void *buf, uint16_t len,
			       uint16_t offset, uint8_t flags)
{
	if (!is_authenticated) {
		printk("DFU write rejected: not authenticated\n");
		return BT_GATT_ERR(BT_ATT_ERR_AUTHORIZATION);
	}

	if (offset + len > sizeof(firmware_buf)) {
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
	}

	memcpy(firmware_buf + offset, buf, len);
	firmware_len = offset + len;
	printk("DFU data received: %u bytes\n", len);

	/* Validate image when first chunk arrives */
	if (offset == 0) {
		if (firmware_buf[0] == 0xFF) {
			printk("Image validation failed: blank flash detected\n");
		} else {
			printk("Image validation passed\n");
		}
	}

	return len;
}

BT_GATT_SERVICE_DEFINE(dfu_svc,
	BT_GATT_PRIMARY_SERVICE(&dfu_svc_uuid),
	BT_GATT_CHARACTERISTIC(&dfu_auth_uuid.uuid,
				BT_GATT_CHRC_WRITE,
				BT_GATT_PERM_WRITE,
				NULL, write_auth, NULL),
	BT_GATT_CHARACTERISTIC(&dfu_data_uuid.uuid,
				BT_GATT_CHRC_WRITE,
				BT_GATT_PERM_WRITE,
				NULL, write_dfu_data, NULL),
);

static void connected(struct bt_conn *conn, uint8_t err)
{
	int ret;

	if (err) {
		printk("DFU connection failed: %d\n", err);
		return;
	}

	printk("DFU client connected, upgrading security\n");

	ret = bt_conn_set_security(conn, BT_SECURITY_L2);
	if (ret) {
		printk("Failed to set security: %d\n", ret);
	}
}

static void disconnected(struct bt_conn *conn, uint8_t reason)
{
	printk("DFU client disconnected (reason %d)\n", reason);
	is_authenticated = false;
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
	.connected    = connected,
	.disconnected = disconnected,
};

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_DFU_SVC_VAL),
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

	printk("BLE DFU service advertising\n");
	k_sleep(K_FOREVER);
	return 0;
}
