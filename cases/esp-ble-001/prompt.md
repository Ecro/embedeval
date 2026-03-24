Write an ESP-IDF application that creates a BLE server exposing a custom service.

Requirements:
1. Initialize non-volatile storage before enabling wireless subsystems
2. Bring up the Bluetooth controller and stack in the correct sequence
3. Register a custom service containing one characteristic that supports both reading and writing
4. Set up connection and disconnection notifications
5. Set the device name and begin advertising so clients can discover and connect to it
6. When a client writes to the characteristic, store the written value
7. When a client reads the characteristic, return the last stored value

Use the ESP-IDF Bluetooth API.
Output ONLY the complete C source file.
