/ {
    chosen {
        zephyr,console = &uart0;
        zephyr,shell-uart = &uart0;
    };

    aliases {
        led0 = &led_0;
        sw0 = &button_0;
    };

    leds {
        compatible = "gpio-leds";
        led_0: led_0 {
            gpios = <&gpio0 13 GPIO_ACTIVE_LOW>;
            label = "LED 0";
        };
    };

    buttons {
        compatible = "gpio-keys";
        button_0: button_0 {
            gpios = <&gpio0 11 GPIO_ACTIVE_LOW>;
            label = "Button 0";
        };
    };
};
