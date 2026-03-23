Write a Zephyr RTOS application where a high-priority real-time thread measures its own execution time and verifies a 10ms deadline.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/util.h (or just kernel.h)
2. Define the thread with priority < 5 (e.g., priority 2) — lower number = higher priority
3. Implement do_work() — a function that does measurable work (e.g., a fixed computation loop with a counter, NOT k_sleep)
4. Implement rt_thread() that:
   - Records start time: uint32_t t0 = k_cycle_get_32();
   - Calls do_work()
   - Records end time: uint32_t t1 = k_cycle_get_32();
   - Computes elapsed cycles: uint32_t cycles = t1 - t0;
   - Converts to microseconds: uint32_t us = k_cyc_to_us_near32(cycles);
   - Checks deadline: if (us > 10000) { printk("DEADLINE MISSED: %u us\n", us); }
   - Else: printk("Work completed in %u us\n", us);
   - Repeats in a loop with k_sleep(K_MSEC(100)) between iterations
5. In main(): thread is started via K_THREAD_DEFINE, sleep forever

CRITICAL RULES:
- Thread priority MUST be < 5 (high priority)
- NO k_sleep inside do_work() or the timing window
- Use k_cycle_get_32() for timing, NOT k_uptime_get()
- Deadline is 10ms = 10000 microseconds
- Use k_cyc_to_us_near32() for cycle-to-microsecond conversion

Output ONLY the complete C source file.
