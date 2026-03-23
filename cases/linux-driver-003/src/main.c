#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/iio/iio.h>

static const struct iio_chan_spec myadc_channels[] = {
	{
		.type             = IIO_VOLTAGE,
		.indexed          = 1,
		.channel          = 0,
		.info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
	},
};

static int myadc_read_raw(struct iio_dev *indio_dev,
			  struct iio_chan_spec const *chan,
			  int *val, int *val2, long mask)
{
	switch (mask) {
	case IIO_CHAN_INFO_RAW:
		*val = 1234;
		return IIO_VAL_INT;
	default:
		return -EINVAL;
	}
}

static const struct iio_info myadc_info = {
	.read_raw = myadc_read_raw,
};

static int myadc_probe(struct platform_device *pdev)
{
	struct iio_dev *indio_dev;

	indio_dev = devm_iio_device_alloc(&pdev->dev, 0);
	if (!indio_dev)
		return -ENOMEM;

	indio_dev->name        = "myadc";
	indio_dev->info        = &myadc_info;
	indio_dev->modes       = INDIO_DIRECT_MODE;
	indio_dev->channels    = myadc_channels;
	indio_dev->num_channels = ARRAY_SIZE(myadc_channels);

	return devm_iio_device_register(&pdev->dev, indio_dev);
}

static struct platform_driver myadc_driver = {
	.probe  = myadc_probe,
	.driver = {
		.name = "myadc",
	},
};
module_platform_driver(myadc_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EmbedEval");
MODULE_DESCRIPTION("Minimal IIO ADC driver skeleton");
