#include <stdio.h>
#include "esp_sleep.h"
#include "esp_log.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TAG          "deep_sleep"
#define WAKEUP_GPIO  GPIO_NUM_0
#define SLEEP_DELAY_MS 5000

void app_main(void)
{
    /* Check wakeup reason before any initialization */
    esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();

    if (cause == ESP_SLEEP_WAKEUP_EXT0) {
        printf("Woke up from deep sleep via GPIO 0 (EXT0)\n");
    } else if (cause != ESP_SLEEP_WAKEUP_UNDEFINED) {
        printf("Woke up from deep sleep, cause: %d\n", cause);
    } else {
        /* First boot: no sleep wakeup */
        printf("First boot — performing initialization\n");
        printf("System initialized and ready\n");
    }

    /* Configure the wakeup GPIO with pull-up so a low signal is detectable */
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << WAKEUP_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    esp_err_t ret = gpio_config(&io_conf);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "GPIO config failed: %s", esp_err_to_name(ret));
        return;
    }

    /* Configure EXT0 wakeup: wake when GPIO 0 goes LOW */
    ret = esp_sleep_enable_ext0_wakeup(WAKEUP_GPIO, 0);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to configure wakeup source: %s", esp_err_to_name(ret));
        return;
    }

    printf("Entering deep sleep in %d ms...\n", SLEEP_DELAY_MS);
    vTaskDelay(pdMS_TO_TICKS(SLEEP_DELAY_MS));

    printf("Going to deep sleep now\n");
    esp_deep_sleep_start();
}
