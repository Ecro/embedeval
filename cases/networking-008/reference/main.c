#include <zephyr/kernel.h>
#include <zephyr/net/mqtt.h>
#include <zephyr/net/socket.h>
#include <string.h>

#define BROKER_ADDR    "192.168.1.100"
#define BROKER_PORT    1883
#define CLIENT_ID      "zephyr_lwt_client"
#define WILL_TOPIC     "devices/zephyr/status"
#define WILL_MESSAGE   "offline"

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
			printk("MQTT connected with LWT configured\n");
			connected = true;
		}
		break;
	case MQTT_EVT_DISCONNECT:
		printk("MQTT disconnected\n");
		connected = false;
		break;
	default:
		break;
	}
}

int main(void)
{
	int ret;

	mqtt_client_init(&client);

	broker.sin_family = AF_INET;
	broker.sin_port = htons(BROKER_PORT);
	net_addr_pton(AF_INET, BROKER_ADDR, &broker.sin_addr);

	client.broker = (struct sockaddr *)&broker;
	client.evt_cb = mqtt_evt_handler;
	client.client_id.utf8 = (uint8_t *)CLIENT_ID;
	client.client_id.size = strlen(CLIENT_ID);
	client.rx_buf = rx_buffer;
	client.rx_buf_size = sizeof(rx_buffer);
	client.tx_buf = tx_buffer;
	client.tx_buf_size = sizeof(tx_buffer);

	/* Configure Last Will and Testament BEFORE connecting */
	client.will_topic.utf8 = (uint8_t *)WILL_TOPIC;
	client.will_topic.size = strlen(WILL_TOPIC);
	client.will_message.payload.data = (uint8_t *)WILL_MESSAGE;
	client.will_message.payload.len = strlen(WILL_MESSAGE);
	client.will_message.topic.qos = MQTT_QOS_1_AT_LEAST_ONCE;
	client.will_retain = 1;

	ret = mqtt_connect(&client);
	if (ret < 0) {
		printk("MQTT connect failed: %d\n", ret);
		return ret;
	}

	printk("MQTT connecting with LWT topic=%s\n", WILL_TOPIC);

	while (1) {
		ret = mqtt_input(&client);
		if (ret < 0) {
			printk("MQTT input error: %d\n", ret);
			break;
		}

		mqtt_live(&client);
		k_sleep(K_MSEC(500));
	}

	mqtt_disconnect(&client);
	return 0;
}
