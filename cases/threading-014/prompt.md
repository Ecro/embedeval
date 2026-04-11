Write a Zephyr application with two threads that share a flag and a data value.

Requirements:
1. A producer thread writes an integer value into a shared variable, then sets a shared flag to 1.
2. A consumer thread waits for the shared flag to become 1, then reads the shared value and prints it.
3. Use `K_THREAD_DEFINE` to create both threads statically.
4. The consumer MUST observe the value the producer wrote before the flag was set — the compiler must not reorder the flag write ahead of the data write, and the consumer must not read a stale data value after observing flag==1.
5. The consumer should print `value=<N>` once and exit.

Output ONLY the complete C source file.
