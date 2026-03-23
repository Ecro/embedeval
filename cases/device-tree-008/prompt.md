Write a Zephyr Device Tree overlay that assigns DMA channels to a UART peripheral.

Requirements:
1. Reference the uart0 node using &uart0
2. Set status = "okay"
3. Add dmas property assigning two DMA channels: one for TX (channel 4, slot 2) and one for RX (channel 5, slot 2) using the dma0 controller
4. Add dma-names property with exactly two entries matching the dmas entries: "tx" and "rx"
5. Use the correct DMA phandle format: <&dma0 channel slot>

Output ONLY the Device Tree overlay (.overlay file content).
