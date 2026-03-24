#include <stdio.h>
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_log.h"

#define TAG          "adc_example"
#define ADC_CHANNEL  ADC_CHANNEL_6   /* GPIO 34 on ESP32 */
#define ADC_ATTEN    ADC_ATTEN_DB_12 /* 0-3.3V range */
#define ADC_BITWIDTH ADC_BITWIDTH_12
#define SAMPLE_COUNT 10

void app_main(void)
{
    /* Create the ADC oneshot unit */
    adc_oneshot_unit_handle_t adc_handle;
    adc_oneshot_unit_init_cfg_t unit_cfg = {
        .unit_id = ADC_UNIT_1,
    };
    esp_err_t ret = adc_oneshot_new_unit(&unit_cfg, &adc_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "ADC unit init failed: %s", esp_err_to_name(ret));
        return;
    }

    /* Configure the channel */
    adc_oneshot_chan_cfg_t chan_cfg = {
        .atten = ADC_ATTEN,
        .bitwidth = ADC_BITWIDTH,
    };
    ret = adc_oneshot_config_channel(adc_handle, ADC_CHANNEL, &chan_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "ADC channel config failed: %s", esp_err_to_name(ret));
        adc_oneshot_del_unit(adc_handle);
        return;
    }

    /* Create calibration scheme — try curve fitting first, fall back to line fitting */
    adc_cali_handle_t cali_handle = NULL;
    bool calibrated = false;

#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
    adc_cali_curve_fitting_config_t cali_cfg = {
        .unit_id  = ADC_UNIT_1,
        .chan     = ADC_CHANNEL,
        .atten    = ADC_ATTEN,
        .bitwidth = ADC_BITWIDTH,
    };
    ret = adc_cali_create_scheme_curve_fitting(&cali_cfg, &cali_handle);
    if (ret == ESP_OK) {
        calibrated = true;
    }
#endif

#if ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
    if (!calibrated) {
        adc_cali_line_fitting_config_t lf_cfg = {
            .unit_id  = ADC_UNIT_1,
            .atten    = ADC_ATTEN,
            .bitwidth = ADC_BITWIDTH,
        };
        ret = adc_cali_create_scheme_line_fitting(&lf_cfg, &cali_handle);
        if (ret == ESP_OK) {
            calibrated = true;
        }
    }
#endif

    if (!calibrated) {
        ESP_LOGW(TAG, "ADC calibration not available, millivolt readings will be inaccurate");
    }

    /* Take SAMPLE_COUNT readings and average them */
    int64_t sum = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
        int raw = 0;
        ret = adc_oneshot_read(adc_handle, ADC_CHANNEL, &raw);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "ADC read failed: %s", esp_err_to_name(ret));
            break;
        }
        sum += raw;
    }
    int raw_avg = (int)(sum / SAMPLE_COUNT);

    /* Convert to millivolts */
    int voltage_mv = 0;
    if (calibrated) {
        ret = adc_cali_raw_to_voltage(cali_handle, raw_avg, &voltage_mv);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Calibration conversion failed: %s", esp_err_to_name(ret));
        }
    }

    printf("ADC raw average: %d\n", raw_avg);
    printf("ADC voltage: %d mV\n", voltage_mv);

    /* Clean up */
    if (calibrated) {
#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
        adc_cali_delete_scheme_curve_fitting(cali_handle);
#elif ADC_CALI_SCHEME_LINE_FITTING_SUPPORTED
        adc_cali_delete_scheme_line_fitting(cali_handle);
#endif
    }
    adc_oneshot_del_unit(adc_handle);
}
