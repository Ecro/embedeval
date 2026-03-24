#include <stdio.h>
#include <string.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define PIN_MOSI 23
#define PIN_SCLK 18
#define PIN_CS   5

static const char *TAG = "spi_master";

void app_main(void)
{
    spi_bus_config_t buscfg = {
        .mosi_io_num = PIN_MOSI,
        .miso_io_num = -1,
        .sclk_io_num = PIN_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 64,
    };

    esp_err_t ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "SPI bus init failed: %s", esp_err_to_name(ret));
        return;
    }

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 1 * 1000 * 1000,
        .mode = 0,
        .spics_io_num = PIN_CS,
        .queue_size = 1,
    };

    spi_device_handle_t spi;
    ret = spi_bus_add_device(SPI2_HOST, &devcfg, &spi);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "SPI add device failed: %s", esp_err_to_name(ret));
        spi_bus_free(SPI2_HOST);
        return;
    }

    uint8_t tx_data[] = {0x01, 0x02, 0x03, 0x04};
    spi_transaction_t t = {
        .length = sizeof(tx_data) * 8,
        .tx_buffer = tx_data,
    };

    ret = spi_device_transmit(spi, &t);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "SPI transmit failed: %s", esp_err_to_name(ret));
    } else {
        ESP_LOGI(TAG, "SPI transmit OK: 0x%02x 0x%02x 0x%02x 0x%02x",
                 tx_data[0], tx_data[1], tx_data[2], tx_data[3]);
    }

    spi_bus_remove_device(spi);
    spi_bus_free(SPI2_HOST);
}
