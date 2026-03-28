Write a Zephyr RTOS application where two threads safely share two mutexes without deadlocking.

Requirements:
1. Declare two mutexes
2. Implement two threads that each need to hold both mutexes simultaneously to do work
3. Each thread should print a message while holding both mutexes, then release them
4. Both threads repeat in a loop
5. Ensure the application is free from deadlocks under all scheduling scenarios
6. In main(), let the statically-defined threads run and sleep forever

Output ONLY the complete C source file.
