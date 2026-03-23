Write a Zephyr Device Tree overlay that adds a PWM LED node using the compatible string "pwm-leds". The node should contain a single LED child entry that references pwm0 channel 0 with a period of 20000000 nanoseconds (20ms). Set the label property to "green-led" on the child entry.

Output ONLY the Device Tree overlay (.overlay file content).
