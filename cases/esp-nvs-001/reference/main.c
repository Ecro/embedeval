#include <stdio.h>
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"

static const char *TAG = "nvs_example";

void app_main(void)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        ret = nvs_flash_init();
    }
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "NVS flash init failed: %s", esp_err_to_name(ret));
        return;
    }

    nvs_handle_t nvs;
    ret = nvs_open("storage", NVS_READWRITE, &nvs);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "nvs_open failed: %s", esp_err_to_name(ret));
        return;
    }

    int32_t counter = 0;
    ret = nvs_get_i32(nvs, "counter", &counter);
    if (ret == ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGI(TAG, "Counter not found, starting at 0");
        counter = 0;
    } else if (ret != ESP_OK) {
        ESP_LOGE(TAG, "nvs_get_i32 failed: %s", esp_err_to_name(ret));
        nvs_close(nvs);
        return;
    }

    counter++;

    ret = nvs_set_i32(nvs, "counter", counter);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "nvs_set_i32 failed: %s", esp_err_to_name(ret));
        nvs_close(nvs);
        return;
    }

    ret = nvs_commit(nvs);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "nvs_commit failed: %s", esp_err_to_name(ret));
    }

    nvs_close(nvs);

    printf("Counter: %" PRId32 "\n", counter);
}
