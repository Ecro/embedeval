Write a Zephyr RTOS application implementing interrupt-safe deferred logging.

The core principle: ISRs MUST NOT call printk or LOG_* directly — printk can block and is not ISR-safe on all platforms. Instead, the ISR writes a compact log entry to a shared buffer, and a dedicated thread drains the buffer using printk.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/atomic.h
2. Define a log entry struct with: uint32_t timestamp, uint32_t event_id, uint32_t data
3. Define a static ring buffer of log entries (size >= 8)
4. Use atomic_t for write_head and read_tail indices
5. Implement isr_log_write(uint32_t event_id, uint32_t data):
   - Reads write_head atomically
   - Writes entry to buffer[write_head % BUF_SIZE] (entry is shared between ISR and thread)
   - Advances write_head atomically
   - Does NOT call printk or LOG_ERR/LOG_INF/LOG_DBG
6. Implement a log_drain_thread that:
   - Sleeps K_MSEC(10) between drain passes
   - Reads read_tail atomically
   - While read_tail != write_head: reads entry, calls printk, advances read_tail
7. Implement a simulated ISR handler that calls isr_log_write()
8. In main(): start drain thread, simulate ISR calls, sleep forever

CRITICAL RULES:
- NO printk inside isr_log_write (or any ISR path)
- NO LOG_ERR, LOG_INF, LOG_DBG, LOG_WRN inside ISR path
- Buffer entries accessed safely between ISR and thread contexts
- Indices advanced with atomic_set (not plain ++)

Output ONLY the complete C source file.
