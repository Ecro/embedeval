#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>

int main(void)
{
	int swap_type = mcuboot_swap_type();

	switch (swap_type) {
	case BOOT_SWAP_TYPE_NONE:
		printk("Swap type: NONE\n");
		break;
	case BOOT_SWAP_TYPE_TEST:
		printk("Swap type: TEST\n");
		break;
	case BOOT_SWAP_TYPE_PERM:
		printk("Swap type: PERM\n");
		break;
	case BOOT_SWAP_TYPE_REVERT:
		printk("Swap type: REVERT\n");
		break;
	default:
		printk("Swap type: UNKNOWN (%d)\n", swap_type);
		break;
	}

	printk("Boot status check complete\n");
	k_sleep(K_FOREVER);
	return 0;
}
