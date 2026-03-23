&pinctrl {
    uart0_default: uart0_default {
        group1 {
            psels = <NRF_PSEL(UART_TX, 0, 6)>,
                    <NRF_PSEL(UART_RX, 0, 8)>;
        };
    };
};

&uart0 {
    status = "okay";
    pinctrl-0 = <&uart0_default>;
    pinctrl-names = "default";
};
