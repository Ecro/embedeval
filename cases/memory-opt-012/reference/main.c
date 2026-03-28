#include <zephyr/kernel.h>

#define CRC16_CCITT_POLY  0x1021U
#define CRC16_CCITT_INIT  0xFFFFU
#define TEST_BUF_SIZE     16U

static uint16_t crc16_ccitt(const uint8_t *data, uint16_t len)
{
    uint16_t crc = CRC16_CCITT_INIT;

    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000U) {
                crc = (crc << 1) ^ CRC16_CCITT_POLY;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

int main(void)
{
    static const uint8_t test_buf[TEST_BUF_SIZE] = {
        0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38,
        0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40,
    };

    uint16_t result = crc16_ccitt(test_buf, TEST_BUF_SIZE);

    printk("CRC-16-CCITT: 0x%04X\n", result);
    return 0;
}
