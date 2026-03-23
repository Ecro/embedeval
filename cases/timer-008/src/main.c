#include <zephyr/kernel.h>

int main(void)
{
	for (int i = 0; i < 10; i++) {
		uint32_t start = k_cycle_get_32();

		/* Dummy workload */
		volatile int dummy = 0;

		for (int j = 0; j < 100; j++) {
			dummy++;
		}

		uint32_t end = k_cycle_get_32();
		uint32_t elapsed_cycles = end - start;
		uint64_t elapsed_ns = k_cyc_to_ns_floor64(elapsed_cycles);

		printk("Cycles: %u, NS: %llu\n", elapsed_cycles, elapsed_ns);
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
