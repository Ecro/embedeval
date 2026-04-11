#include <zephyr/kernel.h>
#include <zephyr/drivers/dma.h>
#include <zephyr/sys/printk.h>

#define BLK 64

static uint8_t src_a[BLK] __aligned(4);
static uint8_t src_b[BLK] __aligned(4);
static uint8_t src_c[BLK] __aligned(4);
static uint8_t dst_a[BLK] __aligned(4);
static uint8_t dst_b[BLK] __aligned(4);
static uint8_t dst_c[BLK] __aligned(4);

static volatile bool done;

static void dma_cb(const struct device *dev, void *u, uint32_t ch, int status)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(u);
	ARG_UNUSED(ch);
	ARG_UNUSED(status);
	done = true;
}

int main(void)
{
	const struct device *dma = DEVICE_DT_GET(DT_NODELABEL(dma0));

	if (!device_is_ready(dma)) {
		printk("DMA not ready\n");
		return -1;
	}

	for (int i = 0; i < BLK; i++) {
		src_a[i] = (uint8_t)i;
		src_b[i] = (uint8_t)(i + 64);
		src_c[i] = (uint8_t)(i + 128);
	}

	/* Linked block descriptors — the scatter-gather list. */
	static struct dma_block_config blk_c = {
		.source_address = (uintptr_t)src_c,
		.dest_address   = (uintptr_t)dst_c,
		.block_size     = BLK,
		.next_block     = NULL,
	};
	static struct dma_block_config blk_b = {
		.source_address = (uintptr_t)src_b,
		.dest_address   = (uintptr_t)dst_b,
		.block_size     = BLK,
		.next_block     = &blk_c,
	};
	static struct dma_block_config blk_a = {
		.source_address = (uintptr_t)src_a,
		.dest_address   = (uintptr_t)dst_a,
		.block_size     = BLK,
		.next_block     = &blk_b,
	};

	struct dma_config cfg = {
		.channel_direction = MEMORY_TO_MEMORY,
		.source_data_size  = 1,
		.dest_data_size    = 1,
		.block_count       = 3,
		.head_block        = &blk_a,
		.dma_callback      = dma_cb,
	};

	if (dma_config(dma, 0, &cfg) != 0) {
		printk("dma_config failed\n");
		return -1;
	}
	if (dma_start(dma, 0) != 0) {
		printk("dma_start failed\n");
		return -1;
	}

	while (!done) {
		k_msleep(1);
	}

	printk("transfer complete\n");
	return 0;
}
