Write a Zephyr RTOS application that uses a kernel timer to increment a counter periodically.

Requirements:
1. Define a global counter variable that will be incremented from a timer callback, initialized to 0
2. Create a kernel timer using K_TIMER_DEFINE with an expiry function
3. The expiry function increments the counter by 1
4. In main(), start the timer with 500ms period (first expiry at 500ms, then every 500ms)
5. In a loop, print the counter value using printk every 2 seconds
6. Use k_sleep(K_SECONDS(2)) for the loop delay

Use the Zephyr kernel timer API: K_TIMER_DEFINE, k_timer_start, K_MSEC, K_SECONDS.

Include proper header: zephyr/kernel.h.

Output ONLY the complete C source file.
