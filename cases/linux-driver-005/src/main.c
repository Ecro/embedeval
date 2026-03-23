#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/device.h>
#include <linux/sysfs.h>
#include <linux/string.h>

static int myvalue = 42;

static ssize_t myvalue_show(struct device *dev,
			    struct device_attribute *attr,
			    char *buf)
{
	return sysfs_emit(buf, "%d\n", myvalue);
}

static ssize_t myvalue_store(struct device *dev,
			     struct device_attribute *attr,
			     const char *buf, size_t count)
{
	int val;
	int ret;

	ret = kstrtoint(buf, 10, &val);
	if (ret)
		return -EINVAL;

	myvalue = val;
	return count;
}

static DEVICE_ATTR_RW(myvalue);

static struct attribute *mydev_attrs[] = {
	&dev_attr_myvalue.attr,
	NULL,
};

static const struct attribute_group mydev_attr_group = {
	.attrs = mydev_attrs,
};

static int mydev_probe(struct platform_device *pdev)
{
	int ret;

	ret = sysfs_create_group(&pdev->dev.kobj, &mydev_attr_group);
	if (ret)
		return ret;

	dev_info(&pdev->dev, "mydev: sysfs group created\n");
	return 0;
}

static int mydev_remove(struct platform_device *pdev)
{
	sysfs_remove_group(&pdev->dev.kobj, &mydev_attr_group);
	dev_info(&pdev->dev, "mydev: sysfs group removed\n");
	return 0;
}

static struct platform_driver mydev_driver = {
	.probe  = mydev_probe,
	.remove = mydev_remove,
	.driver = {
		.name = "mydev",
	},
};
module_platform_driver(mydev_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("Device with custom sysfs attributes");
