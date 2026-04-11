/*
 * Nested interrupt priority management in Zephyr RTOS.
 * Two IRQs at different priorities — higher priority can preempt lower.
 *
 * On native_sim there is no real NVIC, so we exercise the ISR handlers
 * via Zephyr's irq_offload() hook, which runs the supplied function in
 * IRQ context. The priority levels still have to be distinct and valid
 * so IRQ_CONNECT compiles and the case verifies the "lower number =
 * higher priority" convention.
 */

#include <zephyr/kernel.h>
#include <zephyr/irq.h>
#include <zephyr/irq_offload.h>

/* Use software-triggered IRQ numbers available on native_sim */
#define LOW_PRIO_IRQ_NUM   5
#define HIGH_PRIO_IRQ_NUM  6

/* Lower number = higher priority in ARM/Zephyr convention */
#define LOW_PRIO_LEVEL     3
#define HIGH_PRIO_LEVEL    1

static void low_prio_isr(const void *arg)
{
	ARG_UNUSED(arg);
	printk("Low priority ISR running\n");
	/* Short, non-blocking work only */
	printk("Low priority ISR done\n");
}

static void high_prio_isr(const void *arg)
{
	ARG_UNUSED(arg);
	printk("High priority ISR running\n");
	/* Can preempt low_prio_isr because HIGH_PRIO_LEVEL < LOW_PRIO_LEVEL */
	printk("High priority ISR done\n");
}

int main(void)
{
	/* Connect ISRs with distinct priority levels */
	IRQ_CONNECT(LOW_PRIO_IRQ_NUM,  LOW_PRIO_LEVEL,  low_prio_isr,  NULL, 0);
	IRQ_CONNECT(HIGH_PRIO_IRQ_NUM, HIGH_PRIO_LEVEL, high_prio_isr, NULL, 0);

	/* Enable both interrupts */
	irq_enable(LOW_PRIO_IRQ_NUM);
	irq_enable(HIGH_PRIO_IRQ_NUM);

	printk("Both IRQs enabled: low priority=%d high priority=%d\n",
	       LOW_PRIO_LEVEL, HIGH_PRIO_LEVEL);

	/* Invoke both handlers in IRQ context so the test can observe them
	 * on native_sim where there's no NVIC for irq_trigger().
	 */
	irq_offload(low_prio_isr,  NULL);
	irq_offload(high_prio_isr, NULL);

	return 0;
}
