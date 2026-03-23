#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/dma.h>

#define DMA_CHANNEL    0
#define BUF_SIZE       32
#define NUM_TRANSFERS  4

static uint8_t src_buf[BUF_SIZE];
static uint8_t buf_a[BUF_SIZE];
static uint8_t buf_b[BUF_SIZE];
static uint8_t *ping_pong[2] = {buf_a, buf_b};
static volatile int current_buf;
static volatile int transfer_count;
static K_SEM_DEFINE(dma_sem, 0, 1);

static const struct device *dma_dev_ptr;

static void dma_callback(const struct device *dev, void *user_data,
			  uint32_t channel, int status)
{
	transfer_count++;
	int next = (current_buf + 1) % 2;

	dma_reload(dev, channel,
		   (uint32_t)src_buf,
		   (uint32_t)ping_pong[next],
		   BUF_SIZE);

	current_buf = next;
	k_sem_give(&dma_sem);
}

int main(void)
{
	dma_dev_ptr = DEVICE_DT_GET(DT_NODELABEL(dma0));
	int ret;

	if (!device_is_ready(dma_dev_ptr)) {
		printk("DMA device not ready\n");
		return -ENODEV;
	}

	for (int i = 0; i < BUF_SIZE; i++) {
		src_buf[i] = (uint8_t)i;
	}
	memset(buf_a, 0, sizeof(buf_a));
	memset(buf_b, 0, sizeof(buf_b));
	current_buf = 0;
	transfer_count = 0;

	struct dma_block_config block_cfg = {
		.source_address = (uint32_t)src_buf,
		.dest_address = (uint32_t)buf_a,
		.block_size = BUF_SIZE,
		.cyclic = 1,
	};

	struct dma_config dma_cfg = {
		.channel_direction = MEMORY_TO_MEMORY,
		.source_data_size = 1,
		.dest_data_size = 1,
		.source_burst_length = 1,
		.dest_burst_length = 1,
		.dma_callback = dma_callback,
		.block_count = 1,
		.head_block = &block_cfg,
	};

	ret = dma_config(dma_dev_ptr, DMA_CHANNEL, &dma_cfg);
	if (ret < 0) {
		printk("DMA config failed: %d\n", ret);
		return ret;
	}

	ret = dma_start(dma_dev_ptr, DMA_CHANNEL);
	if (ret < 0) {
		printk("DMA start failed: %d\n", ret);
		return ret;
	}

	for (int i = 0; i < NUM_TRANSFERS; i++) {
		ret = k_sem_take(&dma_sem, K_SECONDS(1));
		if (ret < 0) {
			printk("DMA transfer %d timed out\n", i);
			dma_stop(dma_dev_ptr, DMA_CHANNEL);
			return ret;
		}
	}

	dma_stop(dma_dev_ptr, DMA_CHANNEL);
	printk("Circular DMA complete: %d transfers\n", transfer_count);

	return 0;
}
