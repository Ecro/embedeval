Implement a Zephyr RTOS application that defers heavy processing from an ISR to a thread-context handler.

Requirements:
1. The ISR should do minimal work: record the event and schedule deferred processing
2. The deferred handler runs in thread context and performs the actual processing
3. Track the number of ISR events using an atomic counter
4. The deferred handler should print the accumulated event count
5. In main(), ensure all initialization is done before simulating ISR events, then simulate multiple ISR firings and allow time for deferred processing to complete

Output ONLY the complete C source file.
