"""Tests for src/embedeval/failure_factors.py.

Covers the extracted factor-table parser and the new
check-to-category mapper. Duplicate-check behavior (first-category
wins) is exercised with synthetic markdown because the live
FAILURE-FACTORS.md legitimately contains a handful of shared-use
checks (e.g. `counter_is_volatile` in both B and D).
"""

from __future__ import annotations

from embedeval.failure_factors import (
    FACTORS_DOC,
    load_check_category_map,
    load_factors,
    parse_check_category_map,
    parse_factors,
)


def test_parse_factors_extracts_all_six_categories() -> None:
    """Sanity: the live FAILURE-FACTORS.md still yields A–F categories."""
    categories = load_factors()
    letters = [c.letter for c in categories]
    assert letters == ["A", "B", "C", "D", "E", "F"], letters
    for c in categories:
        assert len(c.factors) >= 1, f"category {c.letter} empty"


def test_parse_factors_total_is_42() -> None:
    """Version 1.5 of FAILURE-FACTORS.md declares 42 factors across six
    categories — lock this down so accidental row-drop shows up."""
    categories = load_factors()
    total = sum(len(c.factors) for c in categories)
    assert total == 42, total


def test_parse_factors_preserves_row_fields() -> None:
    """A2 is High + Empirical and well-known — locks field mapping."""
    categories = load_factors()
    a = next(c for c in categories if c.letter == "A")
    a2 = next(f for f in a.factors if f.factor_id == "A2")
    assert a2.strength == "High"
    assert a2.evidence == "Empirical"
    assert "init" in a2.name.lower()


def test_parse_check_category_map_covers_known_checks() -> None:
    """Spot-check the mapping against factor lines verified by hand.

    `volatile_error_flag` is D-category. `dma_config_called` is A.
    `init_error_path_cleanup` is E. `k_sleep_with_k_msec` is F.
    """
    mapping = load_check_category_map()
    assert mapping["volatile_error_flag"] == "D"
    assert mapping["dma_config_called"] == "A"
    assert mapping["init_error_path_cleanup"] == "E"
    assert mapping["k_sleep_with_k_msec"] == "F"
    assert mapping["deadline_miss_detected"] == "B"
    assert mapping["stack_overflow_protection_configured"] == "C"


def test_parse_check_category_map_first_category_wins_for_duplicates() -> None:
    """Shared-use checks appear in multiple categories' mapping lines.
    Parser walks A→F in order and the first letter wins — matches the
    PLAN R6 precedent rule."""
    # counter_is_volatile is mapped under both B and D in the live doc;
    # the order-based precedence rule must resolve it to B.
    mapping = load_check_category_map()
    assert mapping["counter_is_volatile"] == "B"
    # dma_header_included is in both A and F — A must win.
    assert mapping["dma_header_included"] == "A"


def test_parse_check_category_map_synthetic_duplicate_precedence() -> None:
    """Explicit synthetic input locks the precedence rule even when the
    live doc's mapping lines don't demonstrate it."""
    synthetic = (
        "## A. Alpha\n"
        "\n"
        "| A1 | Foo | High | Empirical | desc |\n"
        "\n"
        "**EmbedEval checks mapped:** `shared_check`, `a_only`\n"
        "\n"
        "## B. Beta\n"
        "\n"
        "| B1 | Bar | High | Empirical | desc |\n"
        "\n"
        "**EmbedEval checks mapped:** `shared_check`, `b_only`\n"
    )
    mapping = parse_check_category_map(synthetic)
    assert mapping["shared_check"] == "A"
    assert mapping["a_only"] == "A"
    assert mapping["b_only"] == "B"


def test_parse_check_category_map_ignores_non_mapping_lines() -> None:
    """Content outside the `**EmbedEval checks mapped:**` trailer
    must not leak into the mapping — backtick-wrapped words in factor
    descriptions are especially tempting false positives."""
    synthetic = (
        "## A. Alpha\n"
        "\n"
        "| A1 | Uses `not_a_check_name` in desc | High | Empirical | "
        "the `backticked_word` appears in prose |\n"
        "\n"
        "**EmbedEval checks mapped:** `real_check_one`, `real_check_two`\n"
    )
    mapping = parse_check_category_map(synthetic)
    assert set(mapping) == {"real_check_one", "real_check_two"}


def test_factors_doc_path_points_at_existing_file() -> None:
    """Regression: FACTORS_DOC must resolve to an actual file — broken
    relative paths showed up when the parser moved from scripts/ to
    src/ in Phase 1."""
    assert FACTORS_DOC.is_file(), str(FACTORS_DOC)


def test_parse_factors_and_map_agree_on_categories() -> None:
    """Every check in the mapping must resolve to an A-F letter that
    parse_factors also produced — cross-consistency check."""
    factor_letters = {c.letter for c in load_factors()}
    mapping = load_check_category_map()
    for check, letter in mapping.items():
        assert letter in factor_letters, (
            f"check {check} mapped to category {letter} "
            f"which parse_factors does not know about"
        )


def test_parse_factors_accepts_raw_markdown() -> None:
    """parse_factors shouldn't need the disk — synthetic input works."""
    synthetic = (
        "## A. Alpha\n"
        "\n"
        "| A1 | Foo | High | Empirical | desc |\n"
        "| A2 | Bar | Med | Research | desc |\n"
        "\n"
        "## Summary\n"
        "\n"
        "| something | else |\n"
    )
    cats = parse_factors(synthetic)
    assert len(cats) == 1
    assert cats[0].letter == "A"
    assert [f.factor_id for f in cats[0].factors] == ["A1", "A2"]
