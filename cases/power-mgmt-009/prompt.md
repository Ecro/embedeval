Write a Zephyr RTOS application that adjusts PM policy based on battery charge level read from an ADC.

Requirements:
1. Include zephyr/kernel.h, zephyr/drivers/adc.h
2. Define LOW_BATTERY_THRESHOLD as 20 (percent)
3. Define a mock function int read_battery_percent() that:
   - Simulates ADC read: uses a static counter to return values 100, 80, 50, 15, 10 in sequence
   - In production this would use adc_read() + adc_raw_to_millivolts()
   - Returns a value 0-100 representing charge percentage
4. Implement apply_pm_policy(int battery_pct) that:
   - If battery_pct <= LOW_BATTERY_THRESHOLD: enters aggressive sleep mode
     - Prints "Low battery (%d%%), entering aggressive sleep"
     - Calls pm_policy_state_lock_get(PM_STATE_SUSPEND_TO_IDLE, PM_ALL_SUBSTATES) — allow only deepest sleep
     - Note: this is inverted — actually lock IDLE to FORCE deeper sleep. Alternatively use pm_state_force.
   - Else: normal operation
     - Prints "Battery OK (%d%%), normal PM"
     - Does not lock any PM states
5. In main(): read battery every 500ms, call apply_pm_policy, demonstrate different behaviors

CRITICAL:
- ADC read MUST happen BEFORE PM decision
- Threshold comparison MUST be present
- At least 2 DIFFERENT PM behaviors based on battery level
- Use PM_STATE_SUSPEND_TO_IDLE for light sleep, PM_STATE_SUSPEND_TO_RAM for deep sleep

Output ONLY the complete C source file.
