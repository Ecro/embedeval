Write a Zephyr RTOS application that implements a device power management callback handling suspend and resume transitions.

Requirements:
1. Include the necessary Zephyr headers for kernel and device power management
2. Implement a PM action callback that handles suspend and resume device power state transitions
3. Print "Device suspended" when the device enters suspend, and "Device resumed" when it exits suspend
4. Return an appropriate error code for unsupported power actions
5. Use a switch statement to dispatch on the power action
6. In main(), obtain a device reference and exercise the suspend and resume transitions
7. Check return values from the PM calls and print status
8. Return 0 from main on success

Output ONLY the complete C source file.
