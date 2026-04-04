"""Negative tests for Device Tree I2C sensor overlay.

Reference: cases/device-tree-001/reference/main.c  (actually a .overlay file)
Checks:    cases/device-tree-001/checks/behavior.py

The reference overlay:
    &i2c0 {
        status = "okay";
        bme280@76 {
            compatible = "bosch,bme280";
            reg = <0x76>;
            status = "okay";
            int-gpios = <&gpio0 15 GPIO_ACTIVE_LOW>;
        };
    };

Mutation strategy
-----------------
* no_status_okay : removes all status = "okay" lines.
  The checks status_okay and status_okay_present look for 'status = "okay"' — will fail.

* wrong_reg_address : changes reg = <0x76> to reg = <0x77>.
  The check reg_address_0x76 looks for exact string "reg = <0x76>" — will fail.
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "no_status_okay",
        "description": (
            'status = "okay" removed — the i2c0 bus and bme280 node remain '
            "disabled; driver probe will never be called, sensor stays offline"
        ),
        "mutation": lambda code: _remove_lines(code, 'status = "okay"'),
        "must_fail": ["status_okay"],
    },
    {
        "name": "wrong_reg_address",
        "description": (
            "reg = <0x76> changed to reg = <0x77> — wrong I2C address for "
            "the BME280 sensor; driver will fail to communicate with the device"
        ),
        "mutation": lambda code: code.replace("reg = <0x76>", "reg = <0x77>"),
        "must_fail": ["reg_address_0x76"],
    },
]
