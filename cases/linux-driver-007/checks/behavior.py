"""Behavioral checks for Linux DMA-coherent buffer driver."""

import re

from embedeval.check_utils import (
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA buffer driver behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: No malloc() — C userspace function in kernel code is wrong
    has_malloc = "malloc(" in generated_code and "dma_alloc" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_userspace_malloc",
            passed=not has_malloc,
            expected="No userspace malloc() in kernel DMA driver",
            actual="clean" if not has_malloc else "HALLUCINATION: malloc() used in kernel code!",
            check_type="constraint",
        )
    )

    # Check 2: No vmalloc() for DMA — not physically contiguous
    has_vmalloc = "vmalloc(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_vmalloc_for_dma",
            passed=not has_vmalloc,
            expected="No vmalloc() for DMA buffers (not physically contiguous)",
            actual="clean" if not has_vmalloc else "WRONG: vmalloc not suitable for DMA!",
            check_type="constraint",
        )
    )

    # Check 3: No plain kmalloc() as the DMA allocation method
    has_kmalloc_only = (
        "kmalloc(" in generated_code and "dma_alloc_coherent" not in generated_code
    )
    details.append(
        CheckDetail(
            check_name="no_kmalloc_instead_of_dma_alloc",
            passed=not has_kmalloc_only,
            expected="dma_alloc_coherent() used, not kmalloc() alone for DMA",
            actual="clean" if not has_kmalloc_only else "WRONG: kmalloc used instead of dma_alloc_coherent!",
            check_type="constraint",
        )
    )

    # Check 4: Allocation failure handled with -ENOMEM
    has_enomem = "ENOMEM" in generated_code
    details.append(
        CheckDetail(
            check_name="enomem_on_alloc_failure",
            passed=has_enomem,
            expected="-ENOMEM returned when dma_alloc_coherent fails",
            actual="present" if has_enomem else "missing (allocation failure not handled)",
            check_type="constraint",
        )
    )

    # Check 5: alloc and free are both present (balanced)
    has_alloc = "dma_alloc_coherent" in generated_code
    has_free = "dma_free_coherent" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_alloc_free_balanced",
            passed=has_alloc and has_free,
            expected="dma_alloc_coherent and dma_free_coherent both present",
            actual=f"alloc={has_alloc}, free={has_free}",
            check_type="constraint",
        )
    )

    # Check 6: dev_set_drvdata used to store per-device state
    has_drvdata = "dev_set_drvdata" in generated_code or "devm_" in generated_code
    details.append(
        CheckDetail(
            check_name="per_device_data_stored",
            passed=has_drvdata,
            expected="dev_set_drvdata() or devm_ used to store per-device data",
            actual="present" if has_drvdata else "missing (global state is not multi-device safe)",
            check_type="constraint",
        )
    )

    # Check 7: DMA allocation failure handled in error path
    # LLM failure: dma_alloc_coherent fails but driver continues using NULL pointer
    # Pattern: if (!virt_addr) { return -ENOMEM; } or if (!dev->virt_addr) { ... }
    dma_error_handled = bool(
        re.search(
            r'if\s*\(\s*!\s*\w[\w.>-]*\s*\)\s*\{[^}]*(?:ENOMEM|return\s+-)',
            generated_code,
        )
    ) or (
        "ENOMEM" in generated_code
        and bool(re.search(r'dma_alloc_coherent[^;]+;[^}]*if\s*\(\s*!', generated_code, re.DOTALL))
    )
    details.append(
        CheckDetail(
            check_name="dma_alloc_error_handled",
            passed=dma_error_handled,
            expected="DMA allocation failure path returns -ENOMEM",
            actual="present" if dma_error_handled else "DMA allocation failure may not be handled",
            check_type="constraint",
        )
    )

    # Check 8: No Zephyr API contamination in Linux DMA driver
    zephyr_apis = ["k_work_submit", "k_thread_create", "K_THREAD_DEFINE",
                   "k_mutex_lock", "k_sleep("]
    has_zephyr = any(api in generated_code for api in zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_zephyr_apis",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs in Linux DMA driver",
            actual="clean" if not has_zephyr else "WRONG PLATFORM: Zephyr APIs found",
            check_type="constraint",
        )
    )

    return details
