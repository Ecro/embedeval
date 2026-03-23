/ {
    pwm_leds {
        compatible = "pwm-leds";

        green_led: green_led_0 {
            label = "green-led";
            pwms = <&pwm0 0 20000000 PWM_POLARITY_NORMAL>;
        };
    };
};
