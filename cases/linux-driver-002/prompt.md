Write a Linux kernel platform driver module that matches a Device Tree compatible string.

Requirements:
1. Include linux/module.h, linux/platform_device.h, linux/of.h, linux/mod_devicetable.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Define a static const struct of_device_id table with at least one entry using .compatible = "vendor,mydevice" and a sentinel entry {}
4. Call MODULE_DEVICE_TABLE(of, <your_of_match_table>) after the table definition
5. Implement a probe function:
   - Signature: static int mydev_probe(struct platform_device *pdev)
   - Print "mydevice: probe called" with dev_info(&pdev->dev, ...)
   - Return 0 on success
6. Implement a remove function:
   - Signature: static int mydev_remove(struct platform_device *pdev)
   - Print "mydevice: remove called" with dev_info
   - Return 0
7. Define a static struct platform_driver with:
   - .probe = mydev_probe
   - .remove = mydev_remove
   - .driver.name = "mydevice"
   - .driver.of_match_table pointing to your of_device_id table
8. Use module_platform_driver() macro to register/unregister the driver

IMPORTANT: MODULE_DEVICE_TABLE is required for the kernel module loader to match
Device Tree compatible strings. Missing it is a common mistake.

Output ONLY the complete C source file.
