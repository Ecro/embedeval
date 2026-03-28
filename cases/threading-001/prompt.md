Write a Zephyr RTOS application implementing a producer-consumer pattern with a message queue.

Requirements:
1. Define a message struct carrying an integer value
2. Create a bounded message queue
3. Create a producer thread that sends incrementing values into the queue with a short delay between sends
4. Create a consumer thread that receives and prints values from the queue
5. The producer should have higher scheduling priority than the consumer
6. Both threads should be statically defined
7. main() should sleep indefinitely while the threads run

Output ONLY the complete C source file.
