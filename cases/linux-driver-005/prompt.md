Write a Linux kernel driver that creates a device with custom sysfs read/write attributes.

Requirements:
1. Include linux/module.h, linux/platform_device.h, linux/device.h, linux/sysfs.h, linux/string.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Create a static int myvalue = 42 to store the attribute value
4. Implement a show function for reading the attribute:
   - Signature: static ssize_t myvalue_show(struct device *dev, struct device_attribute *attr, char *buf)
   - Use sysfs_emit(buf, "%d\n", myvalue) and return its result
5. Implement a store function for writing the attribute:
   - Signature: static ssize_t myvalue_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
   - Use kstrtoint(buf, 10, &myvalue) to parse the integer
   - Return count on success, -EINVAL on parse error
6. Declare the attribute with DEVICE_ATTR_RW(myvalue)
7. Define a static struct attribute pointer array and a static struct attribute_group named mydev_attr_group
8. In probe:
   - Call sysfs_create_group(&pdev->dev.kobj, &mydev_attr_group)
   - Return 0 on success
9. In remove:
   - Call sysfs_remove_group(&pdev->dev.kobj, &mydev_attr_group)
   - Return 0
10. Define platform_driver struct and use module_platform_driver() macro

IMPORTANT: sysfs_remove_group MUST be called in remove/exit. Missing it causes
a kernel warning on module unload. In store, always validate the parsed value
and return -EINVAL on error, not silently accept garbage.

Output ONLY the complete C source file.
