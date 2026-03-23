/*
 * ISR-safe lock-free ring buffer for Zephyr RTOS
 * Uses atomic operations for thread-safe producer/consumer access
 */

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>
#include <string.h>

#define RING_BUF_SIZE 256

struct isr_ring_buf {
    uint8_t buffer[RING_BUF_SIZE];
    atomic_t head;
    atomic_t tail;
    uint32_t size;
};

static inline void isr_ring_buf_init(struct isr_ring_buf *rb, uint32_t size)
{
    atomic_set(&rb->head, 0);
    atomic_set(&rb->tail, 0);
    rb->size = (size <= RING_BUF_SIZE) ? size : RING_BUF_SIZE;
    memset(rb->buffer, 0, sizeof(rb->buffer));
}

static inline bool isr_ring_buf_is_empty(const struct isr_ring_buf *rb)
{
    return atomic_get(&rb->head) == atomic_get(&rb->tail);
}

static inline bool isr_ring_buf_is_full(const struct isr_ring_buf *rb)
{
    uint32_t next_head = (atomic_get(&rb->head) + 1) % rb->size;
    return next_head == (uint32_t)atomic_get(&rb->tail);
}

static inline int isr_ring_buf_put(struct isr_ring_buf *rb, uint8_t data)
{
    uint32_t head = atomic_get(&rb->head);
    uint32_t next_head = (head + 1) % rb->size;

    if (next_head == (uint32_t)atomic_get(&rb->tail)) {
        return -1; /* buffer full */
    }

    rb->buffer[head] = data;
    atomic_set(&rb->head, next_head);
    return 0;
}

static inline int isr_ring_buf_get(struct isr_ring_buf *rb, uint8_t *data)
{
    uint32_t tail = atomic_get(&rb->tail);

    if (tail == (uint32_t)atomic_get(&rb->head)) {
        return -1; /* buffer empty */
    }

    *data = rb->buffer[tail];
    atomic_set(&rb->tail, (tail + 1) % rb->size);
    return 0;
}
