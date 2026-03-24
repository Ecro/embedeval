#include <stdio.h>
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TIMER_PERIOD_US 1000000ULL  /* 1 second in microseconds */
#define MAX_COUNT       5

static const char *TAG = "esp_timer";
static int s_count = 0;
static esp_timer_handle_t s_timer;

static void periodic_timer_callback(void *arg)
{
    s_count++;
    ESP_LOGI(TAG, "Timer fired: count = %d", s_count);

    if (s_count >= MAX_COUNT) {
        esp_timer_stop(s_timer);
        ESP_LOGI(TAG, "Timer stopped after %d iterations", MAX_COUNT);
    }
}

void app_main(void)
{
    const esp_timer_create_args_t timer_args = {
        .callback = &periodic_timer_callback,
        .name = "periodic_timer",
    };

    esp_err_t ret = esp_timer_create(&timer_args, &s_timer);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_timer_create failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_timer_start_periodic(s_timer, TIMER_PERIOD_US);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_timer_start_periodic failed: %s", esp_err_to_name(ret));
        esp_timer_delete(s_timer);
        return;
    }

    ESP_LOGI(TAG, "Periodic timer started, period = 1s");

    /* Wait for the timer to complete all iterations */
    while (s_count < MAX_COUNT) {
        vTaskDelay(pdMS_TO_TICKS(100));
    }

    ret = esp_timer_delete(s_timer);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_timer_delete failed: %s", esp_err_to_name(ret));
    } else {
        ESP_LOGI(TAG, "Timer deleted successfully");
    }
}
