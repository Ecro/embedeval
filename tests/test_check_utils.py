"""Tests for enhanced check_utils functions."""

from embedeval.check_utils import (
    blank_comments,
    check_api_in_function,
    check_cleanup_reverse_order,
    check_qualifier_on_variable,
    check_return_after_error,
    expand_string_defines,
    find_in_code,
    find_in_yocto,
    function_bodies,
    has_any_api_call,
    has_api_call,
    has_word,
    ordered_in_same_function,
)


class TestHasAnyApiCall:
    """Check for one of several equivalent API spellings."""

    def test_first_alternative_matches(self) -> None:
        assert has_any_api_call(
            "ret = dma_config(dev, ch, &cfg);", ["dma_config", "dma_configure"]
        )

    def test_second_alternative_matches(self) -> None:
        """Real case from Context Quality Mode trade-off analysis (2026-04-18):
        Haiku with expert pack used dma_configure() instead of dma_config(),
        which is functionally equivalent but failed the older brittle check."""
        assert has_any_api_call(
            "ret = dma_configure(dev, ch, &cfg);",
            ["dma_config", "dma_configure"],
        )

    def test_neither_alternative_misses(self) -> None:
        assert not has_any_api_call(
            "ret = dma_setup(dev, ch);", ["dma_config", "dma_configure"]
        )

    def test_empty_list_returns_false(self) -> None:
        assert not has_any_api_call("anything", [])


class TestHasWord:
    """Word-boundary matching tests."""

    def test_exact_match(self) -> None:
        assert has_word("volatile int flag;", "volatile")

    def test_rejects_substring(self) -> None:
        assert not has_word("__copy_to_user(buf)", "copy_to_user")

    def test_accepts_word_boundary(self) -> None:
        assert has_word("ret = copy_to_user(buf)", "copy_to_user")

    def test_rejects_prefix_match(self) -> None:
        assert not has_word("nonvolatile_flag = 1;", "volatile")


class TestHasApiCall:
    """API call detection with word boundaries."""

    def test_normal_call(self) -> None:
        assert has_api_call("copy_to_user(buf, src, n)", "copy_to_user")

    def test_rejects_double_underscore_variant(self) -> None:
        assert not has_api_call("__copy_to_user(buf, src, n)", "copy_to_user")

    def test_with_paren_in_api(self) -> None:
        assert has_api_call("delay(100);", "delay(")

    def test_with_spaces(self) -> None:
        assert has_api_call("copy_to_user  (buf, src, n)", "copy_to_user")


class TestCheckQualifierOnVariable:
    """Scope-aware qualifier checks."""

    def test_volatile_on_correct_variable(self) -> None:
        code = "volatile int flag = 0;\nint counter = 0;"
        assert check_qualifier_on_variable(code, "volatile", r"flag")

    def test_volatile_on_wrong_variable(self) -> None:
        code = "volatile int other_var = 0;\nint flag = 0;"
        assert not check_qualifier_on_variable(code, "volatile", r"flag")

    def test_volatile_with_pointer(self) -> None:
        code = "volatile uint32_t *shared_data;"
        assert check_qualifier_on_variable(code, "volatile", r"shared_data")

    def test_ignores_comments(self) -> None:
        code = "// volatile int flag;\nint flag = 0;"
        assert not check_qualifier_on_variable(code, "volatile", r"flag")


class TestCheckReturnAfterError:
    """Error handling flow checks."""

    def test_return_present(self) -> None:
        code = """
        ret = gpio_pin_configure(dev, pin, flags);
        if (ret < 0) {
            printk("error");
            return ret;
        }
        """
        assert check_return_after_error(code)

    def test_goto_present(self) -> None:
        code = """
        if (ret != 0) {
            goto cleanup;
        }
        """
        assert check_return_after_error(code)

    def test_no_return_after_error(self) -> None:
        code = """
        if (ret < 0) {
            printk("error detected");
        }
        // continues execution...
        """
        assert not check_return_after_error(code)

    def test_no_error_blocks(self) -> None:
        assert check_return_after_error("int main() { return 0; }")


class TestCheckApiInFunction:
    """Scope-aware API in function body checks."""

    def test_api_in_correct_function(self) -> None:
        code = """
        void my_handler(void) {
            k_spin_lock(&lock);
            shared++;
            k_spin_unlock(&lock);
        }
        """
        assert check_api_in_function(code, "k_spin_lock", "my_handler")

    def test_api_not_in_function(self) -> None:
        code = """
        void other_func(void) {
            k_spin_lock(&lock);
        }
        void my_handler(void) {
            shared++;
        }
        """
        assert not check_api_in_function(code, "k_spin_lock", "my_handler")

    def test_function_not_found(self) -> None:
        code = "void other(void) { k_spin_lock(&lock); }"
        assert not check_api_in_function(code, "k_spin_lock", "nonexistent")


class TestCheckCleanupReverseOrder:
    """Reverse-order cleanup verification."""

    def test_correct_reverse_order(self) -> None:
        code = """
        a_init();
        b_init();
        if (ret < 0) {
            b_cleanup();
            a_cleanup();
        }
        """
        # cleanup calls not named same as init calls, so nothing matched
        assert check_cleanup_reverse_order(code, ["a_cleanup", "b_cleanup"])

    def test_wrong_order_detected(self) -> None:
        code = """
        if (ret < 0) {
            a_cleanup();
            b_cleanup();
        }
        """
        # init order was a,b → cleanup should be b,a but we see a,b → wrong
        assert not check_cleanup_reverse_order(code, ["a_cleanup", "b_cleanup"])

    def test_no_error_blocks(self) -> None:
        code = "int main() { return 0; }"
        assert check_cleanup_reverse_order(code, ["a_init", "b_init"])


