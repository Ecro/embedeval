/ {
    vdd_3v3: regulator-vdd-3v3 {
        compatible = "regulator-fixed";
        regulator-name = "vdd-3v3";
        regulator-min-microvolt = <3300000>;
        regulator-max-microvolt = <3300000>;
        regulator-boot-on;
        status = "okay";
    };
};
