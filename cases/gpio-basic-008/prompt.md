Write a Zephyr RTOS application that configures an ADC channel with hardware oversampling and reads averaged results.

Requirements:
1. Get the ADC device using DEVICE_DT_GET(DT_ALIAS(adc0)) and verify it is initialized and ready before use
2. Define an adc_channel_cfg struct with:
   - gain = ADC_GAIN_1
   - reference = ADC_REF_INTERNAL
   - acquisition_time = ADC_ACQ_TIME_DEFAULT
   - channel_id = 0
3. Configure the ADC channel using adc_channel_setup()
4. Define an adc_sequence struct with:
   - channels = BIT(0)
   - buffer pointing to a static int16_t sample buffer (at least 1 element)
   - buffer_size = sizeof(the buffer)
   - resolution = 12
   - oversampling = 4 (hardware averaging over 2^4 = 16 samples)
5. Read the ADC using adc_read() in a loop
6. Print the raw sample value with printk every iteration
7. Sleep 1 second between reads

Use ONLY the Zephyr ADC API. Do NOT use analogRead() (Arduino), HAL_ADC_Start() (STM32), or ADC_Read() (generic HAL).

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/adc.h.

Output ONLY the complete C source file.
