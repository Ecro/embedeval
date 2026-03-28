#include <zephyr/kernel.h>
#include <string.h>

#define NUM_CHANNELS    4
#define SAMPLE_DEPTH    16
#define FILTER_WINDOW   8
#define OUTPUT_BUF_SIZE 64

static uint16_t raw_samples[NUM_CHANNELS * SAMPLE_DEPTH];
static uint32_t filter_state[NUM_CHANNELS * FILTER_WINDOW];
static uint16_t output_buf[OUTPUT_BUF_SIZE];

static uint16_t moving_average(const uint32_t *history, int window)
{
    uint32_t sum = 0;
    for (int i = 0; i < window; i++) {
        sum += history[i];
    }
    return (uint16_t)(sum / window);
}

int main(void)
{
    printk("Sensor pipeline started (RAM budget: 32KB target)\n");

    /* Simulate sensor read */
    for (int ch = 0; ch < NUM_CHANNELS; ch++) {
        for (int s = 0; s < SAMPLE_DEPTH; s++) {
            raw_samples[ch * SAMPLE_DEPTH + s] = (uint16_t)(ch * 100 + s);
        }
    }

    /* Apply moving average filter per channel */
    for (int ch = 0; ch < NUM_CHANNELS; ch++) {
        for (int w = 0; w < FILTER_WINDOW; w++) {
            filter_state[ch * FILTER_WINDOW + w] =
                raw_samples[ch * SAMPLE_DEPTH + w];
        }
        output_buf[ch] = moving_average(
            &filter_state[ch * FILTER_WINDOW], FILTER_WINDOW);
        printk("Ch%d avg: %u\n", ch, output_buf[ch]);
    }

    printk("Pipeline complete\n");
    return 0;
}
