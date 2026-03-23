&i2c0 {
    status = "okay";

    bme680@77 {
        compatible = "bosch,bme680";
        reg = <0x77>;
        status = "okay";
    };
};

&spi0 {
    status = "okay";

    flash0: w25q256@0 {
        compatible = "jedec,spi-nor";
        reg = <0>;
        spi-max-frequency = <8000000>;
        size = <0x200000>;
        status = "okay";
    };
};

&gpio0 {
    status = "okay";

    named-gpios {
        output-pin {
            gpios = <&gpio0 4 GPIO_ACTIVE_HIGH>;
        };
        input-pin {
            gpios = <&gpio0 5 GPIO_ACTIVE_LOW>;
        };
    };
};
