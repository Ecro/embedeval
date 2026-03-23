#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

#define PROC_NAME "mydriver_status"

static int call_count;
static int status_active = 1;

static int my_show(struct seq_file *m, void *v)
{
	seq_printf(m, "status: %s\n", status_active ? "active" : "inactive");
	seq_printf(m, "count: %d\n", call_count);
	seq_printf(m, "driver: " PROC_NAME "\n");
	return 0;
}

static int my_open(struct inode *inode, struct file *file)
{
	call_count++;
	return single_open(file, my_show, NULL);
}

static const struct proc_ops my_proc_ops = {
	.proc_open    = my_open,
	.proc_read    = seq_read,
	.proc_lseek   = seq_lseek,
	.proc_release = single_release,
};

static int __init myproc_init(void)
{
	struct proc_dir_entry *entry;

	entry = proc_create(PROC_NAME, 0444, NULL, &my_proc_ops);
	if (!entry) {
		pr_err("Failed to create /proc/%s\n", PROC_NAME);
		return -ENOMEM;
	}

	pr_info("Created /proc/%s\n", PROC_NAME);
	return 0;
}

static void __exit myproc_exit(void)
{
	remove_proc_entry(PROC_NAME, NULL);
	pr_info("Removed /proc/%s\n", PROC_NAME);
}

module_init(myproc_init);
module_exit(myproc_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("Proc file for driver debug info");
