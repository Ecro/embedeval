#include <stdio.h>
#include <string.h>
#include "nvs_flash.h"
#include "esp_bt.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"
#include "esp_bt_main.h"
#include "esp_log.h"

#define TAG              "ble_gatt_server"
#define DEVICE_NAME      "ESP32_GATT_SRV"
#define GATTS_APP_ID     0
#define SVC_INST_ID      0

/* Custom service UUID: 0x00FF */
#define GATTS_SERVICE_UUID   0x00FF
/* Custom characteristic UUID: 0xFF01 */
#define GATTS_CHAR_UUID      0xFF01

#define GATTS_CHAR_VAL_LEN_MAX 20

static uint8_t char_value[GATTS_CHAR_VAL_LEN_MAX] = {0};
static uint16_t char_value_len = sizeof(char_value);

static uint16_t gatts_handle_table[2]; /* 0: service, 1: characteristic */

static esp_ble_adv_params_t adv_params = {
    .adv_int_min        = 0x20,
    .adv_int_max        = 0x40,
    .adv_type           = ADV_TYPE_IND,
    .own_addr_type      = BLE_ADDR_TYPE_PUBLIC,
    .channel_map        = ADV_CHNL_ALL,
    .adv_filter_policy  = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};

static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param)
{
    switch (event) {
    case ESP_GAP_BLE_ADV_START_COMPLETE_EVT:
        if (param->adv_start_cmpl.status != ESP_BT_STATUS_SUCCESS) {
            ESP_LOGE(TAG, "Advertising start failed");
        } else {
            ESP_LOGI(TAG, "Advertising started");
        }
        break;
    case ESP_GAP_BLE_ADV_STOP_COMPLETE_EVT:
        ESP_LOGI(TAG, "Advertising stopped");
        break;
    default:
        break;
    }
}

static void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if,
                                esp_ble_gatts_cb_param_t *param)
{
    switch (event) {
    case ESP_GATTS_REG_EVT:
        ESP_LOGI(TAG, "GATTS app registered, status %d", param->reg.status);
        esp_ble_gap_set_device_name(DEVICE_NAME);
        esp_ble_gap_config_adv_data_raw((uint8_t *)DEVICE_NAME, strlen(DEVICE_NAME));

        esp_gatt_srvc_id_t service_id = {
            .is_primary = true,
            .id = {
                .inst_id = SVC_INST_ID,
                .uuid = {
                    .len = ESP_UUID_LEN_16,
                    .uuid.uuid16 = GATTS_SERVICE_UUID,
                },
            },
        };
        esp_ble_gatts_create_service(gatts_if, &service_id, 4);
        break;

    case ESP_GATTS_CREATE_EVT:
        gatts_handle_table[0] = param->create.service_handle;
        esp_ble_gatts_start_service(gatts_handle_table[0]);

        esp_bt_uuid_t char_uuid = {
            .len = ESP_UUID_LEN_16,
            .uuid.uuid16 = GATTS_CHAR_UUID,
        };
        esp_attr_value_t char_val = {
            .attr_max_len = GATTS_CHAR_VAL_LEN_MAX,
            .attr_len = char_value_len,
            .attr_value = char_value,
        };
        esp_ble_gatts_add_char(gatts_handle_table[0], &char_uuid,
                               ESP_GATT_PERM_READ | ESP_GATT_PERM_WRITE,
                               ESP_GATT_CHAR_PROP_BIT_READ | ESP_GATT_CHAR_PROP_BIT_WRITE,
                               &char_val, NULL);
        break;

    case ESP_GATTS_ADD_CHAR_EVT:
        gatts_handle_table[1] = param->add_char.attr_handle;
        ESP_LOGI(TAG, "Characteristic added, handle %d", gatts_handle_table[1]);
        esp_ble_gap_start_advertising(&adv_params);
        break;

    case ESP_GATTS_CONNECT_EVT:
        ESP_LOGI(TAG, "Client connected, conn_id %d", param->connect.conn_id);
        break;

    case ESP_GATTS_DISCONNECT_EVT:
        ESP_LOGI(TAG, "Client disconnected, restarting advertising");
        esp_ble_gap_start_advertising(&adv_params);
        break;

    case ESP_GATTS_READ_EVT:
        ESP_LOGI(TAG, "Read request, handle %d", param->read.handle);
        esp_gatt_rsp_t rsp = {0};
        rsp.attr_value.handle = param->read.handle;
        rsp.attr_value.len = char_value_len;
        memcpy(rsp.attr_value.value, char_value, char_value_len);
        esp_ble_gatts_send_response(gatts_if, param->read.conn_id,
                                   param->read.trans_id, ESP_GATT_OK, &rsp);
        break;

    case ESP_GATTS_WRITE_EVT:
        ESP_LOGI(TAG, "Write request, len %d", param->write.len);
        if (param->write.len <= GATTS_CHAR_VAL_LEN_MAX) {
            memcpy(char_value, param->write.value, param->write.len);
            char_value_len = param->write.len;
        }
        if (param->write.need_rsp) {
            esp_ble_gatts_send_response(gatts_if, param->write.conn_id,
                                       param->write.trans_id, ESP_GATT_OK, NULL);
        }
        break;

    default:
        break;
    }
}

void app_main(void)
{
    /* NVS must be initialized before BLE */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* Release classic BT memory (not needed for BLE only) */
    ESP_ERROR_CHECK(esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT));

    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ret = esp_bt_controller_init(&bt_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "BT controller init failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_bt_controller_enable(ESP_BT_MODE_BLE);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "BT controller enable failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_bluedroid_init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Bluedroid init failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_bluedroid_enable();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Bluedroid enable failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_ble_gatts_register_callback(gatts_event_handler);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "GATTS register callback failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_ble_gap_register_callback(gap_event_handler);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "GAP register callback failed: %s", esp_err_to_name(ret));
        return;
    }

    ret = esp_ble_gatts_app_register(GATTS_APP_ID);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "GATTS app register failed: %s", esp_err_to_name(ret));
        return;
    }

    ESP_LOGI(TAG, "BLE GATT server initialized");
}
