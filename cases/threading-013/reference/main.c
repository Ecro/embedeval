#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#define PRODUCER_STACK_SIZE 1024
#define CONSUMER_STACK_SIZE 1024
#define PRODUCER_PRIORITY   2
#define CONSUMER_PRIORITY   3
#define NUM_SAMPLES         10
#define PRODUCE_INTERVAL_MS 100

/* Shared memory structure with explicit alignment for hardware access safety.
 * __aligned(4) ensures the struct starts on a 4-byte boundary, preventing
 * cache line splits and satisfying DMA alignment requirements.
 */
struct shared_ipc {
    uint32_t sensor_value;
    uint32_t sequence;
    volatile int flag; /* volatile: compiler must not cache this in a register */
} __aligned(4);

static struct shared_ipc shared_region;

static void producer_thread(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    for (uint32_t i = 0; i < NUM_SAMPLES; i++) {
        /* Wait until consumer has cleared the flag (previous data consumed) */
        while (shared_region.flag != 0) {
            k_yield();
        }

        /* Write data fields BEFORE setting the flag.
         * compiler_barrier() prevents the compiler from reordering the
         * flag assignment ahead of the data writes.
         */
        shared_region.sensor_value = 100u + i * 10u;
        shared_region.sequence = i;
        compiler_barrier();
        shared_region.flag = 1;

        printk("[producer] wrote sample %u: value=%u\n",
               i, shared_region.sensor_value);

        k_msleep(PRODUCE_INTERVAL_MS);
    }

    printk("[producer] done\n");
}

static void consumer_thread(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    uint32_t consumed = 0;

    while (consumed < NUM_SAMPLES) {
        /* Poll flag: wait until producer signals new data is ready */
        if (shared_region.flag == 0) {
            k_yield();
            continue;
        }

        /* Read data while flag is still set (data is stable) */
        uint32_t value = shared_region.sensor_value;
        uint32_t seq   = shared_region.sequence;

        /* Acknowledge consumption: clear flag so producer can write again */
        shared_region.flag = 0;

        printk("[consumer] received sample %u: value=%u\n", seq, value);
        consumed++;
    }

    printk("[consumer] done, %u samples processed\n", consumed);
}

K_THREAD_DEFINE(producer_tid, PRODUCER_STACK_SIZE,
                producer_thread, NULL, NULL, NULL,
                PRODUCER_PRIORITY, 0, 0);

K_THREAD_DEFINE(consumer_tid, CONSUMER_STACK_SIZE,
                consumer_thread, NULL, NULL, NULL,
                CONSUMER_PRIORITY, 0, 0);

int main(void)
{
    printk("Shared-memory IPC demo started\n");
    k_sleep(K_FOREVER);
    return 0;
}
