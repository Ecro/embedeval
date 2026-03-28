Write a Zephyr RTOS application that demonstrates CPU yielding with a timed sleep, printing wall-clock timestamps before and after to show elapsed time.

Requirements:
1. Include the necessary Zephyr kernel header
2. In main():
   - Read and print the current system uptime in milliseconds before sleeping
   - Sleep for 1000ms using a proper kernel sleep call (not a busy-wait loop)
   - Read and print the current system uptime in milliseconds after sleeping
   - Compute and print the elapsed time from two separate uptime readings
   - Correctly compute elapsed time, accounting for timer wrap-around on 32-bit platforms
   - Return 0
3. Use the Zephyr kernel timing API for uptime — do NOT use a custom counter or loop variable
4. The elapsed time must be derived from two separate uptime calls, not assumed from the sleep duration

Output ONLY the complete C source file.
