Write a Zephyr RTOS application that reads a single ADC channel and converts the result to millivolts.

Requirements:
1. Get the ADC device from devicetree using ADC_DT_SPEC_GET(DT_PATH(zephyr_user)) or equivalent
2. Verify the device is initialized and ready before use
3. Call adc_channel_setup_dt() to configure the channel before any read
4. Define a sample buffer (int16_t buf) and an adc_sequence struct that references it
5. Call adc_read() or adc_read_dt() to perform the acquisition
6. Call adc_raw_to_millivolts_dt() to convert the raw value to millivolts
7. Print the millivolt value using printk()
8. Read in a loop with k_sleep(K_MSLEEP(1000)) between samples

Use the Zephyr ADC DT spec API (adc_channel_setup_dt, adc_read_dt, adc_raw_to_millivolts_dt).

Include proper headers: zephyr/kernel.h and zephyr/drivers/adc.h.

Output ONLY the complete C source file.
