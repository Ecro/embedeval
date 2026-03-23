#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>

static const struct gpio_dt_spec led = GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios);
static const struct gpio_dt_spec button = GPIO_DT_SPEC_GET(DT_ALIAS(sw0), gpios);
static struct gpio_callback button_cb_data;

K_TIMER_DEFINE(debounce_timer, NULL, NULL);

static void debounce_expiry(struct k_timer *timer)
{
	int val = gpio_pin_get_dt(&button);

	if (val > 0) {
		gpio_pin_toggle_dt(&led);
	}
}

K_TIMER_DEFINE(debounce_tmr, debounce_expiry, NULL);

static void button_isr(const struct device *dev, struct gpio_callback *cb, uint32_t pins)
{
	k_timer_start(&debounce_tmr, K_MSEC(50), K_NO_WAIT);
}

int main(void)
{
	if (!gpio_is_ready_dt(&led) || !gpio_is_ready_dt(&button)) {
		return -1;
	}

	gpio_pin_configure_dt(&led, GPIO_OUTPUT_INACTIVE);
	gpio_pin_configure_dt(&button, GPIO_INPUT | GPIO_PULL_UP);
	gpio_pin_interrupt_configure_dt(&button, GPIO_INT_EDGE_BOTH);
	gpio_init_callback(&button_cb_data, button_isr, BIT(button.pin));
	gpio_add_callback_dt(&button, &button_cb_data);

	k_sleep(K_FOREVER);
	return 0;
}
