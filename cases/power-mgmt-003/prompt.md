Write a Zephyr RTOS device power management callback that tracks device state and rejects duplicate transitions.

Requirements:
1. Include zephyr/kernel.h and zephyr/pm/device.h
2. Define an enum or bool to track device PM state (e.g., active vs. suspended)
3. Declare a static variable to hold the current device state, initialized to active
4. Implement a PM action callback with signature:
   static int my_pm_action(const struct device *dev, enum pm_device_action action)
5. In the callback:
   - For PM_DEVICE_ACTION_SUSPEND:
     - If already suspended, return -EALREADY
     - Otherwise, set state to suspended, print "Device suspended" and return 0
   - For PM_DEVICE_ACTION_RESUME:
     - If already active/resumed, return -EALREADY
     - Otherwise, set state to active, print "Device resumed" and return 0
   - For any other action, return -ENOTSUP
6. In main():
   - Call my_pm_action(NULL, PM_DEVICE_ACTION_SUSPEND) and print the result
   - Call my_pm_action(NULL, PM_DEVICE_ACTION_SUSPEND) again (duplicate) and verify it returns -EALREADY, print the result
   - Call my_pm_action(NULL, PM_DEVICE_ACTION_RESUME) and print the result
   - Return 0

The state tracking variable MUST be checked before applying any transition.
Duplicate transitions MUST return -EALREADY, not 0.

Use the Zephyr API: pm_device_action, PM_DEVICE_ACTION_SUSPEND, PM_DEVICE_ACTION_RESUME.

Output ONLY the complete C source file.
