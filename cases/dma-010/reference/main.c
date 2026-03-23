#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/dma.h>

#define DMA_CHANNEL  0
#define BUF_SIZE     64
#define ITERATIONS   3

static uint8_t buf_a[BUF_SIZE];
static uint8_t buf_b[BUF_SIZE];

static uint8_t *const dma_bufs[2] = {buf_a, buf_b};

static atomic_t active_buf_idx = ATOMIC_INIT(0);
static K_SEM_DEFINE(process_sem, 0, 1);

static const struct device *dma_dev_global;

static void dma_callback(const struct device *dev, void *user_data,
			  uint32_t channel, int status)
{
	ARG_UNUSED(user_data);
	ARG_UNUSED(status);

	/* Swap: the buffer DMA just filled is no longer "active DMA target" */
	atomic_val_t current = atomic_get(&active_buf_idx);
	atomic_val_t next = 1 - current;

	atomic_set(&active_buf_idx, next);

	/* Reload DMA to fill the other buffer (the new active one) */
	dma_reload(dev, channel,
		   (uint32_t)dma_bufs[next],
		   (uint32_t)dma_bufs[next],
		   BUF_SIZE);

	/* Signal CPU to process the buffer DMA just finished */
	k_sem_give(&process_sem);
}

int main(void)
{
	dma_dev_global = DEVICE_DT_GET(DT_NODELABEL(dma0));
	int ret;

	if (!device_is_ready(dma_dev_global)) {
		printk("DMA device not ready\n");
		return -ENODEV;
	}

	struct dma_block_config block_cfg = {
		.source_address = (uint32_t)buf_a,
		.dest_address   = (uint32_t)buf_a,
		.block_size     = BUF_SIZE,
	};

	struct dma_config dma_cfg = {
		.channel_direction   = MEMORY_TO_MEMORY,
		.source_data_size    = 1,
		.dest_data_size      = 1,
		.source_burst_length = 1,
		.dest_burst_length   = 1,
		.dma_callback        = dma_callback,
		.block_count         = 1,
		.head_block          = &block_cfg,
	};

	ret = dma_config(dma_dev_global, DMA_CHANNEL, &dma_cfg);
	if (ret < 0) {
		printk("DMA config failed: %d\n", ret);
		return ret;
	}

	ret = dma_start(dma_dev_global, DMA_CHANNEL);
	if (ret < 0) {
		printk("DMA start failed: %d\n", ret);
		return ret;
	}

	for (int iter = 0; iter < ITERATIONS; iter++) {
		ret = k_sem_take(&process_sem, K_SECONDS(1));
		if (ret < 0) {
			printk("DMA timeout on iteration %d\n", iter);
			return ret;
		}

		/* CPU processes the buffer DMA just completed (NOT active_buf_idx) */
		atomic_val_t fill_idx = atomic_get(&active_buf_idx);
		atomic_val_t process_idx = 1 - fill_idx;
		uint8_t *process_buf = dma_bufs[process_idx];

		/* Zero-copy: read directly from DMA buffer, no memcpy */
		printk("Iter %d: buf[%d] first byte=0x%02x\n",
		       iter, (int)process_idx, process_buf[0]);
	}

	printk("Double-buffer DMA OK\n");
	return 0;
}
