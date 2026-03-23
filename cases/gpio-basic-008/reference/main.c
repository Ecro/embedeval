#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/adc.h>

static int16_t sample_buffer[1];

static const struct adc_channel_cfg ch_cfg = {
	.gain = ADC_GAIN_1,
	.reference = ADC_REF_INTERNAL,
	.acquisition_time = ADC_ACQ_TIME_DEFAULT,
	.channel_id = 0,
};

int main(void)
{
	const struct device *adc = DEVICE_DT_GET(DT_ALIAS(adc0));

	if (!device_is_ready(adc)) {
		printk("ADC device not ready\n");
		return -1;
	}

	int err = adc_channel_setup(adc, &ch_cfg);

	if (err < 0) {
		printk("ADC channel setup failed: %d\n", err);
		return -1;
	}

	struct adc_sequence seq = {
		.channels = BIT(0),
		.buffer = sample_buffer,
		.buffer_size = sizeof(sample_buffer),
		.resolution = 12,
		.oversampling = 4,
	};

	while (1) {
		err = adc_read(adc, &seq);
		if (err < 0) {
			printk("ADC read failed: %d\n", err);
		} else {
			printk("ADC sample: %d\n", sample_buffer[0]);
		}
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
