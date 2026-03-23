Write a minimal Linux IIO (Industrial I/O) driver that exposes an ADC channel via sysfs.

Requirements:
1. Include linux/module.h, linux/platform_device.h, linux/iio/iio.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Define a static const struct iio_chan_spec array with one channel:
   - .type = IIO_VOLTAGE
   - .indexed = 1
   - .channel = 0
   - .info_mask_separate = BIT(IIO_CHAN_INFO_RAW)
4. Implement a read_raw callback:
   - Signature: static int myadc_read_raw(struct iio_dev *indio_dev, struct iio_chan_spec const *chan, int *val, int *val2, long mask)
   - When mask == IIO_CHAN_INFO_RAW: set *val to a fixed value (e.g., 1234), return IIO_VAL_INT
   - For other masks: return -EINVAL
5. Define a static const struct iio_info with .read_raw = myadc_read_raw
6. Implement probe function:
   - Allocate iio_dev with devm_iio_device_alloc(&pdev->dev, 0)
   - Set indio_dev->name, indio_dev->info, indio_dev->modes = INDIO_DIRECT_MODE
   - Set indio_dev->channels and indio_dev->num_channels
   - Register with devm_iio_device_register(&pdev->dev, indio_dev)
   - Return 0 on success
7. Define platform_driver struct and use module_platform_driver() macro

IMPORTANT: read_raw MUST return IIO_VAL_INT (not 0) for RAW reads. Returning 0
causes sysfs reads to show empty data. Also, devm_iio_device_register handles
cleanup automatically — do NOT call iio_device_unregister in remove.

Output ONLY the complete C source file.
