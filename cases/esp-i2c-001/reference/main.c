#include <stdio.h>
#include "driver/i2c_master.h"
#include "esp_log.h"

#define I2C_MASTER_SCL_IO   22
#define I2C_MASTER_SDA_IO   21
#define I2C_MASTER_FREQ_HZ  100000
#define SENSOR_ADDR         0x68
#define WHO_AM_I_REG        0x75

static const char *TAG = "i2c_example";

void app_main(void)
{
    /* Configure and create the I2C master bus */
    i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };

    i2c_master_bus_handle_t bus_handle;
    esp_err_t ret = i2c_new_master_bus(&bus_config, &bus_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to create I2C master bus: %s", esp_err_to_name(ret));
        return;
    }

    /* Add the sensor device to the bus */
    i2c_device_config_t dev_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = SENSOR_ADDR,
        .scl_speed_hz = I2C_MASTER_FREQ_HZ,
    };

    i2c_master_dev_handle_t dev_handle;
    ret = i2c_master_bus_add_device(bus_handle, &dev_config, &dev_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to add device to I2C bus: %s", esp_err_to_name(ret));
        i2c_del_master_bus(bus_handle);
        return;
    }

    /* Write register address, then read 1 byte back (combined transfer) */
    uint8_t reg_addr = WHO_AM_I_REG;
    uint8_t read_data = 0;

    ret = i2c_master_transmit_receive(dev_handle, &reg_addr, sizeof(reg_addr),
                                     &read_data, sizeof(read_data), -1);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "I2C transmit-receive failed: %s", esp_err_to_name(ret));
    } else {
        printf("Register 0x%02X value: 0x%02X\n", WHO_AM_I_REG, read_data);
    }

    /* Clean up */
    i2c_master_bus_rm_device(dev_handle);
    i2c_del_master_bus(bus_handle);
}
