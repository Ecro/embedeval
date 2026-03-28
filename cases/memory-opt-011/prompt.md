Write a Zephyr C program that implements a sensor data processing pipeline for a resource-constrained Cortex-M0+ target with 32KB total RAM.

Requirements:
1. Include zephyr/kernel.h
2. Define static buffers for:
   - Raw sensor sample buffer (multiple channels)
   - Moving average filter state
   - Processed output buffer ready for transmission
3. Implement a main loop that:
   - Simulates reading sensor data into the raw buffer
   - Applies a simple moving average filter
   - Copies result to the output buffer
   - Prints processed values with printk
4. Use #define for all buffer sizes (no magic numbers)

Output ONLY the complete C source file.
