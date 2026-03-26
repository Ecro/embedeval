"""EmbedEval data models for benchmark evaluation."""

from enum import Enum

from pydantic import BaseModel, Field


class CaseCategory(str, Enum):
    """Categories of embedded firmware evaluation cases."""

    # Tier 1: Platform-agnostic C code domains
    GPIO_BASIC = "gpio-basic"
    SPI_I2C = "spi-i2c"
    DMA = "dma"
    ISR_CONCURRENCY = "isr-concurrency"
    THREADING = "threading"
    TIMER = "timer"
    SENSOR_DRIVER = "sensor-driver"
    NETWORKING = "networking"
    BLE = "ble"
    SECURITY = "security"
    STORAGE = "storage"

    # Tier 2: System-level (build/boot/update)
    KCONFIG = "kconfig"
    DEVICE_TREE = "device-tree"
    BOOT = "boot"
    OTA = "ota"
    POWER_MGMT = "power-mgmt"
    WATCHDOG = "watchdog"

    # Tier 3: Platform-specific
    YOCTO = "yocto"
    LINUX_DRIVER = "linux-driver"
    MEMORY_OPT = "memory-opt"


class DifficultyTier(str, Enum):
    """Difficulty tiers for evaluation cases."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Visibility(str, Enum):
    """Visibility of evaluation cases."""

    PUBLIC = "public"
    PRIVATE = "private"


class EvalPlatform(str, Enum):
    """Evaluation platform targets."""

    # Zephyr
    NATIVE_SIM = "native_sim"
    QEMU_ARM = "qemu_arm"
    BABBLESIM = "babblesim"
    # FreeRTOS
    QEMU_FREERTOS = "qemu_freertos"
    ESP_IDF = "esp_idf"
    # STM32 HAL
    STM32_HAL = "stm32_hal"
    # Linux
    DOCKER_ONLY = "docker_only"
    QEMU_LINUX = "qemu_linux"
    YOCTO_BUILD = "yocto_build"


class TokenUsage(BaseModel):
    """Token usage statistics for a single LLM call."""

    input_tokens: int
    output_tokens: int
    total_tokens: int


class CaseMetadata(BaseModel):
    """Metadata for an evaluation case."""

    id: str
    category: CaseCategory
    difficulty: DifficultyTier
    title: str
    description: str
    tags: list[str]
    platform: EvalPlatform
    estimated_tokens: int
    sdk_version: str
    visibility: Visibility = Visibility.PUBLIC
    created_date: str | None = None  # ISO date, e.g. "2026-03-24"


class LLMResponse(BaseModel):
    """Response from an LLM call."""

    model: str
    generated_code: str
    token_usage: TokenUsage
    cost_usd: float = Field(ge=0.0)
    duration_seconds: float = Field(ge=0.0)


class CheckDetail(BaseModel):
    """Detail of a single evaluation check."""

    check_name: str
    passed: bool
    expected: str | None
    actual: str | None
    check_type: str
    weight: float = Field(default=1.0, ge=0.0)


class LayerResult(BaseModel):
    """Result of a single evaluation layer."""

    layer: int = Field(ge=0, le=4)
    name: str
    passed: bool
    details: list[CheckDetail]
    error: str | None = None
    duration_seconds: float = Field(ge=0.0)
    score: float = Field(default=1.0, ge=0.0, le=1.0)


class EvalResult(BaseModel):
    """Result of evaluating a single case against a model."""

    case_id: str
    category: CaseCategory | None = None
    model: str
    attempt: int
    generated_code: str
    layers: list[LayerResult]
    failed_at_layer: int | None = Field(default=None, ge=0, le=4)
    passed: bool
    total_score: float = Field(default=1.0, ge=0.0, le=1.0)
    duration_seconds: float = Field(ge=0.0)
    token_usage: TokenUsage
    cost_usd: float = Field(ge=0.0)


class ModelScore(BaseModel):
    """Aggregated score for a single model across all cases."""

    model: str
    pass_at_1: float = Field(ge=0.0, le=1.0)
    pass_at_3: float = Field(default=0.0, ge=0.0, le=1.0)
    pass_at_5: float = Field(ge=0.0, le=1.0)
    avg_score: float = Field(default=0.0, ge=0.0, le=1.0)
    total_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)
    layer_pass_rates: dict[str, float]
    pass_at_1_ci: tuple[float, float] = (0.0, 0.0)
    n_samples: int = Field(default=1, ge=1)


class CategoryScore(BaseModel):
    """Aggregated score for a single category across all models."""

    category: CaseCategory
    pass_at_1: float = Field(ge=0.0, le=1.0)
    total_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)


class OverallScore(BaseModel):
    """Overall benchmark scoring summary."""

    total_cases: int
    total_models: int
    best_model: str
    best_pass_at_1: float


class BenchmarkReport(BaseModel):
    """Complete benchmark report with all scores."""

    version: str
    date: str
    models: list[ModelScore]
    categories: list[CategoryScore]
    overall: OverallScore
    temperature: float = Field(default=0.0, ge=0.0)
    n_samples_per_case: int = Field(default=1, ge=1)
    n_runs: int = Field(default=1, ge=1)
