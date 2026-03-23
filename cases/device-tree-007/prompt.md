Write a Zephyr Device Tree overlay that configures a peripheral clock source.

Requirements:
1. Reference the uart0 peripheral node using &uart0
2. Set status = "okay"
3. Add assigned-clocks property referencing a valid clock source (e.g., <&rcc STM32_SRC_HSI UART1_SEL>)
4. Add assigned-clock-rates property with a reasonable frequency value in Hz (e.g., 16000000 for 16 MHz)
5. The clock rate must be greater than 0 and less than or equal to 1000000000 (1 GHz)

Output ONLY the Device Tree overlay (.overlay file content).
