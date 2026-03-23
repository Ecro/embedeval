#include <zephyr/kernel.h>
#include <zephyr/random/random.h>

#define RANDOM_BUF_SIZE 32

int main(void)
{
	uint8_t buf[RANDOM_BUF_SIZE];
	int ret;

	/* sys_csrand_get is cryptographically secure (uses entropy driver).
	 * Never use rand()/srand() or sys_rand_get() for security-sensitive use.
	 */
	ret = sys_csrand_get(buf, sizeof(buf));
	if (ret < 0) {
		printk("RNG FAILED: %d\n", ret);
		return ret;
	}

	printk("RNG OK: %02x%02x%02x%02x...\n",
	       buf[0], buf[1], buf[2], buf[3]);

	return 0;
}
