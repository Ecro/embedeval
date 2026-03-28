#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/dma.h>
#include <string.h>

#define DMA_CHANNEL    0
#define TRANSFER_SIZE  256
#define TIMEOUT_MS     500
#define MAX_RETRIES    3

static uint8_t src_buf[TRANSFER_SIZE];
static uint8_t dst_buf[TRANSFER_SIZE];

static K_SEM_DEFINE(dma_done_sem, 0, 1);

static volatile int dma_callback_status;

static int completion_count;
static int timeout_count;
static int abort_count;

static struct dma_config dma_cfg;
static struct dma_block_config block_cfg;

static void dma_callback(const struct device *dev, void *user_data,
			  uint32_t channel, int status)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(user_data);
	ARG_UNUSED(channel);

	dma_callback_status = status;
	k_sem_give(&dma_done_sem);
}

static void setup_dma_config(void)
{
	memset(&block_cfg, 0, sizeof(block_cfg));
	block_cfg.source_address = (uint32_t)src_buf;
	block_cfg.dest_address = (uint32_t)dst_buf;
	block_cfg.block_size = TRANSFER_SIZE;
	block_cfg.next_block = NULL;

	memset(&dma_cfg, 0, sizeof(dma_cfg));
	dma_cfg.channel_direction = MEMORY_TO_MEMORY;
	dma_cfg.source_data_size = 1;
	dma_cfg.dest_data_size = 1;
	dma_cfg.source_burst_length = 1;
	dma_cfg.dest_burst_length = 1;
	dma_cfg.dma_callback = dma_callback;
	dma_cfg.block_count = 1;
	dma_cfg.head_block = &block_cfg;
}

int main(void)
{
	const struct device *const dma_dev = DEVICE_DT_GET(DT_NODELABEL(dma0));
	int ret;
	int attempt;

	if (!device_is_ready(dma_dev)) {
		printk("DMA device not ready\n");
		return -ENODEV;
	}

	/* Initialize source buffer with test pattern */
	for (int i = 0; i < TRANSFER_SIZE; i++) {
		src_buf[i] = (uint8_t)(i & 0xFF);
	}

	for (attempt = 0; attempt < MAX_RETRIES; attempt++) {
		printk("DMA transfer attempt %d...\n", attempt + 1);

		/* Clear destination and configure */
		memset(dst_buf, 0, TRANSFER_SIZE);
		setup_dma_config();

		ret = dma_config(dma_dev, DMA_CHANNEL, &dma_cfg);
		if (ret < 0) {
			printk("DMA config failed: %d\n", ret);
			return ret;
		}

		/* Reset semaphore and start transfer */
		k_sem_reset(&dma_done_sem);
		dma_callback_status = 0;

		ret = dma_start(dma_dev, DMA_CHANNEL);
		if (ret < 0) {
			printk("DMA start failed: %d\n", ret);
			return ret;
		}

		/* Wait for completion with timeout */
		ret = k_sem_take(&dma_done_sem, K_MSEC(TIMEOUT_MS));
		if (ret == -EAGAIN) {
			/* Timeout — abort the transfer */
			printk("DMA transfer timed out, aborting...\n");
			timeout_count++;

			ret = dma_stop(dma_dev, DMA_CHANNEL);
			if (ret < 0) {
				printk("DMA stop failed: %d\n", ret);
				return ret;
			}
			abort_count++;
			printk("DMA channel stopped, will reconfigure and retry\n");

			/* Reconfigure: dma_config will be called at top of next iteration */
			continue;
		}

		/* Check callback status */
		if (dma_callback_status != 0) {
			printk("DMA callback error: %d\n", dma_callback_status);
			continue;
		}

		/* Verify transfer */
		if (memcmp(src_buf, dst_buf, TRANSFER_SIZE) != 0) {
			printk("DMA data verification failed\n");
			continue;
		}

		completion_count++;
		printk("DMA transfer %d completed successfully\n", attempt + 1);
	}

	/* Do one more transfer to demonstrate channel reuse after successful completion */
	printk("Final DMA transfer for channel reuse verification...\n");
	memset(dst_buf, 0, TRANSFER_SIZE);
	setup_dma_config();

	ret = dma_config(dma_dev, DMA_CHANNEL, &dma_cfg);
	if (ret < 0) {
		printk("Final DMA config failed: %d\n", ret);
	} else {
		k_sem_reset(&dma_done_sem);
		dma_callback_status = 0;

		ret = dma_start(dma_dev, DMA_CHANNEL);
		if (ret == 0) {
			ret = k_sem_take(&dma_done_sem, K_MSEC(TIMEOUT_MS));
			if (ret == 0 && dma_callback_status == 0) {
				completion_count++;
				printk("Final transfer OK\n");
			}
		}
	}

	/* Print final statistics */
	printk("=== DMA Transfer Statistics ===\n");
	printk("Completions: %d\n", completion_count);
	printk("Timeouts:    %d\n", timeout_count);
	printk("Aborts:      %d\n", abort_count);

	return 0;
}