class TestBlankComments:
    """Comment blanking must preserve offsets so window slices stay valid."""

    def test_length_preserved(self) -> None:
        code = "int a; /* comment */ int b;\n// trailing\nint c;\n"
        assert len(blank_comments(code)) == len(code)

    def test_comment_text_removed(self) -> None:
        blanked = blank_comments("int a; /* boot_write_img_confirmed */ int b;")
        assert "boot_write_img_confirmed" not in blanked
        assert "int a;" in blanked and "int b;" in blanked

    def test_newlines_survive_block_comment(self) -> None:
        code = "a;\n/* two\n   lines */\nb;\n"
        assert blank_comments(code).count("\n") == code.count("\n")

    def test_offset_valid_in_original(self) -> None:
        code = "/* mentions foo() first */\nvoid foo(void) { bar(); }\n"
        pos = find_in_code(code, "foo(")
        assert code[pos : pos + 4] == "foo("


class TestFindInCode:
    """Ordering checks must ignore API mentions inside comments."""

    def test_comment_mention_ignored(self) -> None:
        code = "/* call boot_write_img_confirmed() after check */\n" "int x = 0;\n"
        assert find_in_code(code, "boot_write_img_confirmed") == -1

    def test_real_call_found(self) -> None:
        code = "// note\nret = boot_write_img_confirmed();\n"
        assert find_in_code(code, "boot_write_img_confirmed") != -1

    def test_ordering_not_inverted_by_header_comment(self) -> None:
        code = (
            "/* Unless the app calls boot_write_img_confirmed(), it reverts. */\n"
            "if (boot_is_img_confirmed()) { return 0; }\n"
            "ret = boot_write_img_confirmed();\n"
        )
        check = find_in_code(code, "boot_is_img_confirmed")
        write = find_in_code(code, "boot_write_img_confirmed")
        assert -1 not in (check, write)
        assert check < write

    def test_absent_needle_is_minus_one(self) -> None:
        assert find_in_code("int main(void) { return 0; }", "k_sleep") == -1


class TestFindInYocto:
    """Recipe lookups strip # comments but keep URIs."""

    def test_commented_line_ignored(self) -> None:
        recipe = '# git apply ${WORKDIR}/x.patch\nA = "1"\n'
        assert find_in_yocto(recipe, "git apply") == -1

    def test_uri_preserved(self) -> None:
        recipe = 'SRC_URI = "file://fix.patch"\n'
        assert find_in_yocto(recipe, "file://fix.patch") != -1

    def test_real_directive_found(self) -> None:
        assert find_in_yocto('do_compile() {\n\tgit apply x\n}\n', "git apply") != -1


class TestExpandStringDefines:
    """String macros are equivalent to the literals they name."""

    def test_macro_use_site_expanded(self) -> None:
        code = '#define SPI_DEVICE "/dev/spidev0.0"\nfd = open(SPI_DEVICE, O_RDWR);\n'
        assert 'open("/dev/spidev0.0", O_RDWR)' in expand_string_defines(code)

    def test_numeric_define_untouched(self) -> None:
        code = "#define COUNT 10\nfor (int i = 0; i < COUNT; i++) {}\n"
        assert expand_string_defines(code) == code

    def test_no_defines_returns_input(self) -> None:
        code = 'fd = open("/dev/spidev0.0", O_RDWR);\n'
        assert expand_string_defines(code) == code

    def test_longest_name_wins(self) -> None:
        code = (
            '#define NAME "short"\n'
            '#define NAME_LONG "long"\n'
            "a = NAME_LONG;\n"
        )
        assert 'a = "long";' in expand_string_defines(code)


class TestFunctionBodies:
    """Per-function views for order checks that must survive refactoring."""

    def test_names_and_nesting(self) -> None:
        code = (
            "static void helper(void)\n{\n\tif (x) {\n\t\ty();\n\t}\n}\n"
            "int main(void)\n{\n\thelper();\n\treturn 0;\n}\n"
        )
        bodies = dict(function_bodies(code))
        assert set(bodies) == {"helper", "main"}
        assert "y();" in bodies["helper"]
        assert "helper();" in bodies["main"]

    def test_commented_signature_ignored(self) -> None:
        code = "/* void ghost(void) { } */\nint main(void)\n{\n\treturn 0;\n}\n"
        assert [name for name, _ in function_bodies(code)] == ["main"]


class TestOrderedInSameFunction:
    """A helper defined above its caller is not an ordering violation."""

    def test_correct_order_in_one_function(self) -> None:
        code = "int main(void)\n{\n\tuart_callback_set();\n\tuart_rx_enable();\n}\n"
        assert ordered_in_same_function(code, "uart_callback_set", "uart_rx_enable")

    def test_wrong_order_in_one_function(self) -> None:
        code = "int main(void)\n{\n\tuart_rx_enable();\n\tuart_callback_set();\n}\n"
        assert not ordered_in_same_function(
            code, "uart_callback_set", "uart_rx_enable"
        )

    def test_helper_above_caller_still_ordered(self) -> None:
        code = (
            "static void rearm(void)\n{\n\tuart_rx_enable();\n}\n"
            "int main(void)\n{\n\tuart_callback_set();\n\tuart_rx_enable();\n}\n"
        )
        assert ordered_in_same_function(code, "uart_callback_set", "uart_rx_enable")

    def test_missing_call_is_false(self) -> None:
        code = "int main(void)\n{\n\tuart_rx_enable();\n}\n"
        assert not ordered_in_same_function(
            code, "uart_callback_set", "uart_rx_enable"
        )
