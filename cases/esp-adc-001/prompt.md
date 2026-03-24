Write an ESP-IDF application that reads an analog voltage and reports it in millivolts.

Requirements:
1. Configure ADC1 channel 6 (GPIO 34) with 12-bit resolution
2. Set signal attenuation appropriate for measuring a 0-3.3V range
3. Calibrate the ADC to compensate for manufacturing variation
4. Take 10 readings and compute their average
5. Convert the averaged raw value to millivolts using the calibration data
6. Print both the raw average and the millivolt result

Use the ESP-IDF ADC oneshot driver.
Output ONLY the complete C source file.
