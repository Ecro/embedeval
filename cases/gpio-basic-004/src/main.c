#include <zephyr/kernel.h>
#include <zephyr/drivers/pwm.h>

static const struct pwm_dt_spec pwm_led = PWM_DT_SPEC_GET(DT_ALIAS(pwm_led0));

#define PWM_PERIOD_NS  20000000U
#define PWM_STEP_NS     2000000U

int main(void)
{
	if (!pwm_is_ready_dt(&pwm_led)) {
		return -1;
	}

	uint32_t duty = 0U;
	int dir = 1;

	while (1) {
		pwm_set_dt(&pwm_led, PWM_PERIOD_NS, duty);

		duty += dir * PWM_STEP_NS;

		if (duty >= PWM_PERIOD_NS) {
			duty = PWM_PERIOD_NS;
			dir = -1;
		} else if (duty == 0U || (int32_t)duty < 0) {
			duty = 0U;
			dir = 1;
		}

		k_sleep(K_MSEC(50));
	}

	return 0;
}
