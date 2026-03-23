Write a Zephyr RTOS application that demonstrates the timeout pattern using a semaphore with a timed wait.

Requirements:
1. Define a static k_sem named "event_sem" with initial count 0 and limit 1 using K_SEM_DEFINE
2. Define a k_timer that gives the semaphore after 2 seconds (simulating a deferred event)
3. In the timer expiry callback, call k_sem_give(&event_sem)
4. In main():
   a. Start the timer with k_timer_start for a one-shot 2-second delay
   b. Attempt to take the semaphore with a 5-second timeout: k_sem_take(&event_sem, K_MSEC(5000))
   c. If k_sem_take returns 0, print "Event received" with printk
   d. If k_sem_take returns -EAGAIN (timeout), print "Timeout: event did not arrive" with printk
   e. Handle the error path — do NOT use a busy-wait polling loop
5. After handling the event or timeout, print a final "Done" message

The timeout value MUST be > 0. Do NOT use while(1) to poll the semaphore — use k_sem_take with a timeout parameter.

Include header: zephyr/kernel.h only.

Output ONLY the complete C source file.
