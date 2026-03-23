Write a Zephyr Device Tree overlay that configures pin control for a UART peripheral.

Requirements:
1. Reference the uart0 node using &uart0
2. Set status = "okay" on uart0
3. Add pinctrl-0 property referencing the &uart0_default state from the pinctrl node
4. Add pinctrl-names = "default" to name the pinctrl state
5. The pinctrl node should define uart0_default with pin configuration for TX and RX

Output ONLY the Device Tree overlay (.overlay file content).
