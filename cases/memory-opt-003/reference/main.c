#include <zephyr/kernel.h>
#include <string.h>

/* K_HEAP_DEFINE: for variable-size allocations (e.g., 50 bytes, then 120 bytes) */
K_HEAP_DEFINE(my_heap, 1024);

/* K_MEM_SLAB_DEFINE: for fixed-size allocations (e.g., always 32-byte blocks) */
K_MEM_SLAB_DEFINE(my_slab, 32, 8, 4);

int main(void)
{
	void *ptr;
	void *block;
	int ret;

	/* --- Variable-size allocation: use heap --- */
	printk("Heap demo: allocating 100 bytes (variable size -> use heap)\n");
	ptr = k_heap_alloc(&my_heap, 100, K_NO_WAIT);
	if (!ptr) {
		printk("Heap alloc failed\n");
		return -ENOMEM;
	}
	memset(ptr, 0xBB, 100);
	printk("Heap alloc at %p\n", ptr);
	k_heap_free(&my_heap, ptr);
	printk("Heap freed\n");

	/* --- Fixed-size allocation: use slab --- */
	printk("Slab demo: allocating 32-byte block (fixed size -> use slab)\n");
	ret = k_mem_slab_alloc(&my_slab, &block, K_NO_WAIT);
	if (ret < 0) {
		printk("Slab alloc failed: %d\n", ret);
		return ret;
	}
	memset(block, 0xCC, 32);
	printk("Slab block at %p, used=%u\n", block,
	       k_mem_slab_num_used_get(&my_slab));
	k_mem_slab_free(&my_slab, block);
	printk("Slab freed, used=%u\n", k_mem_slab_num_used_get(&my_slab));

	return 0;
}
