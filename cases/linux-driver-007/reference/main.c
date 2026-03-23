#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/dma-mapping.h>
#include <linux/slab.h>

#define DRIVER_NAME "dmabuf_drv"
#define DMA_BUF_SIZE 4096

struct dmabuf_dev {
	void *virt_addr;
	dma_addr_t dma_handle;
	size_t size;
};

static int dmabuf_probe(struct platform_device *pdev)
{
	struct dmabuf_dev *dev;

	dev = devm_kzalloc(&pdev->dev, sizeof(*dev), GFP_KERNEL);
	if (!dev)
		return -ENOMEM;

	dev->size = DMA_BUF_SIZE;
	dev->virt_addr = dma_alloc_coherent(&pdev->dev, dev->size,
					    &dev->dma_handle, GFP_KERNEL);
	if (!dev->virt_addr) {
		pr_err("%s: dma_alloc_coherent failed\n", DRIVER_NAME);
		return -ENOMEM;
	}

	dev_set_drvdata(&pdev->dev, dev);
	pr_info("%s: DMA buffer at phys=0x%llx virt=%p size=%zu\n",
		DRIVER_NAME, (unsigned long long)dev->dma_handle,
		dev->virt_addr, dev->size);
	return 0;
}

static int dmabuf_remove(struct platform_device *pdev)
{
	struct dmabuf_dev *dev = dev_get_drvdata(&pdev->dev);

	if (dev && dev->virt_addr)
		dma_free_coherent(&pdev->dev, dev->size, dev->virt_addr,
				  dev->dma_handle);

	pr_info("%s: DMA buffer freed\n", DRIVER_NAME);
	return 0;
}

static struct platform_driver dmabuf_driver = {
	.probe  = dmabuf_probe,
	.remove = dmabuf_remove,
	.driver = {
		.name  = DRIVER_NAME,
		.owner = THIS_MODULE,
	},
};

static int __init dmabuf_init(void)
{
	return platform_driver_register(&dmabuf_driver);
}

static void __exit dmabuf_exit(void)
{
	platform_driver_unregister(&dmabuf_driver);
}

module_init(dmabuf_init);
module_exit(dmabuf_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("DMA-coherent buffer allocation example");
