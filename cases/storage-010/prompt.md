Write a Zephyr application that loads a setting from the settings subsystem with a default value fallback for first-boot scenarios.

Requirements:
1. Include zephyr/settings/settings.h and zephyr/kernel.h
2. Define a default value for the setting (e.g. #define DEFAULT_VALUE 42U)
3. Define a settings handler struct (struct settings_handler) with a name and h_set callback
4. Register the handler using settings_register()
5. Call settings_subsys_init() before settings_load()
6. Call settings_load() to load all settings from storage
7. If the setting was not found (key absent from storage), use the default value — do NOT crash
8. Use a static variable to track whether the setting was loaded (e.g. bool setting_loaded = false)
9. After settings_load(), check if setting_loaded is true; if not, use DEFAULT_VALUE
10. Print "SETTING=<value> (default)" if using default, "SETTING=<value> (loaded)" if loaded from storage
11. Check return value of settings_subsys_init() and settings_load()

Output ONLY the complete C source file.
