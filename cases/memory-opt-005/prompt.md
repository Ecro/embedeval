Write a Zephyr RTOS application that uses memory domains and partitions to isolate a user-mode thread.

Requirements:
1. Include zephyr/kernel.h and zephyr/app_memory/app_memdomain.h
2. Define a memory partition using K_APPMEM_PARTITION_DEFINE(app_partition)
3. Declare a memory domain: static struct k_mem_domain app_domain
4. Declare a shared data variable in the partition's section:
   - Use K_APP_DMEM(app_partition) int shared_counter = 0
5. Define a user thread stack: K_THREAD_STACK_DEFINE(user_stack, 1024)
6. Define struct k_thread user_thread
7. Implement a user thread function:
   - Increment shared_counter and print its value with printk
   - Call k_sleep(K_MSEC(100)) in a loop (3 iterations then return)
8. In main():
   - Initialize the domain: k_mem_domain_init(&app_domain, 0, NULL)
   - Add the partition: k_mem_domain_add_partition(&app_domain, &app_partition)
   - Create the user thread with k_thread_create()
   - Assign domain to thread: k_mem_domain_add_thread(&app_domain, &user_thread)
   - Wait for thread to finish with k_thread_join(&user_thread, K_FOREVER)

IMPORTANT: k_mem_domain_init must be called before k_mem_domain_add_partition.
Partitions must not overlap — define each with a unique K_APPMEM_PARTITION_DEFINE.
The thread MUST be added to the domain with k_mem_domain_add_thread after creation.
Without this, the thread cannot access the partition memory in user mode.

Output ONLY the complete C source file.
