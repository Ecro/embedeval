#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/storage/flash_map.h>

static const struct mcuboot_img_sem_ver offered = {
	.major    = 2,
	.minor    = 0,
	.revision = 0,
	.build_num = 0,
};

static int version_newer(const struct mcuboot_img_sem_ver *candidate,
			  const struct mcuboot_img_sem_ver *running)
{
	if (candidate->major != running->major) {
		return candidate->major > running->major ? 1 : 0;
	}
	if (candidate->minor != running->minor) {
		return candidate->minor > running->minor ? 1 : 0;
	}
	if (candidate->revision != running->revision) {
		return candidate->revision > running->revision ? 1 : 0;
	}
	return 0; /* same version is not newer */
}

int main(void)
{
	struct mcuboot_img_header current_header;
	int ret;

	ret = boot_read_bank_header(FIXED_PARTITION_ID(slot0_partition),
				    &current_header,
				    sizeof(current_header));
	if (ret < 0) {
		printk("Failed to read bank header: %d\n", ret);
		return ret;
	}

	const struct mcuboot_img_sem_ver *running = &current_header.h1.v1.sem_ver;

	printk("Running version: %d.%d.%d\n",
	       running->major, running->minor, running->revision);

	if (version_newer(&offered, running)) {
		printk("Update accepted: %d.%d.%d -> %d.%d.%d\n",
		       running->major, running->minor, running->revision,
		       offered.major, offered.minor, offered.revision);
		printk("Proceeding with OTA\n");
	} else {
		printk("Update rejected: offered version not newer\n");
		return 0;
	}

	k_sleep(K_FOREVER);
	return 0;
}
