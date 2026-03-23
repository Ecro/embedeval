Write a Zephyr RTOS device power management action handler.

Requirements:
1. Include zephyr/pm/device.h and zephyr/kernel.h
2. Implement a PM action callback function with signature:
   static int my_pm_action(const struct device *dev, enum pm_device_action action)
3. Handle PM_DEVICE_ACTION_SUSPEND: print "Device suspended" and return 0
4. Handle PM_DEVICE_ACTION_RESUME: print "Device resumed" and return 0
5. For any other action, return -ENOTSUP
6. Use a switch statement on the action parameter
7. In main(), get a device reference (use DEVICE_DT_GET(DT_NODELABEL(my_dev)) or a mock)
8. Call pm_device_action_run() to test suspend, then resume
9. Check return values and print status
10. Return 0 from main on success

Use the Zephyr PM API: pm_device_action_run, PM_DEVICE_ACTION_SUSPEND, PM_DEVICE_ACTION_RESUME.

Output ONLY the complete C source file.
