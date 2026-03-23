Write a Zephyr RTOS application demonstrating CPU yielding with k_sleep.

Requirements:
1. Include zephyr/kernel.h
2. In main():
   - Print "Before sleep: uptime=X ms" using printk, where X is obtained from k_uptime_get()
   - Sleep for 1000ms using k_sleep(K_MSEC(1000))
   - Print "After sleep: uptime=X ms" using printk, where X is obtained from k_uptime_get() again
   - Print "Elapsed: X ms" using printk showing the difference between the two uptime values
   - Return 0

Use k_sleep(K_MSEC(1000)) for sleeping — do NOT use a busy-wait loop or k_busy_wait().
Use k_uptime_get() to read timestamps — do NOT use a custom counter or loop variable.
The elapsed time printed must be derived from two separate k_uptime_get() calls.

Use the Zephyr API: k_sleep, K_MSEC, k_uptime_get.

Output ONLY the complete C source file.
