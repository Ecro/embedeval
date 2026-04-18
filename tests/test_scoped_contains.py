"""Tests for scoped_contains helper (P2 of PLAN-hiloop-transpile-readiness).

Verifies that substring checks run against properly-scoped code:
- comments stripped (default)
- string literals stripped (default)
- raw-mode opt-out available
"""

import pytest

from embedeval.check_utils import (
    scoped_contains,
    strip_string_literals,
)


class TestStripStringLiterals:
    def test_double_quoted_literal_content_removed(self) -> None:
        code = 'printk("use k_malloc here");'
        assert "k_malloc" not in strip_string_literals(code)

    def test_char_literal_content_removed(self) -> None:
        code = "char c = 'k';"
        out = strip_string_literals(code)
        assert "'k'" not in out
        # Quotes sentinel kept
        assert "''" in out

    def test_escape_sequence_inside_literal(self) -> None:
        code = r'printk("escaped \" quote k_malloc inside");'
        out = strip_string_literals(code)
        assert "k_malloc" not in out

    def test_code_outside_literals_preserved(self) -> None:
        code = 'void *p = k_malloc(64); printk("msg");'
        out = strip_string_literals(code)
        assert "k_malloc" in out
        assert "printk" in out


class TestScopedContainsDefault:
    """Default scope='stripped' must ignore comments AND string literals."""

    def test_hit_in_real_code(self) -> None:
        code = "void *p = k_malloc(64);"
        assert scoped_contains(code, "k_malloc")

    def test_miss_when_only_in_line_comment(self) -> None:
        code = "void f(void) { /* ok */ } // don't use k_malloc"
        assert not scoped_contains(code, "k_malloc")

    def test_miss_when_only_in_block_comment(self) -> None:
        code = "/* k_malloc is forbidden */ int main(void) { return 0; }"
        assert not scoped_contains(code, "k_malloc")

    def test_miss_when_only_in_string_literal(self) -> None:
        code = 'int main(void) { printk("use k_malloc"); return 0; }'
        assert not scoped_contains(code, "k_malloc")

    def test_mixed_hit_and_miss(self) -> None:
        """k_malloc in actual code AND in log message — still a hit."""
        code = 'void *p = k_malloc(64); printk("using k_malloc");'
        assert scoped_contains(code, "k_malloc")


class TestScopedContainsCodeOnly:
    """scope='code_only' strips comments but keeps string literals."""

    def test_literal_content_visible(self) -> None:
        code = 'printk("error_flag");'
        assert scoped_contains(code, "error_flag", scope="code_only")

    def test_comment_still_stripped(self) -> None:
        code = "// error_flag in comment"
        assert not scoped_contains(code, "error_flag", scope="code_only")


class TestScopedContainsRaw:
    """scope='raw' is the old unscoped behavior; must match comments/literals."""

    def test_matches_in_comment(self) -> None:
        code = "// k_malloc forbidden"
        assert scoped_contains(code, "k_malloc", scope="raw")

    def test_matches_in_string(self) -> None:
        code = 'printk("k_malloc");'
        assert scoped_contains(code, "k_malloc", scope="raw")


class TestScopedContainsErrors:
    def test_unknown_scope_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown scope"):
            scoped_contains("code", "x", scope="magic")
