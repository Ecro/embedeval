Write a Zephyr RTOS application that checks device power state before use and resumes it if suspended.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, and zephyr/pm/device.h
2. Declare a device pointer (use a placeholder or NULL for demonstration)
3. Implement safe_device_use(const struct device *dev) that:
   - Calls pm_device_state_get(dev, &state) to get current state
   - Checks if state == PM_DEVICE_STATE_SUSPENDED
   - If suspended: calls pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME) and prints "Resuming device"
   - If active: prints "Device already active"
   - Proceeds to "use" the device: prints "Using device"
4. In main():
   - Call safe_device_use() twice to demonstrate both paths
   - First call: device is "suspended" (simulate with initial state)
   - Return 0

Required enum values to use:
- PM_DEVICE_STATE_SUSPENDED (not PM_DEVICE_ACTION_SUSPEND — different enum!)
- PM_DEVICE_STATE_ACTIVE (for comparison)
- PM_DEVICE_ACTION_RESUME (for the resume call)

CRITICAL: pm_device_state_get() and PM_DEVICE_STATE_* are for QUERYING.
pm_device_action_run() and PM_DEVICE_ACTION_* are for CHANGING.
LLMs often confuse these two enum families.

Use the Zephyr API: pm_device_state_get, pm_device_action_run, PM_DEVICE_STATE_SUSPENDED, PM_DEVICE_ACTION_RESUME.

Output ONLY the complete C source file.
