#include <zephyr/kernel.h>
#include <zephyr/drivers/adc.h>

static const struct adc_dt_spec adc_channel =
	ADC_DT_SPEC_GET(DT_PATH(zephyr_user));

int main(void)
{
	int err;

	if (!adc_is_ready_dt(&adc_channel)) {
		return -1;
	}

	err = adc_channel_setup_dt(&adc_channel);
	if (err < 0) {
		return err;
	}

	int16_t buf;
	struct adc_sequence sequence = {
		.buffer      = &buf,
		.buffer_size = sizeof(buf),
	};

	err = adc_sequence_init_dt(&adc_channel, &sequence);
	if (err < 0) {
		return err;
	}

	while (1) {
		err = adc_read_dt(&adc_channel, &sequence);
		if (err < 0) {
			printk("ADC read error: %d\n", err);
			k_sleep(K_MSEC(1000));
			continue;
		}

		int32_t val_mv = buf;

		err = adc_raw_to_millivolts_dt(&adc_channel, &val_mv);
		if (err < 0) {
			printk("Conversion error: %d\n", err);
		} else {
			printk("ADC value: %d mV\n", val_mv);
		}

		k_sleep(K_MSEC(1000));
	}

	return 0;
}
