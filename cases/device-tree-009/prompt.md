Write a Zephyr Device Tree overlay that defines a fixed voltage regulator node.

Requirements:
1. Define a new regulator node in the root of the overlay (not inside another node)
2. Use compatible = "regulator-fixed"
3. Set regulator-name = "vdd-3v3"
4. Set regulator-min-microvolt = <3300000> (3.3V in microvolts, NOT millivolts)
5. Set regulator-max-microvolt = <3300000> (min must equal or be less than max)
6. Add regulator-boot-on; property (boolean, no value)
7. Set status = "okay"

Output ONLY the Device Tree overlay (.overlay file content).
