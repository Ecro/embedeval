#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#define SENSOR_PERIOD_MS   100
#define OUTPUT_PERIOD_MS   1000
#define FILTER_LEN         10
#define SENSOR_STACK_SIZE  1024
#define OUTPUT_STACK_SIZE  1024
#define SENSOR_PRIORITY    5
#define OUTPUT_PRIORITY    7

/* Message queue: sensor thread produces, output thread consumes */
K_MSGQ_DEFINE(filtered_msgq, sizeof(int32_t), 4, 4);

/* Circular buffer for moving average */
static int32_t samples[FILTER_LEN];
static int     sample_idx;
static int32_t sample_sum;
static int     sample_count;

/* Simulated sensor read */
static int32_t read_sensor(void)
{
    static int32_t value = 100;
    /* Simple ramp simulation */
    value = (value + 3) % 1024;
    return value;
}

static int32_t moving_average(int32_t new_sample)
{
    /* Remove oldest sample from sum when buffer is full */
    if (sample_count == FILTER_LEN) {
        sample_sum -= samples[sample_idx];
    } else {
        sample_count++;
    }

    samples[sample_idx] = new_sample;
    sample_sum += new_sample;
    sample_idx = (sample_idx + 1) % FILTER_LEN;

    return sample_sum / sample_count;
}

static void sensor_thread(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    while (1) {
        int32_t raw = read_sensor();
        int32_t filtered = moving_average(raw);

        /* Non-blocking put: drop oldest if full */
        k_msgq_put(&filtered_msgq, &filtered, K_NO_WAIT);

        k_sleep(K_MSEC(SENSOR_PERIOD_MS));
    }
}

static void output_thread(void *p1, void *p2, void *p3)
{
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    while (1) {
        int32_t value;

        /* Collect latest filtered sample from queue */
        if (k_msgq_get(&filtered_msgq, &value, K_NO_WAIT) == 0) {
            printk("filtered=%d\n", value);
        }

        k_sleep(K_SECONDS(1));
    }
}

K_THREAD_DEFINE(sensor_tid, SENSOR_STACK_SIZE,
                sensor_thread, NULL, NULL, NULL,
                SENSOR_PRIORITY, 0, 0);

K_THREAD_DEFINE(output_tid, OUTPUT_STACK_SIZE,
                output_thread, NULL, NULL, NULL,
                OUTPUT_PRIORITY, 0, 0);

int main(void)
{
    printk("Sensor-filter-UART pipeline started\n");
    k_sleep(K_FOREVER);
    return 0;
}
