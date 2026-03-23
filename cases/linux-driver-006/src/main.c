#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/ioctl.h>

#define DEVICE_NAME "ioctldev"
#define IOCTL_MAGIC 'k'
#define IOCTL_MAX_NR 2

struct ioctl_arg {
	int value;
	char label[16];
};

#define IOCTL_SET_ARG  _IOW(IOCTL_MAGIC, 0, struct ioctl_arg)
#define IOCTL_GET_ARG  _IOR(IOCTL_MAGIC, 1, struct ioctl_arg)

static dev_t dev_num;
static struct cdev my_cdev;
static struct class *dev_class;
static struct ioctl_arg stored_arg;

static int dev_open(struct inode *inode, struct file *file)
{
	return 0;
}

static int dev_release(struct inode *inode, struct file *file)
{
	return 0;
}

static long my_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
	struct ioctl_arg karg;

	if (_IOC_TYPE(cmd) != IOCTL_MAGIC)
		return -ENOTTY;

	if (_IOC_NR(cmd) >= IOCTL_MAX_NR)
		return -ENOTTY;

	switch (cmd) {
	case IOCTL_SET_ARG:
		if (copy_from_user(&karg, (struct ioctl_arg __user *)arg,
				   sizeof(karg)))
			return -EFAULT;
		stored_arg = karg;
		pr_info("%s: set value=%d label=%s\n", DEVICE_NAME,
			karg.value, karg.label);
		break;

	case IOCTL_GET_ARG:
		if (copy_to_user((struct ioctl_arg __user *)arg, &stored_arg,
				 sizeof(stored_arg)))
			return -EFAULT;
		break;

	default:
		return -ENOTTY;
	}

	return 0;
}

static const struct file_operations fops = {
	.owner = THIS_MODULE,
	.open = dev_open,
	.release = dev_release,
	.unlocked_ioctl = my_ioctl,
};

static int __init ioctldev_init(void)
{
	int ret;

	ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
	if (ret < 0)
		return ret;

	cdev_init(&my_cdev, &fops);
	ret = cdev_add(&my_cdev, dev_num, 1);
	if (ret < 0) {
		unregister_chrdev_region(dev_num, 1);
		return ret;
	}

	dev_class = class_create(DEVICE_NAME);
	if (IS_ERR(dev_class)) {
		cdev_del(&my_cdev);
		unregister_chrdev_region(dev_num, 1);
		return PTR_ERR(dev_class);
	}

	device_create(dev_class, NULL, dev_num, NULL, DEVICE_NAME);
	pr_info("%s: registered, magic=0x%x\n", DEVICE_NAME, IOCTL_MAGIC);
	return 0;
}

static void __exit ioctldev_exit(void)
{
	device_destroy(dev_class, dev_num);
	class_destroy(dev_class);
	cdev_del(&my_cdev);
	unregister_chrdev_region(dev_num, 1);
	pr_info("%s: unregistered\n", DEVICE_NAME);
}

module_init(ioctldev_init);
module_exit(ioctldev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("ioctl handler with input validation");
