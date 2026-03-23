#include <linux/module.h>
#include <linux/workqueue.h>
#include <linux/interrupt.h>
#include <linux/slab.h>

#define DRIVER_NAME "wq_demo"

struct my_dev {
	struct work_struct work;
	int event_count;
};

static struct my_dev *g_dev;

static void my_work_handler(struct work_struct *work)
{
	struct my_dev *dev = container_of(work, struct my_dev, work);

	dev->event_count++;
	pr_info("%s: work handler running, event_count=%d\n",
		DRIVER_NAME, dev->event_count);

	/* Heavy processing safe here — process context, can sleep */
	msleep(1);
	pr_info("%s: deferred work completed\n", DRIVER_NAME);
}

/* Simulate triggering from interrupt/timer context */
static void trigger_work(struct my_dev *dev)
{
	pr_info("%s: scheduling deferred work\n", DRIVER_NAME);
	schedule_work(&dev->work);
}

static int __init wq_demo_init(void)
{
	g_dev = kzalloc(sizeof(*g_dev), GFP_KERNEL);
	if (!g_dev)
		return -ENOMEM;

	INIT_WORK(&g_dev->work, my_work_handler);

	/* Trigger initial work item */
	trigger_work(g_dev);

	pr_info("%s: module loaded, work scheduled\n", DRIVER_NAME);
	return 0;
}

static void __exit wq_demo_exit(void)
{
	if (g_dev) {
		cancel_work_sync(&g_dev->work);
		kfree(g_dev);
	}
	pr_info("%s: module unloaded\n", DRIVER_NAME);
}

module_init(wq_demo_init);
module_exit(wq_demo_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("Workqueue deferred processing example");
