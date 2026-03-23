/*
 * ISR-to-thread signaling via k_poll_signal in Zephyr RTOS.
 * ISR raises signal; thread uses k_poll to wait without busy-looping.
 */

#include <zephyr/kernel.h>

static struct k_poll_signal isr_signal;

/* Poll event array — can watch multiple events simultaneously */
static struct k_poll_event events[1];

static void isr_handler(const void *arg)
{
	ARG_UNUSED(arg);

	/* k_poll_signal_raise is ISR-safe and non-blocking */
	k_poll_signal_raise(&isr_signal, 1);
}

#define POLL_STACK_SIZE 1024
#define POLL_PRIORITY   5

static void polling_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		int ret = k_poll(events, ARRAY_SIZE(events), K_FOREVER);

		if (ret == 0 && events[0].state == K_POLL_STATE_SIGNALED) {
			unsigned int result;
			int signaled;

			k_poll_signal_check(&isr_signal, &signaled, &result);
			printk("Signal received: result=%u\n", result);

			/* Must reset signal and event state for next poll */
			k_poll_signal_reset(&isr_signal);
			events[0].state = K_POLL_STATE_NOT_READY;
		}
	}
}

K_THREAD_DEFINE(poll_tid, POLL_STACK_SIZE,
		polling_thread, NULL, NULL, NULL,
		POLL_PRIORITY, 0, 0);

int main(void)
{
	k_poll_signal_init(&isr_signal);

	K_POLL_EVENT_INITIALIZER(events[0],
				 K_POLL_TYPE_SIGNAL,
				 K_POLL_MODE_NOTIFY_ONLY,
				 &isr_signal);

	printk("k_poll demo started\n");

	/* Simulate ISR trigger */
	isr_handler(NULL);

	k_sleep(K_FOREVER);
	return 0;
}
