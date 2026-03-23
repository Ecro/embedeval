#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>

static const struct gpio_dt_spec leds[] = {
	GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios),
	GPIO_DT_SPEC_GET(DT_ALIAS(led1), gpios),
	GPIO_DT_SPEC_GET(DT_ALIAS(led2), gpios),
	GPIO_DT_SPEC_GET(DT_ALIAS(led3), gpios),
};

#define NUM_LEDS ARRAY_SIZE(leds)

int main(void)
{
	for (int i = 0; i < NUM_LEDS; i++) {
		if (!gpio_is_ready_dt(&leds[i])) {
			return -1;
		}
	}

	for (int i = 0; i < NUM_LEDS; i++) {
		gpio_pin_configure_dt(&leds[i], GPIO_OUTPUT_INACTIVE);
	}

	while (1) {
		for (int i = 0; i < NUM_LEDS; i++) {
			gpio_pin_set_dt(&leds[i], 1);
			k_sleep(K_MSEC(200));
			gpio_pin_set_dt(&leds[i], 0);
		}
	}

	return 0;
}
