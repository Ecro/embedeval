Write a Zephyr RTOS application demonstrating peripheral power gating using the device power management API.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, and zephyr/pm/device.h
2. Declare a mock peripheral device pointer (use a placeholder like DEVICE_DT_GET_ANY or a static mock)
3. Implement peripheral_use() function that:
   - Enables the peripheral: calls pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME)
   - Does work with the peripheral (printk "Using peripheral")
   - Disables the peripheral after use: calls pm_device_action_run(dev, PM_DEVICE_ACTION_SUSPEND)
4. Implement a tracking bool 'peripheral_active' to track current state
5. Only call RESUME if peripheral is currently suspended (check state first)
6. Only call SUSPEND if peripheral is currently active
7. In main(): demonstrate periodic peripheral use with k_sleep between uses

CRITICAL: Do NOT use hallucinated Zephyr APIs that do not exist:
- NO peripheral_power_off() — does not exist in Zephyr
- NO peripheral_power_on() — does not exist in Zephyr
- NO clk_disable()/clk_enable() — Linux kernel APIs, NOT Zephyr
- NO clock_control_off()/clock_control_on() without the full Zephyr clock_control subsystem
Use ONLY: pm_device_action_run, PM_DEVICE_ACTION_SUSPEND, PM_DEVICE_ACTION_RESUME

Output ONLY the complete C source file.
