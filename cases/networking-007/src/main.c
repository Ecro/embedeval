#include <zephyr/kernel.h>
#include <zephyr/net/dns_resolve.h>
#include <zephyr/net/socket.h>
#include <string.h>

#define HOSTNAME    "example.com"
#define DNS_TIMEOUT 3000

static K_SEM_DEFINE(dns_sem, 0, 1);

static void dns_result_cb(enum dns_resolve_status status,
			  struct dns_addrinfo *info,
			  void *user_data)
{
	if (status == DNS_EAI_NONAME) {
		printk("DNS: hostname not found (NXDOMAIN)\n");
		k_sem_give(&dns_sem);
		return;
	}

	if (status == DNS_EAI_ALLDONE) {
		printk("DNS: query complete\n");
		k_sem_give(&dns_sem);
		return;
	}

	if (status != 0) {
		printk("DNS: resolve error %d\n", status);
		k_sem_give(&dns_sem);
		return;
	}

	if (info == NULL) {
		return;
	}

	if (info->ai_family == AF_INET) {
		struct sockaddr_in *addr =
			(struct sockaddr_in *)&info->ai_addr;
		uint8_t *ip = (uint8_t *)&addr->sin_addr;

		printk("DNS resolved: %s -> %d.%d.%d.%d\n",
		       HOSTNAME, ip[0], ip[1], ip[2], ip[3]);
	}
}

int main(void)
{
	struct dns_resolve_context *ctx;
	uint16_t dns_id;
	int ret;

	ctx = dns_get_default_context();
	if (ctx == NULL) {
		printk("Failed to get DNS context\n");
		return -1;
	}

	ret = dns_resolve_name(ctx, HOSTNAME, DNS_QUERY_TYPE_A,
			       &dns_id, dns_result_cb, NULL,
			       K_MSEC(DNS_TIMEOUT));
	if (ret < 0) {
		printk("DNS resolve_name failed: %d\n", ret);
		return ret;
	}

	printk("DNS query submitted for %s (id=%u, timeout=%d ms)\n",
	       HOSTNAME, dns_id, DNS_TIMEOUT);

	ret = k_sem_take(&dns_sem, K_MSEC(DNS_TIMEOUT + 500));
	if (ret < 0) {
		printk("DNS timed out waiting for result\n");
		return ret;
	}

	return 0;
}
