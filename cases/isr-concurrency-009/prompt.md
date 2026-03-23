Write a Zephyr RTOS application where an ISR raises a k_poll_signal and a thread waits using k_poll.

Requirements:
1. Include zephyr/kernel.h
2. Declare a k_poll_signal named isr_signal and initialize it with k_poll_signal_init()
3. Declare a k_poll_event array with at least one entry watching the signal
4. Initialize the poll event with K_POLL_EVENT_INITIALIZER(K_POLL_TYPE_SIGNAL, K_POLL_MODE_NOTIFY_ONLY, &isr_signal)
5. Implement an ISR handler (void isr_handler) that:
   - Calls k_poll_signal_raise(&isr_signal, 1) — ISR-safe, non-blocking
   - Does NOT call k_poll() — that blocks
   - Does NOT call k_sem_take() or k_mutex_lock()
6. Implement a polling thread that:
   - Loops calling k_poll(events, N, K_FOREVER) to wait
   - After waking, checks event.state == K_POLL_STATE_SIGNALED
   - Resets the signal with k_poll_signal_reset()
   - Resets event state to K_POLL_STATE_NOT_READY
   - Prints the received result with printk
7. In main(): initialize signal and events, start polling thread

The ISR MUST use k_poll_signal_raise() — NOT k_sem_give() or k_fifo_put() for this pattern.
The thread MUST use k_poll() — NOT k_sem_take() or busy-waiting.
Signal MUST be initialized with k_poll_signal_init() before use.

Use the Zephyr API: k_poll_signal, k_poll_signal_init, k_poll_signal_raise, k_poll, K_POLL_EVENT_INITIALIZER.

Output ONLY the complete C source file.
