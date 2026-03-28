Write a Zephyr RTOS application that combines a hardware watchdog with a persistent reboot counter stored in NVS (Non-Volatile Storage).

Requirements:
1. On boot, read a reboot counter from NVS
2. If the counter exceeds a threshold (e.g., 3), enter a safe/recovery mode instead of normal operation
3. Increment and save the counter to NVS before starting normal operation
4. Set up a hardware watchdog with an appropriate timeout
5. In normal mode, periodically feed the watchdog from the main loop
6. After successful operation for a period (e.g., 30 seconds), reset the counter to 0 in NVS (proving stability)
7. Print the current reboot count and mode (normal vs recovery) on startup

This tests system-level reasoning: persistent state across reboots, escalating recovery, and watchdog integration.
