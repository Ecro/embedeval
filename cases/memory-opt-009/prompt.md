Write a Zephyr C program that uses BUILD_ASSERT to validate buffer sizes and struct constraints at compile time.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/util.h
2. Define at least two constants: MIN_BUF_SIZE and MAX_BUF_SIZE
3. Define a struct that must fit within a hardware constraint (e.g., DMA alignment, size limit)
4. Use BUILD_ASSERT to validate:
   a. A buffer size is at least MIN_BUF_SIZE:
      BUILD_ASSERT(sizeof(buf) >= MIN_BUF_SIZE, "Buffer too small for protocol")
   b. A struct does not exceed a maximum size:
      BUILD_ASSERT(sizeof(my_struct) <= MAX_STRUCT_SIZE, "Struct exceeds DMA limit")
   c. A struct field is properly aligned (e.g., 4-byte aligned):
      BUILD_ASSERT(offsetof(my_struct, field) % 4 == 0, "Field must be 4-byte aligned")
5. In main(), print the sizes being validated with printk
6. All BUILD_ASSERT conditions must be true (compile-time verification)

IMPORTANT: Use BUILD_ASSERT (Zephyr macro), not runtime assert() or if-statements.
BUILD_ASSERT fails at compile time — the error message in the second argument helps
developers diagnose failures. Do NOT use _Static_assert or static_assert directly.

Output ONLY the complete C source file.
