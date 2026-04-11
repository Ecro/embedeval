Write a Zephyr RTOS application demonstrating nested interrupt priority management.

Target board: native_sim (no real NVIC — use `irq_offload()` for IRQ dispatch).

Requirements:
1. Include `zephyr/kernel.h`, `zephyr/irq.h`, and `zephyr/irq_offload.h`
2. Define two IRQ numbers (software-generated, e.g. 5 and 6)
3. Assign DIFFERENT priorities to the two interrupts (e.g., priority 1 and priority 3)
4. Implement two ISR handlers:
   - low_prio_isr: prints "Low priority ISR running", does short work, prints "Low priority ISR done"
   - high_prio_isr: prints "High priority ISR running", prints "High priority ISR done"
5. Connect both ISRs using IRQ_CONNECT or irq_connect_dynamic
6. Enable both interrupts with irq_enable()
7. In main(): after printing "Both IRQs enabled: low priority=... high priority=...", dispatch both handlers in IRQ context via `irq_offload(handler, NULL)` — this is the native_sim way to exercise an ISR without real NVIC hardware

Rules:
- DO NOT use irq_lock()/irq_unlock() to manage priority — use proper IRQ priority levels
- DO NOT use k_sched_lock() — that only affects thread scheduling, not ISR preemption
- ISR bodies MUST be short (no loops, no k_sleep, no blocking calls)
- Priorities MUST be numerically different (lower number = higher priority in ARM)
- Do NOT use POSIX APIs (pthread_setschedprio etc.)

The key concept: high_prio_isr CAN preempt low_prio_isr because it has a lower priority NUMBER.

Use the Zephyr API: IRQ_CONNECT, irq_enable, irq_offload.

Output ONLY the complete C source file.
