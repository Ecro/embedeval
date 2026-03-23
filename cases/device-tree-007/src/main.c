&uart0 {
    status = "okay";
    assigned-clocks = <&rcc STM32_SRC_HSI UART1_SEL>;
    assigned-clock-rates = <16000000>;
};
