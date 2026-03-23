#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/pm/pm.h>

static const struct gpio_dt_spec button = GPIO_DT_SPEC_GET(DT_ALIAS(sw0), gpios);
static struct gpio_callback wake_cb_data;

static void wake_callback(const struct device *dev, struct gpio_callback *cb, uint32_t pins)
{
	printk("GPIO wake event received\n");
}

int main(void)
{
	if (!gpio_is_ready_dt(&button)) {
		return -1;
	}

	gpio_pin_configure_dt(&button, GPIO_INPUT | GPIO_PULL_UP);
	gpio_pin_interrupt_configure_dt(&button, GPIO_INT_EDGE_TO_ACTIVE);
	gpio_init_callback(&wake_cb_data, wake_callback, BIT(button.pin));
	gpio_add_callback_dt(&button, &wake_cb_data);

	printk("Entering deep sleep, press button to wake\n");

	pm_state_force(0U, &(struct pm_state_info){PM_STATE_SOFT_OFF, 0, 0});

	/* Execution resumes here after wakeup */
	printk("Woke from deep sleep\n");

	k_sleep(K_FOREVER);
	return 0;
}
