Write an ESP-IDF application that updates its own firmware over the network.

Requirements:
1. Connect to WiFi (use hardcoded SSID "MyNetwork" and password "MyPassword")
2. Download new firmware from "https://example.com/firmware.bin"
3. After the download completes, verify the new firmware is valid before committing to it
4. If verification or the update process fails, revert to the previous firmware
5. If the update succeeds, restart the device to run the new firmware
6. Handle all errors (network, download, update) appropriately

Use the ESP-IDF over-the-air update mechanism.
Output ONLY the complete C source file.
