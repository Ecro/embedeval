"""Behavioral checks for Zephyr memory domain with partitions."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate memory domain behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: k_mem_domain_init called before k_mem_domain_add_partition
    # (LLM failure: calling add_partition on uninitialized domain = kernel assertion)
    init_pos = generated_code.find("k_mem_domain_init")
    add_part_pos = generated_code.find("k_mem_domain_add_partition")
    init_before_add = (
        init_pos != -1 and add_part_pos != -1 and init_pos < add_part_pos
    )
    details.append(
        CheckDetail(
            check_name="domain_init_before_add_partition",
            passed=init_before_add,
            expected="k_mem_domain_init() before k_mem_domain_add_partition()",
            actual="correct order" if init_before_add else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: k_mem_domain_add_thread called after k_thread_create
    # (LLM failure: domain assigned before thread exists)
    thread_create_pos = generated_code.find("k_thread_create")
    add_thread_pos = generated_code.find("k_mem_domain_add_thread")
    thread_then_domain = (
        thread_create_pos != -1
        and add_thread_pos != -1
        and thread_create_pos < add_thread_pos
    )
    details.append(
        CheckDetail(
            check_name="thread_created_before_domain_assign",
            passed=thread_then_domain,
            expected="k_thread_create() before k_mem_domain_add_thread()",
            actual="correct order" if thread_then_domain else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: K_APPMEM_PARTITION_DEFINE used to define partition
    # (LLM failure: using K_MEM_PARTITION_DEFINE which is the old/wrong API)
    has_appmem_partition = "K_APPMEM_PARTITION_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="appmem_partition_define_used",
            passed=has_appmem_partition,
            expected="K_APPMEM_PARTITION_DEFINE used for app memory partition",
            actual="present" if has_appmem_partition else "missing or wrong macro",
            check_type="constraint",
        )
    )

    # Check 4: K_APP_DMEM used to place data in partition
    # (LLM failure: declares partition but puts data in regular .data section)
    has_app_dmem = "K_APP_DMEM" in generated_code
    details.append(
        CheckDetail(
            check_name="k_app_dmem_used",
            passed=has_app_dmem,
            expected="K_APP_DMEM() used to place shared data in partition section",
            actual="present" if has_app_dmem else "MISSING (data not in partition!)",
            check_type="constraint",
        )
    )

    # Check 5: Thread created with K_USER flag for user-mode
    # (LLM failure: creating thread without K_USER — memory domains only apply to user threads)
    has_k_user = "K_USER" in generated_code
    details.append(
        CheckDetail(
            check_name="thread_has_k_user_flag",
            passed=has_k_user,
            expected="K_USER flag in k_thread_create for user-mode thread",
            actual="present" if has_k_user else "MISSING (domain isolation requires K_USER!)",
            check_type="constraint",
        )
    )

    # Check 6: k_mem_domain_add_thread called (thread assigned to domain)
    # (LLM failure: creates domain and partition but never assigns thread)
    has_add_thread = "k_mem_domain_add_thread" in generated_code
    details.append(
        CheckDetail(
            check_name="thread_added_to_domain",
            passed=has_add_thread,
            expected="k_mem_domain_add_thread() called to assign thread to domain",
            actual="present" if has_add_thread else "MISSING (thread not isolated!)",
            check_type="constraint",
        )
    )

    return details
