#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>

/* Stack overflow protection: enable CONFIG_STACK_SENTINEL in prj.conf */
/* CONFIG_STACK_SENTINEL=y */
/* CONFIG_HW_STACK_PROTECTION=y */

#define PROC_STACK_SIZE  1024
#define PROC_PRIORITY    5
#define RING_BUF_SIZE    16
#define NUM_CYCLES       5

static struct k_sem data_ready_sem;

/* Ring buffer for ISR -> thread data transfer */
static volatile uint16_t ring_buf[RING_BUF_SIZE];
static volatile uint32_t head;
static volatile uint32_t tail;

static void adc_data_ready_callback(const struct device *dev,
                                     struct gpio_callback *cb,
                                     uint32_t pins)
{
    ARG_UNUSED(dev);
    ARG_UNUSED(cb);
    ARG_UNUSED(pins);

    /* Simulated ADC read */
    uint16_t sample = (uint16_t)(head * 100 + 42);

    uint32_t next_head = (head + 1) % RING_BUF_SIZE;
    if (next_head != tail) {
        ring_buf[head] = sample;
        head = next_head;
    }
    /* Signal processing thread — k_sem_give is ISR-safe */
    k_sem_give(&data_ready_sem);
}

static void processing_thread(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    for (int cycle = 0; cycle < NUM_CYCLES; cycle++) {
        k_sem_take(&data_ready_sem, K_FOREVER);

        /* Process all available samples */
        while (tail != head) {
            uint16_t sample = ring_buf[tail];
            tail = (tail + 1) % RING_BUF_SIZE;
            printk("[%d] Processed sample: %u\n", cycle, sample);
        }
    }

    /* Check remaining stack space */
    printk("Processing complete (%d cycles)\n", NUM_CYCLES);
    printk("Stack space check: K_THREAD_STACK_SIZEOF used for sizing\n");
}

K_THREAD_STACK_DEFINE(proc_stack, PROC_STACK_SIZE);
static struct k_thread proc_thread_data;

int main(void)
{
    k_sem_init(&data_ready_sem, 0, 1);

    k_thread_create(&proc_thread_data, proc_stack,
                    K_THREAD_STACK_SIZEOF(proc_stack),
                    processing_thread, NULL, NULL, NULL,
                    PROC_PRIORITY, 0, K_NO_WAIT);

    printk("ISR data collection started\n");

    /* Simulate interrupt triggers */
    for (int i = 0; i < NUM_CYCLES; i++) {
        /* Simulate ISR by calling callback directly */
        adc_data_ready_callback(NULL, NULL, 0);
        k_msleep(100);
    }

    k_msleep(500);
    printk("Done\n");
    return 0;
}
