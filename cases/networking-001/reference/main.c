#include <zephyr/kernel.h>
#include <zephyr/net/mqtt.h>
#include <zephyr/net/socket.h>
#include <string.h>

static struct mqtt_client client;
static struct sockaddr_in broker;
static uint8_t rx_buffer[256];
static uint8_t tx_buffer[256];
static bool connected;

static void mqtt_evt_handler(struct mqtt_client *const c,
			      const struct mqtt_evt *evt)
{
	switch (evt->type) {
	case MQTT_EVT_CONNACK:
		if (evt->result == 0) {
			printk("MQTT connected\n");
			connected = true;
		}
		break;
	case MQTT_EVT_PUBACK:
		printk("MQTT published\n");
		break;
	case MQTT_EVT_DISCONNECT:
		printk("MQTT disconnected\n");
		connected = false;
		break;
	default:
		break;
	}
}

static int publish(struct mqtt_client *c, const char *topic,
		   const char *payload)
{
	struct mqtt_publish_param param = {
		.message.topic.qos = MQTT_QOS_1_AT_LEAST_ONCE,
		.message.topic.topic.utf8 = (uint8_t *)topic,
		.message.topic.topic.size = strlen(topic),
		.message.payload.data = (uint8_t *)payload,
		.message.payload.len = strlen(payload),
		.message_id = 1,
		.dup_flag = 0,
		.retain_flag = 0,
	};

	return mqtt_publish(c, &param);
}

int main(void)
{
	int ret;

	mqtt_client_init(&client);

	broker.sin_family = AF_INET;
	broker.sin_port = htons(1883);
	net_addr_pton(AF_INET, "192.168.1.100", &broker.sin_addr);

	client.broker = (struct sockaddr *)&broker;
	client.evt_cb = mqtt_evt_handler;
	client.client_id.utf8 = (uint8_t *)"zephyr_client";
	client.client_id.size = strlen("zephyr_client");
	client.rx_buf = rx_buffer;
	client.rx_buf_size = sizeof(rx_buffer);
	client.tx_buf = tx_buffer;
	client.tx_buf_size = sizeof(tx_buffer);

	ret = mqtt_connect(&client);
	if (ret < 0) {
		printk("MQTT connect failed: %d\n", ret);
		return ret;
	}

	while (1) {
		ret = mqtt_input(&client);
		if (ret < 0) {
			printk("MQTT input error: %d\n", ret);
			break;
		}

		mqtt_live(&client);

		if (connected) {
			ret = publish(&client, "test/topic", "hello");
			if (ret < 0) {
				printk("Publish failed: %d\n", ret);
			}
			connected = false;
		}

		k_sleep(K_MSEC(500));
	}

	mqtt_disconnect(&client);
	return 0;
}
