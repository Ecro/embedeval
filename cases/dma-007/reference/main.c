#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/dma.h>
#include <string.h>

#define CH_HIGH  0
#define CH_LOW   1
#define BUF_SIZE 32

static uint8_t src_hi[BUF_SIZE];
static uint8_t dst_hi[BUF_SIZE];
static uint8_t src_lo[BUF_SIZE];
static uint8_t dst_lo[BUF_SIZE];

static K_SEM_DEFINE(sem_hi, 0, 1);
static K_SEM_DEFINE(sem_lo, 0, 1);

static void cb_hi(const struct device *dev, void *user_data,
		  uint32_t channel, int status)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(user_data);
	ARG_UNUSED(channel);
	ARG_UNUSED(status);
	printk("High priority channel done\n");
	k_sem_give(&sem_hi);
}

static void cb_lo(const struct device *dev, void *user_data,
		  uint32_t channel, int status)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(user_data);
	ARG_UNUSED(channel);
	ARG_UNUSED(status);
	printk("Low priority channel done\n");
	k_sem_give(&sem_lo);
}

int main(void)
{
	const struct device *const dma_dev = DEVICE_DT_GET(DT_NODELABEL(dma0));
	int ret;

	if (!device_is_ready(dma_dev)) {
		printk("DMA device not ready\n");
		return -ENODEV;
	}

	for (int i = 0; i < BUF_SIZE; i++) {
		src_hi[i] = (uint8_t)(0xAA + i);
		src_lo[i] = (uint8_t)(0x55 + i);
	}
	memset(dst_hi, 0, sizeof(dst_hi));
	memset(dst_lo, 0, sizeof(dst_lo));

	struct dma_block_config blk_hi = {
		.source_address = (uint32_t)src_hi,
		.dest_address   = (uint32_t)dst_hi,
		.block_size     = BUF_SIZE,
	};
	struct dma_config cfg_hi = {
		.channel_direction = MEMORY_TO_MEMORY,
		.channel_priority  = 0,
		.source_data_size  = 1,
		.dest_data_size    = 1,
		.source_burst_length = 1,
		.dest_burst_length   = 1,
		.dma_callback        = cb_hi,
		.block_count         = 1,
		.head_block          = &blk_hi,
	};

	struct dma_block_config blk_lo = {
		.source_address = (uint32_t)src_lo,
		.dest_address   = (uint32_t)dst_lo,
		.block_size     = BUF_SIZE,
	};
	struct dma_config cfg_lo = {
		.channel_direction = MEMORY_TO_MEMORY,
		.channel_priority  = 1,
		.source_data_size  = 1,
		.dest_data_size    = 1,
		.source_burst_length = 1,
		.dest_burst_length   = 1,
		.dma_callback        = cb_lo,
		.block_count         = 1,
		.head_block          = &blk_lo,
	};

	ret = dma_config(dma_dev, CH_HIGH, &cfg_hi);
	if (ret < 0) {
		printk("DMA config CH_HIGH failed: %d\n", ret);
		return ret;
	}

	ret = dma_config(dma_dev, CH_LOW, &cfg_lo);
	if (ret < 0) {
		printk("DMA config CH_LOW failed: %d\n", ret);
		return ret;
	}

	dma_start(dma_dev, CH_HIGH);
	dma_start(dma_dev, CH_LOW);

	k_sem_take(&sem_hi, K_SECONDS(1));
	k_sem_take(&sem_lo, K_SECONDS(1));

	if (memcmp(src_hi, dst_hi, BUF_SIZE) == 0 &&
	    memcmp(src_lo, dst_lo, BUF_SIZE) == 0) {
		printk("Both DMA channels verified OK\n");
	} else {
		printk("DMA verify FAILED\n");
		return -EIO;
	}

	return 0;
}
