"""Tests for prompt sensitivity analysis."""

from embedeval.sensitivity import (
    CaseSensitivity,
    SensitivityReport,
    calculate_robustness,
    generate_variants,
    _find_bullet_groups,
    _rephrase_imperatives,
    _remove_output_instruction,
)


class TestGenerateVariants:
    """Tests for prompt variant generation."""

    def test_returns_n_variants(self) -> None:
        prompt = "Write a function.\n- Req 1\n- Req 2\n- Req 3\n- Req 4"
        variants = generate_variants(prompt, n=3)
        assert len(variants) == 3

    def test_variants_differ_from_original(self) -> None:
        prompt = (
            "Write a Zephyr application.\n"
            "1. Configure GPIO\n"
            "2. Set up interrupt\n"
            "3. Toggle LED\n"
            "4. Add callback\n"
            "Output ONLY the complete C source file."
        )
        variants = generate_variants(prompt, n=3)
        # At least one variant should differ
        assert any(v != prompt for v in variants)

    def test_single_line_prompt_returns_padded(self) -> None:
        prompt = "Write hello world."
        variants = generate_variants(prompt, n=3)
        assert len(variants) == 3


class TestFindBulletGroups:
    """Tests for bullet group detection."""

    def test_finds_numbered_list(self) -> None:
        lines = ["header", "1. item", "2. item", "3. item", "footer"]
        groups = _find_bullet_groups(lines)
        assert len(groups) == 1
        assert groups[0] == (1, 4)

    def test_finds_dash_list(self) -> None:
        lines = ["header", "- a", "- b", "- c", "footer"]
        groups = _find_bullet_groups(lines)
        assert len(groups) == 1

    def test_no_bullets(self) -> None:
        lines = ["just text", "more text"]
        groups = _find_bullet_groups(lines)
        assert groups == []

    def test_short_list_ignored(self) -> None:
        lines = ["- a", "- b", "end"]
        groups = _find_bullet_groups(lines)
        assert groups == []  # need >= 3 bullets


class TestRephraseImperatives:
    """Tests for imperative verb replacement."""

    def test_replaces_write(self) -> None:
        assert "Implement" in _rephrase_imperatives("Write a function")

    def test_replaces_create(self) -> None:
        assert "Develop" in _rephrase_imperatives("Create a module")

    def test_no_change_when_no_imperatives(self) -> None:
        text = "This is a description."
        assert _rephrase_imperatives(text) == text


class TestRemoveOutputInstruction:
    """Tests for output instruction removal."""

    def test_removes_output_only(self) -> None:
        prompt = "Do something.\nOutput ONLY the complete C file.\nMore text."
        result = _remove_output_instruction(prompt)
        assert "Output ONLY" not in result
        assert "More text" in result

    def test_no_change_when_no_instruction(self) -> None:
        prompt = "Just a normal prompt."
        assert _remove_output_instruction(prompt) == prompt


class TestCalculateRobustness:
    """Tests for robustness score calculation."""

    def test_all_agree_returns_one(self) -> None:
        assert calculate_robustness(True, [True, True, True]) == 1.0

    def test_all_disagree_returns_zero(self) -> None:
        assert calculate_robustness(True, [False, False, False]) == 0.0

    def test_partial_agreement(self) -> None:
        assert calculate_robustness(True, [True, False, True]) == 2 / 3

    def test_empty_variants_returns_one(self) -> None:
        assert calculate_robustness(True, []) == 1.0

    def test_original_false_variants_false(self) -> None:
        assert calculate_robustness(False, [False, False]) == 1.0

    def test_original_false_variants_mixed(self) -> None:
        assert calculate_robustness(False, [True, False]) == 0.5


class TestSensitivityReport:
    """Tests for SensitivityReport model."""

    def test_report_creation(self) -> None:
        cases = [
            CaseSensitivity(
                case_id="case-001",
                original_passed=True,
                variant_results=[True, True],
                robustness=1.0,
            ),
            CaseSensitivity(
                case_id="case-002",
                original_passed=True,
                variant_results=[False, True],
                robustness=0.5,
            ),
        ]
        report = SensitivityReport(
            model="test",
            total_cases=2,
            variants_per_case=2,
            avg_robustness=0.75,
            cases=cases,
            most_sensitive=["case-002"],
            most_robust=["case-001"],
        )
        assert report.avg_robustness == 0.75
        assert len(report.most_sensitive) == 1
