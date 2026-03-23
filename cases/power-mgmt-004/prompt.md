Write a Zephyr RTOS application demonstrating PM device runtime enable/disable with reference counting.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, and zephyr/pm/device_runtime.h
2. Implement a PM action callback with signature:
   static int my_pm_action(const struct device *dev, enum pm_device_action action)
   handling PM_DEVICE_ACTION_SUSPEND (print "Runtime: suspended") and PM_DEVICE_ACTION_RESUME (print "Runtime: resumed"), default returns -ENOTSUP
3. In main():
   - Get a device reference (use DEVICE_DT_GET(DT_NODELABEL(my_dev)) or a suitable mock device)
   - Call pm_device_runtime_enable() on the device, check return value
   - Print "Runtime PM enabled" on success
   - Call pm_device_runtime_get() to increment the reference count (device becomes active), check return value
   - Print "Got device reference" on success
   - Do some work: print "Doing work with device"
   - Call pm_device_runtime_put() to decrement the reference count (device may suspend), check return value
   - Print "Released device reference" on success
   - Call pm_device_runtime_disable() to disable runtime PM
   - Print "Runtime PM disabled"
   - Return 0

pm_device_runtime_enable() MUST be called before pm_device_runtime_get()/put().
Every pm_device_runtime_get() MUST be paired with a pm_device_runtime_put() to avoid reference leaks.

Use the Zephyr API: pm_device_runtime_enable, pm_device_runtime_disable, pm_device_runtime_get, pm_device_runtime_put.

Output ONLY the complete C source file.
