Write a Zephyr RTOS application that uses the hardware counter driver API to set a one-shot alarm.

Requirements:
1. Get the counter device using DEVICE_DT_GET(DT_ALIAS(counter0)) or equivalent
2. Verify the device is initialized and ready before use
3. Start the counter using counter_start()
4. Define an alarm callback function that prints "Alarm fired" using printk
5. Set a one-shot alarm using counter_set_channel_alarm() with channel 0 and a 1-second delay
6. Convert 1 second to ticks using counter_us_to_ticks() with 1000000 microseconds
7. In main(), after setting the alarm, sleep 3 seconds then return

Use the Zephyr counter API: counter_start, counter_set_channel_alarm, counter_us_to_ticks.

Include proper headers: zephyr/kernel.h, zephyr/drivers/counter.h, zephyr/device.h.

Output ONLY the complete C source file.
