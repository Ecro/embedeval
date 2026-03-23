Write a Zephyr Device Tree overlay that configures the /chosen node for console output and defines /aliases for board hardware.

Requirements:
1. Set /chosen { zephyr,console = &uart0; zephyr,shell-uart = &uart0; } to route console and shell to uart0
2. Define /aliases { led0 = &led_0; sw0 = &button_0; } using label references
3. Define the referenced nodes: led_0 as a GPIO LED node and button_0 as a GPIO button node, both as children of leds {} and buttons {} respectively under the root
4. Both led_0 and button_0 must use gpios properties with valid GPIO references

Output ONLY the Device Tree overlay (.overlay file content).
