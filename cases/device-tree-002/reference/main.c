&spi0 {
    status = "okay";

    flash0: w25q128@0 {
        compatible = "jedec,spi-nor";
        reg = <0>;
        spi-max-frequency = <1000000>;
        size = <0x100000>;
        status = "okay";
    };
};
