Write a Zephyr RTOS application that configures a window watchdog with both minimum and maximum feed timing constraints.

Requirements:
1. Obtain the watchdog device from the devicetree and verify it is ready
2. Configure a window watchdog that detects both stalled tasks (feeding too late) and runaway loops (feeding too early)
3. The feed window must have a nonzero minimum — feeding before the minimum elapsed time is a violation
4. In the main loop, time the watchdog feeds to fall within the valid window
5. Print timing information before and after each feed
6. The watchdog should not trigger during debug halts

Output ONLY the complete C source file.
