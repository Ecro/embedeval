#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#define CONTROL_PERIOD_MS  10
#define CONTROL_STACK_SIZE 1024
#define CONTROL_PRIORITY   -1
#define NUM_ITERATIONS     20
#define SETPOINT           1000

static volatile int sensor_value = 500;
static volatile int actuator_output;
static volatile int deadline_misses;

static void control_loop(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    int64_t next_wakeup = k_uptime_get();

    for (int i = 0; i < NUM_ITERATIONS; i++) {
        int64_t start = k_uptime_get();

        /* Read sensor (simulated) */
        int error = SETPOINT - sensor_value;

        /* PID proportional term */
        int output = error / 4;
        actuator_output = output;

        /* Simulate sensor response */
        sensor_value += output / 10;

        printk("[%d] sensor=%d error=%d output=%d\n",
               i, sensor_value, error, output);

        /* Deadline check */
        int64_t elapsed = k_uptime_get() - start;
        if (elapsed >= CONTROL_PERIOD_MS) {
            deadline_misses++;
            printk("WARN: deadline miss #%d (took %lld ms)\n",
                   deadline_misses, elapsed);
            /* Skip sleep, run next iteration immediately */
            next_wakeup = k_uptime_get() + CONTROL_PERIOD_MS;
            continue;
        }

        /* Sleep until next period */
        next_wakeup += CONTROL_PERIOD_MS;
        int64_t remaining = next_wakeup - k_uptime_get();
        if (remaining > 0) {
            k_msleep((int32_t)remaining);
        }
    }

    printk("Control loop done. Deadline misses: %d\n", deadline_misses);
}

K_THREAD_DEFINE(control_tid, CONTROL_STACK_SIZE,
                control_loop, NULL, NULL, NULL,
                CONTROL_PRIORITY, 0, 0);

int main(void)
{
    printk("Motor control started (period=%d ms)\n", CONTROL_PERIOD_MS);
    k_sleep(K_FOREVER);
    return 0;
}
