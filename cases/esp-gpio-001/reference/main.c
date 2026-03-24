#include <stdio.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LED_GPIO GPIO_NUM_2

void app_main(void)
{
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << LED_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    esp_err_t ret = gpio_config(&io_conf);
    if (ret != ESP_OK) {
        printf("GPIO config failed: %s\n", esp_err_to_name(ret));
        return;
    }

    int level = 0;
    while (1) {
        gpio_set_level(LED_GPIO, level);
        printf("LED %s\n", level ? "ON" : "OFF");
        level = !level;
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
