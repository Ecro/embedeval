Write a Zephyr RTOS application that isolates a thread's memory access using memory domains and partitions, so the thread can only access its assigned memory region.

Requirements:
1. Include the necessary headers for kernel and application memory domains
2. Define a memory partition and a memory domain
3. Place a shared counter variable in the partition's data section so only threads assigned to that domain can access it
4. Define a user thread with a 1024-byte stack
5. The user thread increments the shared counter 3 times (with a short delay between increments), printing the value each time
6. In main():
   - Initialize the domain
   - Add the partition to the domain
   - Create the user thread
   - Assign the thread to the domain
   - Wait for the thread to finish

Output ONLY the complete C source file.
