Implement a Zephyr RTOS application that sends sensor data from an ISR to a processing thread using a message queue.

Requirements:
1. Define a message struct containing a sensor value
2. Create a message queue large enough to buffer multiple messages
3. Implement an ISR handler that enqueues sensor readings into the message queue
4. Implement a consumer thread that retrieves and prints messages from the queue
5. In main(), simulate the ISR firing multiple times, then allow the consumer thread time to process
6. The consumer thread should be defined statically with an appropriate stack size

Output ONLY the complete C source file.
