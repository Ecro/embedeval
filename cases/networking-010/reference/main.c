#include <zephyr/kernel.h>
#include <zephyr/net/net_mgmt.h>
#include <zephyr/net/net_if.h>

static struct net_mgmt_event_callback net_cb;

static void net_event_handler(struct net_mgmt_event_callback *cb,
			       uint32_t mgmt_event,
			       struct net_if *iface)
{
	if (mgmt_event == NET_EVENT_IF_UP) {
		printk("Interface UP\n");
	} else if (mgmt_event == NET_EVENT_IF_DOWN) {
		printk("Interface DOWN\n");
	}
}

int main(void)
{
	struct net_if *iface;

	/* Register callback BEFORE checking initial state */
	net_mgmt_init_event_callback(&net_cb, net_event_handler,
				     NET_EVENT_IF_UP | NET_EVENT_IF_DOWN);
	net_mgmt_add_event_callback(&net_cb);

	/* Check initial interface state */
	iface = net_if_get_default();
	if (iface == NULL) {
		printk("No default interface found\n");
		return -1;
	}

	if (net_if_is_up(iface)) {
		printk("Interface is currently UP\n");
	} else {
		printk("Interface is currently DOWN\n");
	}

	while (1) {
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
