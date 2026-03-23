"""EmbedEval data models for benchmark evaluation."""

from enum import Enum

from pydantic import BaseModel, Field


class CaseCategory(str, Enum):
    """Categories of embedded firmware evaluation cases."""

    KCONFIG = "zephyr-kconfig"
    DEVICE_TREE = "device-tree"
    DMA = "dma"
    ISR_CONCURRENCY = "isr-concurrency"
    BLE = "ble"
    SPI_I2C = "spi-i2c"
    POWER_MGMT = "power-mgmt"
    WATCHDOG = "watchdog"
    OTA = "ota"
    BOOT = "boot"
    YOCTO = "yocto"
    NETWORKING = "networking"
    MEMORY_OPT = "memory-opt"


class DifficultyTier(str, Enum):
    """Difficulty tiers for evaluation cases."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EvalPlatform(str, Enum):
    """Evaluation platform targets."""

    NATIVE_SIM = "native_sim"
    QEMU_ARM = "qemu_arm"
    BABBLESIM = "babblesim"
    DOCKER_ONLY = "docker_only"


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
    zephyr_version: str


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


class LayerResult(BaseModel):
    """Result of a single evaluation layer."""

    layer: int = Field(ge=0, le=4)
    name: str
    passed: bool
    details: list[CheckDetail]
    error: str | None = None
    duration_seconds: float = Field(ge=0.0)


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
    duration_seconds: float = Field(ge=0.0)
    token_usage: TokenUsage
    cost_usd: float = Field(ge=0.0)


class ModelScore(BaseModel):
    """Aggregated score for a single model across all cases."""

    model: str
    pass_at_1: float = Field(ge=0.0, le=1.0)
    pass_at_5: float = Field(ge=0.0, le=1.0)
    total_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)
    layer_pass_rates: dict[str, float]


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
