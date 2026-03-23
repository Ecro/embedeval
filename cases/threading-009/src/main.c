/*
 * Thread pool pattern using system work queue with completion tracking.
 * Counting semaphore tracks how many work items have completed.
 */

#include <zephyr/kernel.h>

#define NUM_WORK_ITEMS 5

static struct k_work work_items[NUM_WORK_ITEMS];

/* Initial count = 0; limit = NUM_WORK_ITEMS */
static struct k_sem completion_sem;

static void work_handler(struct k_work *work)
{
	/* Determine which item this is via pointer arithmetic */
	int idx = (int)(work - work_items);

	printk("Work item %d completed\n", idx);

	/* Signal one completion */
	k_sem_give(&completion_sem);
}

int main(void)
{
	/* Initialize semaphore with count=0, limit=NUM_WORK_ITEMS */
	k_sem_init(&completion_sem, 0, NUM_WORK_ITEMS);

	/* Initialize ALL work items before submitting any */
	for (int i = 0; i < NUM_WORK_ITEMS; i++) {
		k_work_init(&work_items[i], work_handler);
	}

	/* Submit all work items to the system work queue */
	for (int i = 0; i < NUM_WORK_ITEMS; i++) {
		k_work_submit(&work_items[i]);
	}

	/* Wait for each work item to complete */
	for (int i = 0; i < NUM_WORK_ITEMS; i++) {
		k_sem_take(&completion_sem, K_FOREVER);
	}

	printk("All work items completed\n");
	return 0;
}
