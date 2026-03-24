Write a Zephyr RTOS application that uses the hardware counter API for precise microsecond-level timing measurements.

Requirements:
1. Get the counter device using DEVICE_DT_GET(DT_ALIAS(counter0)) and verify with device_is_ready()
2. Define a counter alarm callback; the callback MUST NOT block (no k_sleep, no printk, no mutex)
3. In the alarm callback, record the current counter value using counter_get_value() into a global variable shared with the main thread
4. In main():
   a. Start the counter with counter_start()
   b. Read the initial counter value with counter_get_value()
   c. Set a counter alarm using counter_set_channel_alarm() with a short tick offset
   d. Wait for the alarm to fire using k_sleep(K_MSEC(100))
   e. Read the final counter value again
   f. Calculate elapsed ticks (final - initial)
   g. Print the elapsed ticks with printk
5. Stop the counter with counter_cancel_channel_alarm() or counter_stop()

Use ONLY Zephyr counter API. Do NOT use xTimerCreate() (FreeRTOS), timerfd_create() (Linux), or SetTimer() (Win32).
The ISR/alarm callback must be non-blocking — no printk, no sleep, no synchronization primitives.

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/counter.h.

Output ONLY the complete C source file.
