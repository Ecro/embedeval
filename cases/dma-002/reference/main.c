#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/dma.h>

#define DMA_CHANNEL      0
#define PERIPH_ADDR      0x40012400U
#define TRANSFER_SIZE    32

static uint8_t dst_buf[TRANSFER_SIZE];
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

	memset(dst_buf, 0, sizeof(dst_buf));

	struct dma_block_config block_cfg = {
		.source_address = PERIPH_ADDR,
		.dest_address = (uint32_t)dst_buf,
		.block_size = TRANSFER_SIZE,
		.source_addr_adj = DMA_ADDR_ADJ_NO_CHANGE,
		.dest_addr_adj = DMA_ADDR_ADJ_INCREMENT,
	};

	struct dma_config dma_cfg = {
		.channel_direction = PERIPHERAL_TO_MEMORY,
		.source_data_size = 2,
		.dest_data_size = 2,
		.source_burst_length = 1,
		.dest_burst_length = 1,
		.dma_callback = dma_callback,
		.block_count = 1,
		.head_block = &block_cfg,
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
		printk("Peripheral DMA transfer timed out\n");
		return ret;
	}

	printk("Peripheral DMA transfer complete\n");

	return 0;
}
