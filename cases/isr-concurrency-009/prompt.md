Write a Zephyr RTOS application where a thread efficiently waits for signals raised by an ISR using the poll API.

Requirements:
1. Set up a signal mechanism that an ISR can trigger and a thread can wait on
2. Implement an ISR handler that raises the signal to notify the waiting thread
3. Implement a polling thread that blocks until a signal arrives, processes it, then resets state and waits again
4. The polling thread should print the received signal value
5. In main(), initialize all required objects, start the polling thread, and simulate ISR events

Output ONLY the complete C source file.
