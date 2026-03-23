Write a Zephyr RTOS application that submits multiple work items to the system workqueue and waits for all to complete using a counting semaphore.

Requirements:
1. Include zephyr/kernel.h
2. Define NUM_WORK_ITEMS as 5
3. Declare an array of struct k_work items: work_items[NUM_WORK_ITEMS]
4. Declare a k_sem named completion_sem initialized with count=0, limit=NUM_WORK_ITEMS
5. Implement work_handler(struct k_work *work) that:
   - Determines which work item number this is (use ARRAY_INDEX or pointer arithmetic)
   - Prints "Work item N completed" with printk
   - Calls k_sem_give(&completion_sem) to signal completion
6. In main():
   - Initialize ALL work items with k_work_init() BEFORE submitting any
   - Submit all work items with k_work_submit() to the system work queue
   - Wait for ALL completions: loop NUM_WORK_ITEMS times calling k_sem_take(&completion_sem, K_FOREVER)
   - Print "All work items completed" when done
   - Return 0

CRITICAL RULES:
- k_work_init() MUST be called before k_work_submit() (LLM failure: submitting uninitialized work)
- k_sem_give() count must match k_sem_take() count (NUM_WORK_ITEMS each)
- Use k_work_submit() for system work queue (not k_work_submit_to_queue with custom queue)
- Semaphore initial count MUST be 0 (not NUM_WORK_ITEMS)

Use the Zephyr API: k_work, k_work_init, k_work_submit, k_sem, k_sem_init, k_sem_give, k_sem_take.

Output ONLY the complete C source file.
