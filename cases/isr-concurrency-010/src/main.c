/*
 * Interrupt-safe deferred logging for Zephyr RTOS.
 * ISR writes to ring buffer; drain thread calls printk.
 * printk is NEVER called from ISR context.
 */

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#define LOG_BUF_SIZE 16

struct log_entry {
	uint32_t timestamp;
	uint32_t event_id;
	uint32_t data;
};

static struct log_entry log_buf[LOG_BUF_SIZE];
static atomic_t write_head;
static atomic_t read_tail;

/*
 * Called from ISR context — MUST NOT call printk or LOG_*.
 * Writes entry to ring buffer and advances write_head atomically.
 */
static void isr_log_write(uint32_t event_id, uint32_t data)
{
	atomic_val_t w = atomic_get(&write_head);
	atomic_val_t r = atomic_get(&read_tail);

	/* Drop entry silently if buffer full (ISR cannot block) */
	if ((uint32_t)(w - r) >= LOG_BUF_SIZE) {
		return;
	}

	volatile struct log_entry *entry = &log_buf[w % LOG_BUF_SIZE];

	entry->timestamp = k_cycle_get_32();
	entry->event_id  = event_id;
	entry->data      = data;

	compiler_barrier();
	atomic_set(&write_head, w + 1);
}

/* Simulated ISR — in real code this would be registered with IRQ_CONNECT */
static void my_isr(const void *arg)
{
	ARG_UNUSED(arg);
	isr_log_write(0x01, 0xDEAD);
}

#define DRAIN_STACK_SIZE 1024
#define DRAIN_PRIORITY   8

static void log_drain_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		k_msleep(10);

		atomic_val_t tail = atomic_get(&read_tail);
		atomic_val_t head = atomic_get(&write_head);

		while (tail != head) {
			struct log_entry entry = log_buf[tail % LOG_BUF_SIZE];

			compiler_barrier();
			atomic_set(&read_tail, tail + 1);
			tail++;

			printk("[%08u] event=0x%02X data=0x%08X\n",
			       entry.timestamp, entry.event_id, entry.data);
		}
	}
}

K_THREAD_DEFINE(drain_tid, DRAIN_STACK_SIZE,
		log_drain_thread, NULL, NULL, NULL,
		DRAIN_PRIORITY, 0, 0);

int main(void)
{
	atomic_set(&write_head, 0);
	atomic_set(&read_tail, 0);

	printk("Deferred logging demo started\n");

	/* Simulate several ISR triggers */
	my_isr(NULL);
	my_isr(NULL);
	my_isr(NULL);

	k_sleep(K_FOREVER);
	return 0;
}
