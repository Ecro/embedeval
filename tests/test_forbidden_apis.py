"""Tests for src/embedeval/data/forbidden_apis.yaml and its loader.

Ensures the YAML extraction (P4 of PLAN-hiloop-transpile-readiness)
preserves byte-equivalent behavior to the prior hardcoded dict, and
that the data file is actually reachable via importlib.resources.
"""

from embedeval.check_utils import (
    _load_forbidden_apis,
    check_no_cross_platform_apis,
    get_cross_platform_forbidden,
)

EXPECTED_PLATFORMS = {
    "FreeRTOS",
    "Arduino",
    "STM32_HAL",
    "POSIX",
    "Linux_Userspace",
}


def test_yaml_loads_and_contains_all_platforms() -> None:
    data = get_cross_platform_forbidden()
    assert set(data.keys()) == EXPECTED_PLATFORMS


def test_yaml_preserves_prior_api_lists() -> None:
    """Byte-equivalent to prior hardcoded CROSS_PLATFORM_FORBIDDEN dict."""
    data = get_cross_platform_forbidden()
    assert data["FreeRTOS"] == [
        "xTaskCreate",
        "vTaskDelay",
        "xQueueSend",
        "xQueueReceive",
        "xSemaphoreTake",
        "xSemaphoreGive",
        "xTimerCreate",
        "vTaskDelete",
        "portYIELD",
    ]
    assert data["Arduino"] == [
        "analogRead",
        "analogWrite",
        "digitalRead",
        "digitalWrite",
        "Serial.print",
        "Serial.begin",
        "delay(",
        "millis(",
        "pinMode(",
    ]
    assert data["STM32_HAL"] == [
        "HAL_GPIO_WritePin",
        "HAL_GPIO_ReadPin",
        "HAL_UART_Transmit",
        "HAL_SPI_Transmit",
        "HAL_I2C_Master_Transmit",
        "HAL_ADC_Start",
        "HAL_TIM_Base_Start",
    ]
    assert data["POSIX"] == [
        "pthread_create",
        "pthread_mutex_lock",
        "pthread_mutex_unlock",
        "sem_wait",
        "sem_post",
    ]
    assert data["Linux_Userspace"] == [
        "open(",
        "close(",
        "ioctl(",
        "mmap(",
    ]


def test_detection_catches_freertos_contamination() -> None:
    code = """
    void setup_tasks(void) {
        xTaskCreate(worker, "w", 256, NULL, 1, NULL);
    }
    """
    found = check_no_cross_platform_apis(code)
    assert ("xTaskCreate", "FreeRTOS") in found


def test_detection_catches_arduino_contamination() -> None:
    code = """
    void loop(void) {
        digitalWrite(13, HIGH);
        delay(100);
    }
    """
    found = check_no_cross_platform_apis(code)
    apis = {api for api, _ in found}
    assert "digitalWrite" in apis
    assert "delay(" in apis


def test_detection_catches_posix_contamination() -> None:
    code = """
    void worker(void) {
        pthread_mutex_lock(&m);
    }
    """
    found = check_no_cross_platform_apis(code)
    assert ("pthread_mutex_lock", "POSIX") in found


def test_detection_ignores_comments() -> None:
    """Cross-platform detector strips comments before matching."""
    code = """
    // xTaskCreate is forbidden here
    /* also don't call digitalWrite */
    void clean_function(void) { return; }
    """
    found = check_no_cross_platform_apis(code)
    assert found == []


def test_skip_platforms_param_works() -> None:
    code = """
    void f(void) {
        open("/dev/mem", O_RDWR);
    }
    """
    # Without skip — Linux_Userspace detected
    assert any(p == "Linux_Userspace" for _, p in check_no_cross_platform_apis(code))
    # With skip — nothing detected
    assert check_no_cross_platform_apis(code, skip_platforms=["Linux_Userspace"]) == []


def test_loader_is_cached() -> None:
    """lru_cache must prevent redundant YAML reads within one process."""
    a = _load_forbidden_apis()
    b = _load_forbidden_apis()
    assert a is b  # identity, not just equality


def test_data_file_is_packaged() -> None:
    """Data file must be reachable via importlib.resources (ships with wheel)."""
    from importlib.resources import files

    resource = files("embedeval.data").joinpath("forbidden_apis.yaml")
    assert resource.is_file()
    text = resource.read_text()
    assert "platforms:" in text
    assert "FreeRTOS:" in text
