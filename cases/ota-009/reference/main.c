#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/storage/flash_map.h>

static const char *swap_type_str(int swap_type)
{
	switch (swap_type) {
	case BOOT_SWAP_TYPE_NONE:   return "No swap pending";
	case BOOT_SWAP_TYPE_TEST:   return "Test swap pending";
	case BOOT_SWAP_TYPE_PERM:   return "Permanent swap pending";
	case BOOT_SWAP_TYPE_REVERT: return "Revert swap pending";
	default:                    return "Unknown swap type";
	}
}

static void print_slot_info(const char *slot_name, uint8_t slot_id)
{
	struct mcuboot_img_header header;
	int ret;

	ret = boot_read_bank_header(slot_id, &header, sizeof(header));
	if (ret != 0) {
		printk("%s: empty or unreadable (ret=%d)\n", slot_name, ret);
		return;
	}

	printk("%s: version %u.%u.%u+%u, image size %u bytes\n",
	       slot_name,
	       header.h.v1.sem_ver.major,
	       header.h.v1.sem_ver.minor,
	       header.h.v1.sem_ver.revision,
	       header.h.v1.sem_ver.build_num,
	       header.h.v1.image_size);
}

int main(void)
{
	int swap_type;

	printk("MCUboot slot status query\n");

	swap_type = mcuboot_swap_type();
	printk("Swap type: %s\n", swap_type_str(swap_type));

	print_slot_info("Primary slot (slot0)", FIXED_PARTITION_ID(slot0_partition));
	print_slot_info("Secondary slot (slot1)", FIXED_PARTITION_ID(slot1_partition));

	printk("Current image confirmed: %s\n",
	       boot_is_img_confirmed() ? "yes" : "no");

	k_sleep(K_FOREVER);
	return 0;
}
