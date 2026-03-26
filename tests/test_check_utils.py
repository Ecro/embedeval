"""Tests for enhanced check_utils functions."""

from embedeval.check_utils import (
    check_api_in_function,
    check_cleanup_reverse_order,
    check_qualifier_on_variable,
    check_return_after_error,
    has_api_call,
    has_word,
)


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
