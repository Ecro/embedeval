Write a Zephyr RTOS MQTT client that connects to a broker and publishes a message.

Requirements:
1. Include zephyr/net/mqtt.h, zephyr/net/socket.h, zephyr/kernel.h
2. Define broker address as "192.168.1.100" and port 1883
3. Define a static mqtt_client struct
4. Implement an MQTT event handler function that handles:
   - MQTT_EVT_CONNACK: print "Connected" and set a connected flag
   - MQTT_EVT_PUBACK: print "Published"
   - MQTT_EVT_DISCONNECT: print "Disconnected" and clear connected flag
5. Initialize the MQTT client with mqtt_client_init()
6. Configure broker connection parameters (broker addr, client id)
7. Set the client ID to "zephyr_client"
8. Call mqtt_connect() and check return value
9. In main loop, call mqtt_input() and mqtt_live() for protocol handling
10. After connection, publish a message to topic "test/topic" with QoS 1
11. Use mqtt_publish() with a struct mqtt_publish_param
12. Handle errors at each step

Output ONLY the complete C source file.
