#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/mod_devicetable.h>

static int mydev_probe(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "mydevice: probe called\n");
	return 0;
}

static int mydev_remove(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "mydevice: remove called\n");
	return 0;
}

static const struct of_device_id mydev_of_match[] = {
	{ .compatible = "vendor,mydevice" },
	{},
};
MODULE_DEVICE_TABLE(of, mydev_of_match);

static struct platform_driver mydev_driver = {
	.probe  = mydev_probe,
	.remove = mydev_remove,
	.driver = {
		.name           = "mydevice",
		.of_match_table = mydev_of_match,
	},
};
module_platform_driver(mydev_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("Platform driver with Device Tree binding");
