"""Static analysis checks for Linux GPIO consumer driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate GPIO consumer driver code structure."""
    details: list[CheckDetail] = []

    has_gpio_consumer = "linux/gpio/consumer.h" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_consumer_header",
            passed=has_gpio_consumer,
            expected="linux/gpio/consumer.h included (modern gpiod API)",
            actual="present" if has_gpio_consumer else "missing",
            check_type="exact_match",
        )
    )

    has_gpio_desc = "gpio_desc" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_desc_type_used",
            passed=has_gpio_desc,
            expected="struct gpio_desc* used (modern gpiod type)",
            actual="present" if has_gpio_desc else "missing (int gpio number = legacy)",
            check_type="exact_match",
        )
    )

    has_devm_gpiod = "devm_gpiod_get" in generated_code
    details.append(
        CheckDetail(
            check_name="devm_gpiod_get_used",
            passed=has_devm_gpiod,
            expected="devm_gpiod_get() used for auto-cleanup GPIO request",
            actual="present" if has_devm_gpiod else "MISSING (use devm_ for auto cleanup!)",
            check_type="exact_match",
        )
    )

    has_gpiod_set = "gpiod_set_value" in generated_code
    details.append(
        CheckDetail(
            check_name="gpiod_set_value_used",
            passed=has_gpiod_set,
            expected="gpiod_set_value() used (modern API)",
            actual="present" if has_gpiod_set else "missing",
            check_type="exact_match",
        )
    )

    has_direction = "gpiod_direction_output" in generated_code or "gpiod_direction_input" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_direction_set",
            passed=has_direction,
            expected="gpiod_direction_output/input() called before I/O",
            actual="present" if has_direction else "missing (direction must be set first)",
            check_type="exact_match",
        )
    )

    return details
