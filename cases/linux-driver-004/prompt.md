Write a Linux kernel character device driver that uses an IRQ handler and a wait queue to implement blocking read().

Requirements:
1. Include linux/module.h, linux/fs.h, linux/cdev.h, linux/uaccess.h, linux/interrupt.h, linux/wait.h, linux/spinlock.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Define module parameters: irq_num (int, default 0) for the IRQ number
4. Declare:
   - A static wait_queue_head_t data_wq (initialized with init_waitqueue_head)
   - A static spinlock_t data_lock (initialized with spin_lock_init)
   - A static volatile int data_ready = 0
   - A static char data_buf[64] with a static int data_len
5. Implement the IRQ handler:
   - Signature: static irqreturn_t mydev_irq_handler(int irq, void *dev_id)
   - Acquire spin_lock, set data_ready = 1, fill data_buf with sample data, release spin_lock
   - Call wake_up_interruptible(&data_wq) to wake blocked readers
   - Return IRQ_HANDLED
6. Implement file_operations:
   - .open: return 0
   - .release: return 0
   - .read: call wait_event_interruptible(data_wq, data_ready != 0), then copy data to user with copy_to_user, reset data_ready = 0, return bytes copied
7. In module_init:
   - Allocate chrdev region, cdev_init, cdev_add
   - Call request_irq(irq_num, mydev_irq_handler, IRQF_SHARED, "mydev", &data_wq)
   - Initialize wait queue and spinlock
8. In module_exit:
   - Call free_irq(irq_num, &data_wq) BEFORE removing the cdev
   - cdev_del, unregister_chrdev_region

IMPORTANT: Never sleep (wait_event, msleep, etc.) inside an IRQ handler — the IRQ
context cannot schedule. Only wake_up_interruptible is safe from IRQ context.
Always free_irq in exit to avoid spurious IRQs after module unload.

Output ONLY the complete C source file.
