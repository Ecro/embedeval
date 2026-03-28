Write a Zephyr RTOS application that uses a watchdog timer to detect and recover from main loop stalls.

Requirements:
1. Obtain the watchdog device from the devicetree
2. Verify the device is ready before use
3. Configure a watchdog timeout that resets the system if the main loop stops responding
4. The watchdog should survive debug halt scenarios (not trigger during debugging)
5. In the main loop, periodically service the watchdog and print a heartbeat message
6. Choose appropriate timeout and feed intervals for a typical embedded system

Output ONLY the complete C source file.
