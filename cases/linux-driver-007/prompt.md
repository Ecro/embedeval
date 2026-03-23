Write a Linux kernel platform driver that allocates a DMA-coherent buffer.

Requirements:
1. Include linux/module.h, linux/platform_device.h, linux/dma-mapping.h, linux/slab.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Implement a platform_driver with probe and remove functions
4. In probe():
   - Allocate a DMA-coherent buffer with dma_alloc_coherent()
     (size: 4096 bytes, flags: GFP_KERNEL)
   - Store the returned virtual address and DMA handle (dma_addr_t)
   - Check for allocation failure and return -ENOMEM on failure
   - Print the DMA address with pr_info
5. In remove():
   - Free the DMA buffer with dma_free_coherent() using the stored handle
   - This MUST be called to avoid memory leaks
6. Store per-device data (virtual address, dma address, size) in a struct
   and attach to device with dev_set_drvdata()
7. Register with platform_driver_register() in module_init
8. Unregister with platform_driver_unregister() in module_exit

CRITICAL: Use dma_alloc_coherent() — NEVER use kmalloc() or vmalloc() for DMA buffers.
DMA buffers require physical contiguity and cache coherency that kmalloc/vmalloc cannot guarantee.

Output ONLY the complete C source file.
