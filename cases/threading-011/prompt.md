Write a Zephyr C program that implements a periodic control loop thread for motor control.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/printk.h
2. Create a dedicated high-priority thread for the control loop
3. The control loop must run at a fixed 10ms period
4. In main():
   - Start the control loop thread
   - Sleep indefinitely (or run a low-priority monitoring task)
5. In the control loop:
   - Read simulated sensor data
   - Compute a simple PID-like output (proportional term is sufficient)
   - Apply the output (simulated with printk)
   - Run for at least 10 iterations

The system must handle the case where a control iteration takes longer than the period.

Output ONLY the complete C source file.
