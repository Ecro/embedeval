Write a Zephyr RTOS application that configures two independent watchdog channels with different timeout requirements.

Requirements:
1. Obtain the watchdog device from the devicetree and verify it is ready
2. Configure two separate watchdog channels: one for a fast-responding subsystem and one for a slower periodic task
3. Each channel should reset the system if its respective task stalls
4. Feed each channel at the correct rate relative to its timeout — feeding too late causes reset
5. Print which channel is being serviced each time
6. The watchdog should not trigger during debug halts

Output ONLY the complete C source file.
