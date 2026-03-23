#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/dma.h>
#include <string.h>

#define DMA_CHANNEL 0
#define BLOCK_SIZE  16

static uint8_t src0[BLOCK_SIZE] = {0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
				   0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20};
static uint8_t src1[BLOCK_SIZE] = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28,
				   0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30};
static uint8_t src2[BLOCK_SIZE] = {0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38,
				   0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40};

static uint8_t dst0[BLOCK_SIZE];
static uint8_t dst1[BLOCK_SIZE];
static uint8_t dst2[BLOCK_SIZE];

static K_SEM_DEFINE(dma_sem, 0, 1);

static void dma_callback(const struct device *dev, void *user_data,
			  uint32_t channel, int status)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(user_data);
	ARG_UNUSED(channel);
	ARG_UNUSED(status);
	k_sem_give(&dma_sem);
}

int main(void)
{
	const struct device *const dma_dev = DEVICE_DT_GET(DT_NODELABEL(dma0));
	int ret;

	if (!device_is_ready(dma_dev)) {
		printk("DMA device not ready\n");
		return -ENODEV;
	}

	memset(dst0, 0, sizeof(dst0));
	memset(dst1, 0, sizeof(dst1));
	memset(dst2, 0, sizeof(dst2));

	struct dma_block_config block2 = {
		.source_address = (uint32_t)src2,
		.dest_address   = (uint32_t)dst2,
		.block_size     = BLOCK_SIZE,
		.next_block     = NULL,  /* Stop condition: no more blocks */
	};

	struct dma_block_config block1 = {
		.source_address = (uint32_t)src1,
		.dest_address   = (uint32_t)dst1,
		.block_size     = BLOCK_SIZE,
		.next_block     = &block2,
	};

	struct dma_block_config block0 = {
		.source_address = (uint32_t)src0,
		.dest_address   = (uint32_t)dst0,
		.block_size     = BLOCK_SIZE,
		.next_block     = &block1,
	};

	struct dma_config dma_cfg = {
		.channel_direction   = MEMORY_TO_MEMORY,
		.source_data_size    = 1,
		.dest_data_size      = 1,
		.source_burst_length = 1,
		.dest_burst_length   = 1,
		.dma_callback        = dma_callback,
		.block_count         = 3,
		.head_block          = &block0,
	};

	ret = dma_config(dma_dev, DMA_CHANNEL, &dma_cfg);
	if (ret < 0) {
		printk("DMA config failed: %d\n", ret);
		return ret;
	}

	ret = dma_start(dma_dev, DMA_CHANNEL);
	if (ret < 0) {
		printk("DMA start failed: %d\n", ret);
		return ret;
	}

	ret = k_sem_take(&dma_sem, K_SECONDS(2));
	if (ret < 0) {
		printk("DMA timed out\n");
		return ret;
	}

	if (memcmp(src0, dst0, BLOCK_SIZE) == 0 &&
	    memcmp(src1, dst1, BLOCK_SIZE) == 0 &&
	    memcmp(src2, dst2, BLOCK_SIZE) == 0) {
		printk("Multi-block DMA OK\n");
	} else {
		printk("Multi-block DMA FAILED\n");
		return -EIO;
	}

	return 0;
}
