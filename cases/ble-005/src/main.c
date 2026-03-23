#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gap.h>

static void passkey_display(struct bt_conn *conn, unsigned int passkey)
{
	printk("Passkey: %06u\n", passkey);
}

static void passkey_confirm(struct bt_conn *conn, unsigned int passkey)
{
	printk("Confirm passkey: %06u\n", passkey);
	bt_conn_auth_passkey_confirm(conn);
}

static void cancel(struct bt_conn *conn)
{
	printk("Pairing cancelled\n");
}

static void pairing_complete(struct bt_conn *conn, bool bonded)
{
	printk("Pairing complete, bonded=%d\n", bonded);
}

static void pairing_failed(struct bt_conn *conn, enum bt_security_err reason)
{
	printk("Pairing failed: reason=%d\n", reason);
}

static const struct bt_conn_auth_cb auth_callbacks = {
	.passkey_display = passkey_display,
	.passkey_confirm = passkey_confirm,
	.cancel          = cancel,
};

static const struct bt_conn_auth_info_cb auth_info_callbacks = {
	.pairing_complete = pairing_complete,
	.pairing_failed   = pairing_failed,
};

static void connected(struct bt_conn *conn, uint8_t err)
{
	int ret;

	if (err) {
		printk("Connection failed: %d\n", err);
		return;
	}

	printk("Connected, requesting security level 3\n");

	ret = bt_conn_set_security(conn, BT_SECURITY_L3);
	if (ret) {
		printk("Failed to set security: %d\n", ret);
	}
}

static void disconnected(struct bt_conn *conn, uint8_t reason)
{
	printk("Disconnected (reason %d)\n", reason);
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
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

	err = bt_conn_auth_cb_register(&auth_callbacks);
	if (err) {
		printk("Failed to register auth callbacks: %d\n", err);
		return err;
	}

	err = bt_conn_auth_info_cb_register(&auth_info_callbacks);
	if (err) {
		printk("Failed to register auth info callbacks: %d\n", err);
		return err;
	}

	err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), NULL, 0);
	if (err) {
		printk("Advertising failed: %d\n", err);
		return err;
	}

	printk("Advertising with security\n");
	k_sleep(K_FOREVER);
	return 0;
}
