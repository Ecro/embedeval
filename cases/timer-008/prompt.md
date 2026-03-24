Write a Zephyr RTOS application that uses hardware cycle counting for high-resolution timing measurements.

Requirements:
1. In a loop, perform the following measurement steps:
   a. Record start cycles with: uint32_t start = k_cycle_get_32()
   b. Perform a short dummy operation to simulate work (e.g., a small busy loop of 100 iterations)
   c. Record end cycles with: uint32_t end = k_cycle_get_32()
   d. Calculate elapsed cycles: uint32_t elapsed_cycles = end - start
   e. Convert to nanoseconds: uint64_t elapsed_ns = k_cyc_to_ns_floor64(elapsed_cycles)
   f. Print both values: printk("Cycles: %u, NS: %llu\n", elapsed_cycles, elapsed_ns)
2. Sleep 1 second between measurements with k_sleep(K_SECONDS(1))
3. Repeat 10 times (loop bound), then exit

Use ONLY Zephyr timing APIs: k_cycle_get_32(), k_cyc_to_ns_floor64().
Do NOT use clock_gettime() (Linux/POSIX), micros() (Arduino), HAL_GetTick() (STM32), or gettimeofday().

Include header: zephyr/kernel.h only.

Output ONLY the complete C source file.
