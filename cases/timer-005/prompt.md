Write a Zephyr RTOS application that coordinates three kernel timers running at different rates, all updating shared state safely using atomic operations.

Requirements:
1. Define three global atomic variables: fast_count, mid_count, slow_count, initialized to 0
2. Define three timers using K_TIMER_DEFINE: fast_timer (100ms), mid_timer (250ms), slow_timer (1000ms)
3. Each timer's expiry function increments its corresponding atomic variable using atomic_inc()
4. In main(), start all three timers with their respective periods (first expiry same as period)
5. In a loop, every 2 seconds print all three counter values using printk and atomic_get()
6. Loop 5 times then return

Use the Zephyr kernel API: K_TIMER_DEFINE, k_timer_start, atomic_inc, atomic_get, K_MSEC, K_SECONDS.
Use atomic_t for the counter type.

Include proper header: zephyr/kernel.h.

Output ONLY the complete C source file.
