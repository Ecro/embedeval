Write an ESP-IDF application that connects to a WiFi network in station (STA) mode.

Requirements:
1. Initialize NVS flash before WiFi initialization
2. Initialize the network interface with esp_netif_init and create a default STA netif
3. Initialize WiFi with esp_wifi_init and a default configuration
4. Register an event handler for both WIFI_EVENT and IP_EVENT events
5. Set WiFi mode to WIFI_MODE_STA
6. Configure SSID as "MyNetwork" and password as "MyPassword"
7. Call esp_wifi_start() and esp_wifi_connect()
8. In the event handler: reconnect on disconnect, print IP address on got-IP event

Use the ESP-IDF event loop (esp_event_handler_register).
Include proper headers.
Output ONLY the complete C source file.
