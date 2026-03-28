Write a Zephyr RTOS application that implements a persistent data logger storing sensor readings to NVS (Non-Volatile Storage).

Requirements:
1. Read a simulated sensor value periodically
2. Persist the readings to NVS so they survive reboots
3. Maintain a running sample count across reboots
4. The system must operate reliably for years without manual intervention
5. Handle the case where NVS storage becomes full
6. Print the current sample count and latest reading on each cycle

Provide the complete main.c implementation.
