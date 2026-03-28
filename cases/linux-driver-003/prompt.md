Write a minimal Linux IIO (Industrial I/O) driver that exposes an ADC channel via sysfs.

Requirements:
1. Define proper module metadata (license, author, description)
2. Define one IIO voltage channel with raw value access
3. Implement a read_raw callback that returns a fixed ADC reading (e.g., 1234) when the raw value is requested
4. For unsupported attribute requests, return an appropriate error
5. Implement a platform driver probe function that allocates and registers the IIO device using managed (devm) APIs
6. Use the module_platform_driver convenience macro

Output ONLY the complete C source file.
