Write an ESP-IDF application that puts the chip into its lowest-power sleep state and wakes it on a button press.

Requirements:
1. Configure GPIO 0 as a wakeup source that triggers on a low signal level
2. On startup, check whether the device is waking from sleep or booting fresh, and print the reason
3. On first boot, perform initialization work (print a startup message)
4. Wait 5 seconds, then enter the lowest-power sleep mode available
5. Ensure the GPIO pull configuration is appropriate for detecting a low-level signal

Use the ESP-IDF power management and sleep APIs.
Output ONLY the complete C source file.
