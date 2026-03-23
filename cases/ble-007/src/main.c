#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>

/* Nordic Semiconductor company ID (little-endian) + custom payload */
#define COMPANY_ID_LSB 0x59
#define COMPANY_ID_MSB 0x00

/* Manufacturer-specific data: 2-byte company ID + 2-byte payload (fw version) */
static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS,
		      (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	/* Total AD structure: 1 byte type + 4 bytes data = 5 bytes (well under 31) */
	BT_DATA_BYTES(BT_DATA_MANUFACTURER_DATA,
		      COMPANY_ID_LSB, COMPANY_ID_MSB,  /* Company ID LE */
		      0x01, 0x00),                      /* Firmware version 1.0 */
};

int main(void)
{
	int err;

	err = bt_enable(NULL);
	if (err) {
		printk("Bluetooth init failed: %d\n", err);
		return err;
	}

	err = bt_le_adv_start(BT_LE_ADV_NCONN, ad, ARRAY_SIZE(ad), NULL, 0);
	if (err) {
		printk("Advertising failed: %d\n", err);
		return err;
	}

	printk("Advertising with manufacturer data\n");
	k_sleep(K_FOREVER);
	return 0;
}
