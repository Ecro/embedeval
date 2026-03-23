#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/dma.h>
#include <string.h>

#define DMA_CHANNEL  0
#define BLOCK_SIZE   16
#define NUM_BLOCKS   3
#define TOTAL_SIZE   (BLOCK_SIZE * NUM_BLOCKS)

static uint8_t src0[BLOCK_SIZE];
static uint8_t src1[BLOCK_SIZE];
static uint8_t src2[BLOCK_SIZE];
static uint8_t dst[TOTAL_SIZE];
static K_SEM_DEFINE(dma_sem, 0, 1);

static void dma_callback(const struct device *dev, void *user_data,
			  uint32_t channel, int status)
{
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

	memset(src0, 0xAA, sizeof(src0));
	memset(src1, 0xBB, sizeof(src1));
	memset(src2, 0xCC, sizeof(src2));
	memset(dst, 0, sizeof(dst));

	struct dma_block_config block2 = {
		.source_address = (uint32_t)src2,
		.dest_address = (uint32_t)(dst + BLOCK_SIZE * 2),
		.block_size = BLOCK_SIZE,
		.next_block = NULL,
	};

	struct dma_block_config block1 = {
		.source_address = (uint32_t)src1,
		.dest_address = (uint32_t)(dst + BLOCK_SIZE),
		.block_size = BLOCK_SIZE,
		.next_block = &block2,
	};

	struct dma_block_config block0 = {
		.source_address = (uint32_t)src0,
		.dest_address = (uint32_t)dst,
		.block_size = BLOCK_SIZE,
		.next_block = &block1,
	};

	struct dma_config dma_cfg = {
		.channel_direction = MEMORY_TO_MEMORY,
		.source_data_size = 1,
		.dest_data_size = 1,
		.source_burst_length = 1,
		.dest_burst_length = 1,
		.dma_callback = dma_callback,
		.block_count = NUM_BLOCKS,
		.head_block = &block0,
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

	ret = k_sem_take(&dma_sem, K_SECONDS(1));
	if (ret < 0) {
		printk("DMA scatter-gather timed out\n");
		return ret;
	}

	/* Verify each segment */
	bool ok = true;

	for (int i = 0; i < BLOCK_SIZE; i++) {
		if (dst[i] != 0xAA) {
			ok = false;
			break;
		}
	}
	for (int i = BLOCK_SIZE; i < BLOCK_SIZE * 2; i++) {
		if (dst[i] != 0xBB) {
			ok = false;
			break;
		}
	}
	for (int i = BLOCK_SIZE * 2; i < TOTAL_SIZE; i++) {
		if (dst[i] != 0xCC) {
			ok = false;
			break;
		}
	}

	if (ok) {
		printk("Scatter-gather OK\n");
	} else {
		printk("Scatter-gather FAILED\n");
		return -EIO;
	}

	return 0;
}
