#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/interrupt.h>
#include <linux/wait.h>
#include <linux/spinlock.h>

#define DEVICE_NAME "irqchardev"
#define BUF_SIZE    64

static int irq_num = 0;
module_param(irq_num, int, 0444);
MODULE_PARM_DESC(irq_num, "IRQ number to request");

static dev_t dev_num;
static struct cdev my_cdev;

static DECLARE_WAIT_QUEUE_HEAD(data_wq);
static DEFINE_SPINLOCK(data_lock);
static volatile int data_ready;
static char data_buf[BUF_SIZE];
static int data_len;

static irqreturn_t mydev_irq_handler(int irq, void *dev_id)
{
	unsigned long flags;

	spin_lock_irqsave(&data_lock, flags);
	snprintf(data_buf, BUF_SIZE, "irq=%d\n", irq);
	data_len   = strlen(data_buf);
	data_ready = 1;
	spin_unlock_irqrestore(&data_lock, flags);

	wake_up_interruptible(&data_wq);
	return IRQ_HANDLED;
}

static int mydev_open(struct inode *inode, struct file *file)
{
	return 0;
}

static int mydev_release(struct inode *inode, struct file *file)
{
	return 0;
}

static ssize_t mydev_read(struct file *file, char __user *buf,
			  size_t count, loff_t *offset)
{
	int ret;
	unsigned long flags;
	int len;

	ret = wait_event_interruptible(data_wq, data_ready != 0);
	if (ret)
		return ret;

	spin_lock_irqsave(&data_lock, flags);
	len        = min((int)count, data_len);
	data_ready = 0;
	spin_unlock_irqrestore(&data_lock, flags);

	if (copy_to_user(buf, data_buf, len))
		return -EFAULT;

	return len;
}

static const struct file_operations fops = {
	.owner   = THIS_MODULE,
	.open    = mydev_open,
	.release = mydev_release,
	.read    = mydev_read,
};

static int __init irqchardev_init(void)
{
	int ret;

	init_waitqueue_head(&data_wq);
	spin_lock_init(&data_lock);

	ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
	if (ret < 0)
		return ret;

	cdev_init(&my_cdev, &fops);
	ret = cdev_add(&my_cdev, dev_num, 1);
	if (ret < 0) {
		unregister_chrdev_region(dev_num, 1);
		return ret;
	}

	if (irq_num > 0) {
		ret = request_irq(irq_num, mydev_irq_handler,
				  IRQF_SHARED, DEVICE_NAME, &data_wq);
		if (ret < 0) {
			cdev_del(&my_cdev);
			unregister_chrdev_region(dev_num, 1);
			return ret;
		}
	}

	pr_info("%s: registered, irq=%d\n", DEVICE_NAME, irq_num);
	return 0;
}

static void __exit irqchardev_exit(void)
{
	if (irq_num > 0)
		free_irq(irq_num, &data_wq);

	cdev_del(&my_cdev);
	unregister_chrdev_region(dev_num, 1);
	pr_info("%s: unregistered\n", DEVICE_NAME);
}

module_init(irqchardev_init);
module_exit(irqchardev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("Interrupt-driven character device with wait queue");
