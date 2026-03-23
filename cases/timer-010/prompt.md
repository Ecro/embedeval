Write a Zephyr RTOS application that prints the system uptime every 2 seconds using k_uptime_get().

Requirements:
1. In an infinite while loop:
   a. Read the system uptime in milliseconds using k_uptime_get(), store in a int64_t variable
   b. Print the uptime with printk, e.g.: printk("Uptime: %lld ms\n", uptime)
   c. Sleep 2 seconds with k_sleep(K_SECONDS(2))
2. Use k_uptime_get() — do NOT define a custom counter variable or use k_cycle_get_32() for uptime

Include header: zephyr/kernel.h only.

Output ONLY the complete C source file.
