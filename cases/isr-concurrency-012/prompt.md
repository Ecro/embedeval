Write a Zephyr application where an ISR and a thread share and mutate the same data structure.

Requirements:
1. Declare a static global `struct { uint32_t count; uint32_t last_value; }` shared between the ISR and a worker thread.
2. Use `irq_offload()` in main to simulate 5 ISR fires; each fire increments `count` and sets `last_value` to `count * 10`.
3. The worker thread periodically reads both fields atomically (they must be observed as a consistent pair — the reader must not see `count` from one fire and `last_value` from another).
4. The chosen synchronization primitive must be callable from both ISR and thread contexts WITHOUT blocking or deadlocking the ISR.
5. After 5 fires the thread prints `final count=N value=M` and exits.

Output ONLY the complete C source file.
