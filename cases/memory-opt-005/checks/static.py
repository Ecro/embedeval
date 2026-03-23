"""Static analysis checks for Zephyr memory domain with partitions."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate memory domain code structure."""
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

    has_appmem_h = "app_memdomain.h" in generated_code
    details.append(
        CheckDetail(
            check_name="app_memdomain_header",
            passed=has_appmem_h,
            expected="app_memdomain.h included",
            actual="present" if has_appmem_h else "missing",
            check_type="exact_match",
        )
    )

    has_partition_define = "K_APPMEM_PARTITION_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="partition_defined",
            passed=has_partition_define,
            expected="K_APPMEM_PARTITION_DEFINE macro used",
            actual="present" if has_partition_define else "missing",
            check_type="exact_match",
        )
    )

    has_mem_domain = "k_mem_domain" in generated_code
    details.append(
        CheckDetail(
            check_name="mem_domain_declared",
            passed=has_mem_domain,
            expected="struct k_mem_domain declared",
            actual="present" if has_mem_domain else "missing",
            check_type="exact_match",
        )
    )

    has_domain_init = "k_mem_domain_init" in generated_code
    details.append(
        CheckDetail(
            check_name="mem_domain_init_called",
            passed=has_domain_init,
            expected="k_mem_domain_init() called",
            actual="present" if has_domain_init else "missing",
            check_type="exact_match",
        )
    )

    has_add_partition = "k_mem_domain_add_partition" in generated_code
    details.append(
        CheckDetail(
            check_name="partition_added_to_domain",
            passed=has_add_partition,
            expected="k_mem_domain_add_partition() called",
            actual="present" if has_add_partition else "missing",
            check_type="exact_match",
        )
    )

    has_add_thread = "k_mem_domain_add_thread" in generated_code
    details.append(
        CheckDetail(
            check_name="thread_added_to_domain",
            passed=has_add_thread,
            expected="k_mem_domain_add_thread() called",
            actual="present" if has_add_thread else "missing",
            check_type="exact_match",
        )
    )

    return details
