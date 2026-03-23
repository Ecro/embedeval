Write a Zephyr RTOS application that saves and loads a configuration value using the Settings subsystem.

Requirements:
1. Include zephyr/settings/settings.h and zephyr/kernel.h
2. Call settings_subsys_init() before any other settings calls, check return value
3. Define a settings key path using the format "app/mykey" (namespace/key)
4. Write a uint32_t value (42) using settings_save_one() with the full key path and a pointer to the value
5. Implement a settings_handler struct with a load_cb that stores the loaded value into a variable
6. Register the handler with settings_register() before calling settings_load()
7. Call settings_load() to trigger loading, check return value
8. Print the loaded value with printk to confirm round-trip success
9. Handle all errors with return codes

Use the Zephyr Settings API: settings_subsys_init, settings_save_one, settings_register, settings_load.

Output ONLY the complete C source file.
