Write an ESP-IDF application that uses the high-resolution esp_timer to fire a periodic callback every 1 second.

Requirements:
1. Define a callback function that prints the current timer count and increments a counter
2. Create the timer with esp_timer_create using the callback
3. Start the timer as periodic with a period of 1,000,000 microseconds (1 second)
4. Let the timer run for 5 iterations then stop it
5. Delete the timer with esp_timer_delete after stopping
6. Handle all esp_err_t return values

Use esp_timer_create, esp_timer_start_periodic, esp_timer_stop, esp_timer_delete.
Do NOT use FreeRTOS software timers (xTimerCreate) — use esp_timer only.
Include proper headers.
Output ONLY the complete C source file.
