#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>

#define DEVICE_NAME "mychardev"
#define BUF_SIZE 256

static dev_t dev_num;
static struct cdev my_cdev;
static struct class *dev_class;
static char device_buf[BUF_SIZE];
static int buf_len;

static int dev_open(struct inode *inode, struct file *file)
{
	pr_info("%s: device opened\n", DEVICE_NAME);
	return 0;
}

static int dev_release(struct inode *inode, struct file *file)
{
	pr_info("%s: device closed\n", DEVICE_NAME);
	return 0;
}

static ssize_t dev_read(struct file *file, char __user *buf,
			 size_t count, loff_t *offset)
{
	int bytes_to_read;

	if (*offset >= buf_len)
		return 0;

	bytes_to_read = min((int)count, buf_len - (int)*offset);

	if (copy_to_user(buf, device_buf + *offset, bytes_to_read))
		return -EFAULT;

	*offset += bytes_to_read;
	return bytes_to_read;
}

static ssize_t dev_write(struct file *file, const char __user *buf,
			  size_t count, loff_t *offset)
{
	int bytes_to_write = min((int)count, BUF_SIZE - 1);

	if (copy_from_user(device_buf, buf, bytes_to_write))
		return -EFAULT;

	buf_len = bytes_to_write;
	device_buf[buf_len] = '\0';
	pr_info("%s: received %d bytes\n", DEVICE_NAME, bytes_to_write);
	return bytes_to_write;
}

static const struct file_operations fops = {
	.owner = THIS_MODULE,
	.open = dev_open,
	.release = dev_release,
	.read = dev_read,
	.write = dev_write,
};

static int __init mychardev_init(void)
{
	int ret;

	ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
	if (ret < 0) {
		pr_err("Failed to allocate chrdev region\n");
		return ret;
	}

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
	pr_info("%s: registered with major %d\n", DEVICE_NAME, MAJOR(dev_num));
	return 0;
}

static void __exit mychardev_exit(void)
{
	device_destroy(dev_class, dev_num);
	class_destroy(dev_class);
	cdev_del(&my_cdev);
	unregister_chrdev_region(dev_num, 1);
	pr_info("%s: unregistered\n", DEVICE_NAME);
}

module_init(mychardev_init);
module_exit(mychardev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("Minimal character device driver");
