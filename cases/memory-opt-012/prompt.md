Write a Zephyr RTOS application that computes CRC-16-CCITT over a data buffer and prints the result.

Requirements:
1. Implement CRC-16-CCITT (polynomial 0x1021, initial value 0xFFFF)
2. The target is a Cortex-M0 with only 16KB of flash — code size must be minimal
3. Compute CRC over a test buffer of at least 16 bytes
4. Print the computed CRC value
5. The implementation must be correct and verifiable against known CRC values
6. Structure the code for a resource-constrained environment

Provide the complete main.c implementation.
