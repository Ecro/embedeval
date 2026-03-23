#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>

#define DRIVER_NAME "gpio_consumer"

struct gpio_dev {
	struct gpio_desc *led_gpio;
};

static int gpio_consumer_probe(struct platform_device *pdev)
{
	struct gpio_dev *dev;
	int val;

	dev = devm_kzalloc(&pdev->dev, sizeof(*dev), GFP_KERNEL);
	if (!dev)
		return -ENOMEM;

	dev->led_gpio = devm_gpiod_get(&pdev->dev, "led", GPIOD_OUT_LOW);
	if (IS_ERR(dev->led_gpio)) {
		dev_err(&pdev->dev, "Failed to get LED GPIO: %ld\n",
			PTR_ERR(dev->led_gpio));
		return PTR_ERR(dev->led_gpio);
	}

	gpiod_direction_output(dev->led_gpio, 0);

	gpiod_set_value(dev->led_gpio, 1);
	val = gpiod_get_value(dev->led_gpio);
	dev_info(&pdev->dev, "LED GPIO set high, readback=%d\n", val);

	platform_set_drvdata(pdev, dev);
	return 0;
}

static int gpio_consumer_remove(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "%s: removed (devm handles GPIO release)\n",
		 DRIVER_NAME);
	return 0;
}

static struct platform_driver gpio_consumer_driver = {
	.probe  = gpio_consumer_probe,
	.remove = gpio_consumer_remove,
	.driver = {
		.name  = DRIVER_NAME,
		.owner = THIS_MODULE,
	},
};

static int __init gpio_consumer_init(void)
{
	return platform_driver_register(&gpio_consumer_driver);
}

static void __exit gpio_consumer_exit(void)
{
	platform_driver_unregister(&gpio_consumer_driver);
}

module_init(gpio_consumer_init);
module_exit(gpio_consumer_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("GPIO consumer using modern gpiod API");
