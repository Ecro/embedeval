/*
 * Lock-free SPSC ring queue for Zephyr RTOS.
 * Power-of-2 buffer with atomic indices — no locks required.
 */

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#define QUEUE_SIZE 16  /* MUST be power of 2 */
#define QUEUE_MASK (QUEUE_SIZE - 1)

struct spsc_queue {
	uint8_t    buf[QUEUE_SIZE];
	atomic_t   write_idx;
	atomic_t   read_idx;
};

static struct spsc_queue q;

static int spsc_push(struct spsc_queue *q, uint8_t val)
{
	atomic_val_t w = atomic_get(&q->write_idx);
	atomic_val_t r = atomic_get(&q->read_idx);

	/* Check full: queue holds at most QUEUE_SIZE-1 items */
	if ((uint32_t)(w - r) >= QUEUE_SIZE) {
		return -1; /* full */
	}

	q->buf[w & QUEUE_MASK] = val;

	/* Ensure write is visible before advancing the index */
	compiler_barrier();
	atomic_set(&q->write_idx, w + 1);
	return 0;
}

static int spsc_pop(struct spsc_queue *q, uint8_t *val)
{
	atomic_val_t r = atomic_get(&q->read_idx);
	atomic_val_t w = atomic_get(&q->write_idx);

	if (r == w) {
		return -1; /* empty */
	}

	*val = q->buf[r & QUEUE_MASK];

	/* Ensure read is complete before advancing the index */
	compiler_barrier();
	atomic_set(&q->read_idx, r + 1);
	return 0;
}

int main(void)
{
	uint8_t val;

	atomic_set(&q.write_idx, 0);
	atomic_set(&q.read_idx, 0);

	spsc_push(&q, 0xAB);
	spsc_push(&q, 0xCD);

	if (spsc_pop(&q, &val) == 0) {
		printk("Popped: 0x%02X\n", val);
	}
	if (spsc_pop(&q, &val) == 0) {
		printk("Popped: 0x%02X\n", val);
	}
	if (spsc_pop(&q, &val) != 0) {
		printk("Queue empty as expected\n");
	}

	return 0;
}
