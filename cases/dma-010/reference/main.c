#include <zephyr/kernel.h>
#include <zephyr/drivers/dma.h>
#include <zephyr/cache.h>
#include <zephyr/sys/printk.h>

#define BUF_SIZE 256

static uint8_t src_buf[BUF_SIZE] __aligned(32);
static uint8_t dst_buf[BUF_SIZE] __aligned(32);

static volatile bool dma_done;

static void dma_cb(const struct device *dev, void *user_data,
		   uint32_t channel, int status)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(user_data);
	ARG_UNUSED(channel);
	ARG_UNUSED(status);
	dma_done = true;
}

int main(void)
{
	const struct device *dma_dev = DEVICE_DT_GET(DT_NODELABEL(dma0));

	if (!device_is_ready(dma_dev)) {
		printk("DMA device not ready\n");
		return -1;
	}

	for (size_t i = 0; i < BUF_SIZE; i++) {
		src_buf[i] = (uint8_t)(i & 0xFF);
	}

	/* Flush CPU cache so the DMA engine observes the bytes the CPU wrote. */
	sys_cache_data_flush_range(src_buf, BUF_SIZE);
	/* Invalidate dest cache so post-DMA CPU reads don't return stale cached lines. */
	sys_cache_data_invd_range(dst_buf, BUF_SIZE);

	struct dma_block_config block = {
		.source_address  = (uintptr_t)src_buf,
		.dest_address    = (uintptr_t)dst_buf,
		.block_size      = BUF_SIZE,
	};

	struct dma_config cfg = {
		.channel_direction = MEMORY_TO_MEMORY,
		.source_data_size  = 1,
		.dest_data_size    = 1,
		.block_count       = 1,
		.head_block        = &block,
		.dma_callback      = dma_cb,
	};

	if (dma_config(dma_dev, 0, &cfg) != 0) {
		printk("dma_config failed\n");
		return -1;
	}

	if (dma_start(dma_dev, 0) != 0) {
		printk("dma_start failed\n");
		return -1;
	}

	while (!dma_done) {
		k_msleep(1);
	}

	printk("dma done\n");
	return 0;
}
