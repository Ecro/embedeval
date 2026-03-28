"""Static analysis checks for sensor-filter-UART task architecture."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor-filter-UART task architecture code structure."""
    details: list[CheckDetail] = []

    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    has_thread = (
        "K_THREAD_DEFINE" in generated_code
        or "k_thread_create" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="thread_created",
            passed=has_thread,
            expected="K_THREAD_DEFINE or k_thread_create present",
            actual="present" if has_thread else "missing",
            check_type="exact_match",
        )
    )

    has_freertos = any(api in generated_code for api in [
        "xTaskCreate", "vTaskDelay", "TaskHandle_t", "FreeRTOS.h",
        "portTICK_PERIOD_MS",
    ])
    has_arduino = any(api in generated_code for api in [
        "Arduino.h", "setup()", "loop()", "Serial.print",
    ])
    no_contamination = not has_freertos and not has_arduino
    details.append(
        CheckDetail(
            check_name="no_cross_platform_contamination",
            passed=no_contamination,
            expected="No FreeRTOS or Arduino APIs",
            actual="clean" if no_contamination else "contaminated with non-Zephyr APIs",
            check_type="exact_match",
        )
    )

    has_main = "int main(" in generated_code or "void main(" in generated_code
    details.append(
        CheckDetail(
            check_name="has_main_function",
            passed=has_main,
            expected="main() function present",
            actual="present" if has_main else "missing",
            check_type="exact_match",
        )
    )

    return details
