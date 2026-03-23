#include <zephyr/kernel.h>
#include <zephyr/sys/util.h>
#include <string.h>

/*
 * DMA buffer placed in dedicated .dma_buf section.
 * The linker script maps this section to DMA-accessible RAM.
 * Cache-line aligned (32 bytes) for proper DMA operation.
 */
static uint8_t dma_buf[1024]
	__attribute__((section(".dma_buf"), aligned(32)));

/*
 * Fast scratch buffer in .noinit section — not zero-initialized at startup.
 * Placed in fast SRAM for performance-critical operations.
 */
static uint8_t fast_buf[512]
	__attribute__((section(".noinit")));

/* Regular buffer for comparison — goes in .bss (default) */
static uint8_t normal_buf[256];

int main(void)
{
	printk("Buffer section placement demo\n");
	printk("dma_buf   @ %p (size=%zu, section=.dma_buf)\n",
	       (void *)dma_buf, sizeof(dma_buf));
	printk("fast_buf  @ %p (size=%zu, section=.noinit)\n",
	       (void *)fast_buf, sizeof(fast_buf));
	printk("normal_buf@ %p (size=%zu, section=.bss)\n",
	       (void *)normal_buf, sizeof(normal_buf));

	/* Use the DMA buffer */
	memset(dma_buf, 0xAA, sizeof(dma_buf));
	printk("dma_buf[0]=0x%02x dma_buf[1023]=0x%02x\n",
	       dma_buf[0], dma_buf[1023]);

	return 0;
}
