&i2c0 {
    status = "okay";

    bme280@76 {
        compatible = "bosch,bme280";
        reg = <0x76>;
        status = "okay";
        int-gpios = <&gpio0 15 GPIO_ACTIVE_LOW>;
    };
};
