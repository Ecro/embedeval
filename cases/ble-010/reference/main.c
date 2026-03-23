#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/l2cap.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/net/buf.h>
#include <string.h>

#define L2CAP_PSM 0x80

static struct bt_l2cap_le_chan l2cap_chan;

static int l2cap_recv(struct bt_l2cap_chan *chan, struct net_buf *buf)
{
	printk("L2CAP received %u bytes\n", buf->len);

	/* Echo the data back to the sender */
	struct net_buf *send_buf;

	send_buf = net_buf_alloc(&net_buf_pool_fixed_get, K_NO_WAIT);
	if (send_buf != NULL) {
		net_buf_add_mem(send_buf, buf->data, buf->len);
		int err = bt_l2cap_chan_send(chan, send_buf);

		if (err < 0) {
			printk("L2CAP send failed: %d\n", err);
			net_buf_unref(send_buf);
		}
	}

	return 0;
}

static void l2cap_chan_connected(struct bt_l2cap_chan *chan)
{
	printk("L2CAP channel connected\n");
}

static void l2cap_chan_disconnected(struct bt_l2cap_chan *chan)
{
	printk("L2CAP channel disconnected\n");
}

static struct bt_l2cap_chan_ops l2cap_ops = {
	.recv         = l2cap_recv,
	.connected    = l2cap_chan_connected,
	.disconnected = l2cap_chan_disconnected,
};

static int l2cap_server_accept(struct bt_conn *conn,
			        struct bt_l2cap_chan **chan)
{
	printk("L2CAP server: accepting new channel\n");

	l2cap_chan.chan.ops = &l2cap_ops;
	*chan = &l2cap_chan.chan;

	return 0;
}

static struct bt_l2cap_server l2cap_server = {
	.psm    = L2CAP_PSM,
	.accept = l2cap_server_accept,
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

	err = bt_l2cap_server_register(&l2cap_server);
	if (err) {
		printk("L2CAP server register failed: %d\n", err);
		return err;
	}

	printk("L2CAP server registered on PSM 0x%02x\n", L2CAP_PSM);

	err = bt_le_adv_start(BT_LE_ADV_CONN, ad, ARRAY_SIZE(ad), NULL, 0);
	if (err) {
		printk("Advertising failed: %d\n", err);
		return err;
	}

	printk("BLE L2CAP CoC server advertising\n");
	k_sleep(K_FOREVER);
	return 0;
}
