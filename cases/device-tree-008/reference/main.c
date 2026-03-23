&uart0 {
    status = "okay";
    dmas = <&dma0 4 2>, <&dma0 5 2>;
    dma-names = "tx", "rx";
};
