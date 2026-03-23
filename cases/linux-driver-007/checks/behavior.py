"""Behavioral checks for Linux DMA-coherent buffer driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA buffer driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: No malloc() — C userspace function in kernel code is wrong
    # (LLM hallucination: confusing userspace malloc with kernel allocation)
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

    # Check 2: No vmalloc() for DMA — vmalloc gives virtually contiguous but
    # not physically contiguous memory, wrong for DMA
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
    # (kmalloc may not be DMA-coherent on all architectures)
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

    return details
