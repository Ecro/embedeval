#include <zephyr/kernel.h>
#include <string.h>

#define BLOCK_SIZE 64
#define NUM_BLOCKS 4

K_MEM_SLAB_DEFINE(my_slab, BLOCK_SIZE, NUM_BLOCKS, 4);

int main(void)
{
	void *block;
	int ret;

	ret = k_mem_slab_alloc(&my_slab, &block, K_NO_WAIT);
	if (ret < 0) {
		printk("Slab alloc failed: %d\n", ret);
		return ret;
	}

	memset(block, 0xAA, BLOCK_SIZE);
	printk("Allocated block at %p\n", block);
	printk("Used blocks: %u\n", k_mem_slab_num_used_get(&my_slab));

	k_mem_slab_free(&my_slab, block);
	printk("Freed block, used: %u\n", k_mem_slab_num_used_get(&my_slab));

	return 0;
}
