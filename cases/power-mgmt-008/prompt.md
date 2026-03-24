Write a Zephyr RTOS application that sets a wakeup timer before entering a deep sleep PM state.

Requirements:
1. Include zephyr/kernel.h and zephyr/pm/pm.h
2. Define SLEEP_DURATION_MS as 2000 (2 seconds)
3. Define WAKEUP_TIMER_MS as 1500 — MUST be less than SLEEP_DURATION_MS
4. Declare a static k_timer named wakeup_timer
5. Implement wakeup_timer_cb(struct k_timer *t) callback that:
   - Prints "Wakeup timer fired" with printk
6. In main():
   - Initialize wakeup_timer with k_timer_init(&wakeup_timer, wakeup_timer_cb, NULL)
   - Start wakeup_timer as a one-shot (fires once, no periodic repeat): k_timer_start(&wakeup_timer, K_MSEC(WAKEUP_TIMER_MS), ...)
   - Print "Entering deep sleep, wakeup in %d ms"
   - Force PM state: pm_state_force(0, &(struct pm_state_info){PM_STATE_SUSPEND_TO_RAM, 0, 0})
   - After wakeup, print "Returned from deep sleep"
   - Stop the timer: k_timer_stop(&wakeup_timer)

CRITICAL RULES:
- Timer MUST be started BEFORE pm_state_force (wakeup source must be armed first)
- WAKEUP_TIMER_MS MUST be less than SLEEP_DURATION_MS (timer fires before max allowed sleep)
- Use pm_state_force() to enter deep sleep — NOT k_sleep() which is just thread sleep
- Use PM_STATE_SUSPEND_TO_RAM for deep sleep

Use the Zephyr API: k_timer, k_timer_init, k_timer_start, k_timer_stop, pm_state_force, PM_STATE_SUSPEND_TO_RAM.

Output ONLY the complete C source file.