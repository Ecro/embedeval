Write a Zephyr C program that implements ISR-driven data collection from a simulated ADC sensor.

Requirements:
1. Include zephyr/kernel.h
2. Define a GPIO callback (simulating ADC data-ready interrupt)
3. In the ISR callback:
   - Read simulated ADC data into a ring buffer
   - Signal a processing thread via semaphore
4. Create a processing thread that:
   - Waits on the semaphore
   - Processes accumulated samples
   - Prints results with printk
5. In main():
   - Configure the interrupt
   - Start processing
   - Run for at least 5 simulated interrupt cycles

The system must be robust against stack overflow conditions.

Output ONLY the complete C source file.
