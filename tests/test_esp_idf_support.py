"""Tests for ESP-IDF platform support in EmbedEval."""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from embedeval.evaluator import (
    _esp_idf_env_available,
    _is_esp_idf_case,
    evaluate,
)
from embedeval.models import CheckDetail


def _write_esp_metadata(case_dir: Path, **overrides: object) -> None:
    """Write a complete metadata.yaml for an ESP-IDF case."""
    meta = {
        "id": case_dir.name,
        "category": "gpio-basic",
        "difficulty": "easy",
        "title": "ESP test",
        "description": "ESP-IDF test case",
        "tags": ["esp-idf"],
        "platform": "esp_idf",
        "estimated_tokens": 200,
        "sdk_version": "5.3",
    }
    meta.update(overrides)
    (case_dir / "metadata.yaml").write_text(
        yaml.dump(meta), encoding="utf-8"
    )


def _write_zephyr_metadata(case_dir: Path, **overrides: object) -> None:
    """Write a complete metadata.yaml for a Zephyr case."""
    meta = {
        "id": case_dir.name,
        "category": "kconfig",
        "difficulty": "easy",
        "title": "Zephyr test",
        "description": "Zephyr test case",
        "tags": ["zephyr"],
        "platform": "native_sim",
        "estimated_tokens": 200,
        "sdk_version": "4.1.0",
    }
    meta.update(overrides)
    (case_dir / "metadata.yaml").write_text(
        yaml.dump(meta), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# _is_esp_idf_case detection tests
# ---------------------------------------------------------------------------

class TestIsEspIdfCase:
    """Tests for _is_esp_idf_case() detection logic."""

    def test_metadata_platform_esp_idf(self, tmp_path: Path) -> None:
        """Case with platform: esp_idf in metadata.yaml is detected."""
        case_dir = tmp_path / "esp-gpio-001"
        case_dir.mkdir()
        _write_esp_metadata(case_dir)
        assert _is_esp_idf_case(case_dir) is True

    def test_sdkconfig_defaults_marker(self, tmp_path: Path) -> None:
        """Case with sdkconfig.defaults file is detected as ESP-IDF."""
        case_dir = tmp_path / "esp-spi-001"
        case_dir.mkdir()
        (case_dir / "sdkconfig.defaults").write_text("CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n")
        assert _is_esp_idf_case(case_dir) is True

    def test_zephyr_case_not_detected(self, tmp_path: Path) -> None:
        """Zephyr case with native_sim platform is not detected as ESP-IDF."""
        case_dir = tmp_path / "kconfig-001"
        case_dir.mkdir()
        _write_zephyr_metadata(case_dir)
        assert _is_esp_idf_case(case_dir) is False

    def test_empty_case_dir_not_esp_idf(self, tmp_path: Path) -> None:
        """Empty case directory is not detected as ESP-IDF."""
        case_dir = tmp_path / "unknown-001"
        case_dir.mkdir()
        assert _is_esp_idf_case(case_dir) is False

    def test_no_metadata_but_has_sdkconfig(self, tmp_path: Path) -> None:
        """Case without metadata but with sdkconfig.defaults is detected."""
        case_dir = tmp_path / "esp-no-meta"
        case_dir.mkdir()
        (case_dir / "sdkconfig.defaults").touch()
        assert _is_esp_idf_case(case_dir) is True


# ---------------------------------------------------------------------------
# _esp_idf_env_available tests
# ---------------------------------------------------------------------------

class TestEspIdfEnvAvailable:
    """Tests for _esp_idf_env_available() environment check."""

    def test_no_idf_path_returns_false(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert _esp_idf_env_available() is False

    def test_idf_path_set_but_no_enable_build(self) -> None:
        env = {"IDF_PATH": "/opt/esp-idf"}
        with patch.dict("os.environ", env, clear=True):
            assert _esp_idf_env_available() is False

    def test_enable_build_set_but_no_idf_path(self) -> None:
        env = {"EMBEDEVAL_ENABLE_BUILD": "1"}
        with patch.dict("os.environ", env, clear=True):
            assert _esp_idf_env_available() is False

    def test_both_set_returns_true(self) -> None:
        env = {"IDF_PATH": "/opt/esp-idf", "EMBEDEVAL_ENABLE_BUILD": "1"}
        with patch.dict("os.environ", env, clear=True):
            assert _esp_idf_env_available() is True


# ---------------------------------------------------------------------------
# ESP-IDF compile gate integration tests
# ---------------------------------------------------------------------------

class TestEspIdfCompileGate:
    """Tests for ESP-IDF compile gate behaviour in the evaluation pipeline."""

    def _make_esp_idf_case(self, tmp_path: Path) -> Path:
        """Create a minimal ESP-IDF case directory."""
        case_dir = tmp_path / "esp-test-001"
        case_dir.mkdir()
        _write_esp_metadata(case_dir)
        return case_dir

    @patch("embedeval.evaluator._esp_idf_env_available", return_value=False)
    def test_esp_idf_case_skips_compile_when_no_env(
        self, _mock_env: object, tmp_path: Path
    ) -> None:
        """ESP-IDF case passes compile gate when IDF_PATH is not available."""
        case_dir = self._make_esp_idf_case(tmp_path)
        result = evaluate(case_dir=case_dir, generated_code="void app_main(void) {}")
        # compile gate (layer 1) should pass (skipped gracefully)
        assert result.layers[1].passed is True
        assert result.layers[1].details[0].check_name == "esp_idf_available"

    @patch("embedeval.evaluator._esp_idf_env_available", return_value=True)
    @patch("embedeval.evaluator.subprocess")
    def test_esp_idf_compile_success(
        self,
        mock_subprocess: object,
        _mock_env: object,
        tmp_path: Path,
    ) -> None:
        """ESP-IDF case compile gate passes when idf.py build returns 0."""
        import subprocess as sp
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.run.return_value = mock_result  # type: ignore[union-attr]
        mock_subprocess.TimeoutExpired = sp.TimeoutExpired  # type: ignore[union-attr]

        case_dir = self._make_esp_idf_case(tmp_path)
        result = evaluate(case_dir=case_dir, generated_code="void app_main(void) {}")
        assert result.layers[1].passed is True
        assert result.layers[1].details[0].check_name == "idf_build"

    @patch("embedeval.evaluator._esp_idf_env_available", return_value=True)
    @patch("embedeval.evaluator.subprocess")
    def test_esp_idf_compile_failure(
        self,
        mock_subprocess: object,
        _mock_env: object,
        tmp_path: Path,
    ) -> None:
        """ESP-IDF compile gate fails when idf.py build returns non-zero."""
        import subprocess as sp
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "CMake error: ..."
        mock_subprocess.run.return_value = mock_result  # type: ignore[union-attr]
        mock_subprocess.TimeoutExpired = sp.TimeoutExpired  # type: ignore[union-attr]

        case_dir = self._make_esp_idf_case(tmp_path)
        result = evaluate(case_dir=case_dir, generated_code="// bad code")
        assert result.layers[1].passed is False
        assert result.layers[1].error is not None

    @patch("embedeval.evaluator._esp_idf_env_available", return_value=True)
    @patch("embedeval.evaluator.subprocess")
    def test_esp_idf_compile_timeout(
        self,
        mock_subprocess: object,
        _mock_env: object,
        tmp_path: Path,
    ) -> None:
        """ESP-IDF compile gate reports timeout when idf.py hangs."""
        import subprocess as sp

        mock_subprocess.run.side_effect = sp.TimeoutExpired(  # type: ignore[union-attr]
            cmd="idf.py build", timeout=300.0
        )
        mock_subprocess.TimeoutExpired = sp.TimeoutExpired  # type: ignore[union-attr]

        case_dir = self._make_esp_idf_case(tmp_path)
        result = evaluate(case_dir=case_dir, generated_code="void app_main(void) {}")
        assert result.layers[1].passed is False
        assert result.layers[1].error is not None
        assert "timed out" in result.layers[1].error

    @patch("embedeval.evaluator._build_env_available", return_value=True)
    def test_zephyr_case_not_routed_to_esp_idf(
        self, _mock_env: object, tmp_path: Path
    ) -> None:
        """Zephyr case is not routed through the ESP-IDF compile path."""
        case_dir = tmp_path / "kconfig-001"
        case_dir.mkdir()
        _write_zephyr_metadata(case_dir)
        # Should attempt west build, not idf.py. We don't mock subprocess here
        # so we just verify it doesn't crash trying to call idf.py detection.
        assert _is_esp_idf_case(case_dir) is False


# ---------------------------------------------------------------------------
# Case check file validation: reference solutions should pass their own checks
# ---------------------------------------------------------------------------

class TestEspCaseChecks:
    """Verify each ESP-IDF case's static/behavior checks pass on reference code."""

    CASES_DIR = Path("/home/noel/embedeval/cases")

    def _load_reference(self, case_name: str) -> str:
        ref = self.CASES_DIR / case_name / "reference" / "main.c"
        return ref.read_text(encoding="utf-8")

    def _run_case_checks(self, case_name: str, module_name: str) -> list[CheckDetail]:
        import importlib.util

        module_path = self.CASES_DIR / case_name / "checks" / f"{module_name}.py"
        spec = importlib.util.spec_from_file_location("checks", module_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module.run_checks(self._load_reference(case_name))

    @pytest.mark.parametrize("case_name", [
        "esp-gpio-001",
        "esp-spi-001",
        "esp-wifi-001",
        "esp-i2c-001",
        "esp-timer-001",
    ])
    def test_static_checks_pass_on_reference(self, case_name: str) -> None:
        """Each case's static.py checks should all pass on the reference solution."""
        details = self._run_case_checks(case_name, "static")
        failures = [d for d in details if not d.passed]
        assert not failures, (
            f"{case_name} static check failures: "
            + ", ".join(f"{d.check_name}: {d.actual}" for d in failures)
        )

    @pytest.mark.parametrize("case_name", [
        "esp-gpio-001",
        "esp-spi-001",
        "esp-wifi-001",
        "esp-i2c-001",
        "esp-timer-001",
    ])
    def test_behavior_checks_pass_on_reference(self, case_name: str) -> None:
        """Each case's behavior.py checks should all pass on the reference solution."""
        details = self._run_case_checks(case_name, "behavior")
        failures = [d for d in details if not d.passed]
        assert not failures, (
            f"{case_name} behavior check failures: "
            + ", ".join(f"{d.check_name}: {d.actual}" for d in failures)
        )

    @pytest.mark.parametrize("case_name,bad_code,check_name", [
        (
            "esp-gpio-001",
            "#include <zephyr/kernel.h>\nvoid main(void) { gpio_pin_configure(dev, 2, GPIO_OUTPUT); }",
            "no_zephyr_apis",
        ),
        (
            "esp-spi-001",
            "#include <zephyr/drivers/spi.h>\nvoid app_main(void) { spi_transceive(dev, &cfg, &tx, &rx); }",
            "no_zephyr_apis",
        ),
        (
            "esp-gpio-001",
            "void setup() { pinMode(2, OUTPUT); } void loop() { digitalWrite(2, HIGH); delay(500); }",
            "no_arduino_apis",
        ),
        (
            "esp-wifi-001",
            "#include <WiFi.h>\nvoid app_main(void) { WiFi.begin(\"ssid\", \"pass\"); }",
            "no_arduino_apis",
        ),
        (
            "esp-timer-001",
            "void app_main(void) { xTimerCreate(\"t\", 1000, pdTRUE, NULL, cb); }",
            "no_freertos_timer_mixing",
        ),
    ])
    def test_hallucination_detected(
        self, case_name: str, bad_code: str, check_name: str
    ) -> None:
        """Hallucination checks reject wrong-platform code."""
        import importlib.util

        # Try both modules — check may be in either static.py or behavior.py
        target = None
        for module_name in ("behavior", "static"):
            module_path = self.CASES_DIR / case_name / "checks" / f"{module_name}.py"
            if not module_path.exists():
                continue
            spec = importlib.util.spec_from_file_location("checks", module_path)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            details = module.run_checks(bad_code)
            target = next((d for d in details if d.check_name == check_name), None)
            if target is not None:
                break

        assert target is not None, f"Check '{check_name}' not found in any check module"
        assert target.passed is False, f"Expected '{check_name}' to fail on wrong-platform code"
