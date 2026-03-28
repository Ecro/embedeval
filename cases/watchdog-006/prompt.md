Write a Zephyr RTOS application that configures a watchdog with a pre-timeout callback that logs diagnostic information before the system resets.

Requirements:
1. Obtain the watchdog device from the devicetree and verify it is ready
2. Register a pre-timeout callback that executes just before the watchdog resets the system
3. The callback should log a warning message indicating an imminent reset
4. Configure the watchdog with an appropriate timeout period
5. The watchdog should not trigger during debug halts
6. In the main loop, feed the watchdog normally for several iterations, then deliberately stop feeding to trigger the pre-timeout callback and observe the behavior

Output ONLY the complete C source file.
