Write a Zephyr RTOS application that overrides the system PM policy to prevent deep sleep while a network activity period is active.

Requirements:
1. Include zephyr/kernel.h and zephyr/pm/policy.h
2. Implement start_network_activity() that:
   - Acquires a PM state lock to prevent deep sleep: pm_policy_state_lock_get(PM_STATE_SUSPEND_TO_RAM, PM_ALL_SUBSTATES)
   - Prints "Network active — deep sleep prevented"
3. Implement stop_network_activity() that:
   - Releases the PM state lock: pm_policy_state_lock_put(PM_STATE_SUSPEND_TO_RAM, PM_ALL_SUBSTATES)
   - Prints "Network idle — deep sleep allowed"
4. In main():
   - Call start_network_activity()
   - Simulate network work with k_sleep(K_MSEC(500))
   - Call stop_network_activity()
   - Sleep forever with k_sleep(K_FOREVER)

CRITICAL RULES:
- pm_policy_state_lock_get MUST be paired with pm_policy_state_lock_put (no leaks)
- Use PM_STATE_SUSPEND_TO_RAM for deep sleep prevention
- Do NOT use PM_ALL_SUBSTATES literal if it causes compile issues — use 0 (all substates)
- Lock MUST be acquired before active period, released after
- DO NOT call pm_state_force() here — that forces a transition, not a prevention

Use the Zephyr API: pm_policy_state_lock_get, pm_policy_state_lock_put, PM_STATE_SUSPEND_TO_RAM.

Output ONLY the complete C source file.
