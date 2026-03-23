&can0 {
    status = "okay";
    bus-speed = <125000>;
    sample-point = <875>;

    can_transceiver0: mcp2562fd {
        compatible = "microchip,mcp2562fd";
        status = "okay";
    };
};
