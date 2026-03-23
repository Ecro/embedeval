Write a Zephyr RTOS MQTT client that configures a Last Will and Testament (LWT) message.

Requirements:
1. Include zephyr/net/mqtt.h, zephyr/net/socket.h, and zephyr/kernel.h
2. Define broker address "192.168.1.100" and port 1883
3. Define a will topic "devices/zephyr/status" and will message "offline"
4. Define a static struct mqtt_client
5. Implement an MQTT event handler that handles MQTT_EVT_CONNACK and MQTT_EVT_DISCONNECT
6. Initialize the MQTT client with mqtt_client_init()
7. Configure the will message BEFORE calling mqtt_connect():
   - Set client.will_topic.utf8 to the will topic string
   - Set client.will_topic.size to the topic length
   - Set client.will_message.payload.data to the will message
   - Set client.will_message.payload.len to the message length
   - Set client.will_message.topic.qos to MQTT_QOS_1_AT_LEAST_ONCE
8. Set client.will_retain = 1 (or true)
9. Set the client ID to "zephyr_lwt_client"
10. Call mqtt_connect() and check return value
11. In main loop, call mqtt_input() and mqtt_live()
12. Do NOT use mosquitto_will_set() or any mosquitto_* API — those are not Zephyr

Output ONLY the complete C source file.
