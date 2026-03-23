#include <zephyr/kernel.h>
#include <zephyr/sys/util.h>
#include <stddef.h>

#define MIN_BUF_SIZE   64U
#define MAX_BUF_SIZE   256U
#define MAX_STRUCT_SIZE 128U

/* Protocol buffer — must be at least MIN_BUF_SIZE */
static uint8_t proto_buf[128];

/* DMA descriptor struct — must fit in hardware limit */
struct dma_desc {
	uint32_t src_addr;
	uint32_t dst_addr;
	uint32_t length;
	uint32_t flags;
	uint8_t  reserved[16];
};

/* Compile-time buffer size validations */
BUILD_ASSERT(sizeof(proto_buf) >= MIN_BUF_SIZE,
	     "proto_buf too small for protocol minimum");

BUILD_ASSERT(sizeof(proto_buf) <= MAX_BUF_SIZE,
	     "proto_buf exceeds maximum allowed size");

BUILD_ASSERT(sizeof(struct dma_desc) <= MAX_STRUCT_SIZE,
	     "dma_desc struct exceeds DMA hardware limit");

BUILD_ASSERT(offsetof(struct dma_desc, src_addr) % 4 == 0,
	     "dma_desc.src_addr must be 4-byte aligned");

BUILD_ASSERT(offsetof(struct dma_desc, dst_addr) % 4 == 0,
	     "dma_desc.dst_addr must be 4-byte aligned");

int main(void)
{
	printk("proto_buf size:    %zu bytes (min=%u, max=%u)\n",
	       sizeof(proto_buf), MIN_BUF_SIZE, MAX_BUF_SIZE);
	printk("dma_desc size:     %zu bytes (max=%u)\n",
	       sizeof(struct dma_desc), MAX_STRUCT_SIZE);
	printk("src_addr offset:   %zu (alignment check passed)\n",
	       offsetof(struct dma_desc, src_addr));
	printk("All compile-time assertions passed\n");

	return 0;
}
