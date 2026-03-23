Write a Zephyr Device Tree overlay that configures three peripherals on a single board:

1. Enable i2c0 (status = "okay") and add a BME680 environmental sensor child node at I2C address 0x77 (compatible "bosch,bme680", status "okay").
2. Enable spi0 (status = "okay") and add a SPI NOR flash child node at chip select 0 (compatible "jedec,spi-nor", reg = <0>, spi-max-frequency = <8000000>, size = <0x200000>, status "okay").
3. Enable gpio0 (status = "okay") and add a named-gpios property referencing two GPIO pins: gpio0 pin 4 (active high, output) and gpio0 pin 5 (active low, input).

Output ONLY the Device Tree overlay (.overlay file content).
