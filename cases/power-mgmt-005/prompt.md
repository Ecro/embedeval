Write a Zephyr RTOS application that suspends and resumes three devices in correct dependency order with rollback on failure.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, and zephyr/pm/device.h
2. Define a PM state enum or use bool to track each device state (active/suspended)
3. Implement a single PM action callback used by all three devices:
   static int my_pm_action(const struct device *dev, enum pm_device_action action)
   - Handles SUSPEND (print "device X suspended", return 0) and RESUME (print "device X resumed", return 0)
   - Returns -ENOTSUP for other actions
4. Declare three mock devices (dev_a, dev_b, dev_c) where dev_c depends on dev_b, and dev_b depends on dev_a
5. Implement a suspend_all() function that:
   - Suspends dev_c first (dependent device), then dev_b, then dev_a (in dependency order)
   - If any suspend fails, rolls back by resuming already-suspended devices in reverse order
   - Returns 0 on success, negative error code on failure
6. Implement a resume_all() function that:
   - Resumes in reverse order: dev_a first, then dev_b, then dev_c
   - Checks that each device was actually suspended before resuming
   - Returns 0 on success, negative error code on failure
7. In main():
   - Call suspend_all() and print result
   - Call resume_all() and print result
   - Return 0

Suspend order MUST be: dev_c, dev_b, dev_a (dependent first).
Resume order MUST be: dev_a, dev_b, dev_c (reverse of suspend).
Rollback MUST resume already-suspended devices if a later suspend fails.

Use the Zephyr API: pm_device_action_run, PM_DEVICE_ACTION_SUSPEND, PM_DEVICE_ACTION_RESUME.

Output ONLY the complete C source file.
