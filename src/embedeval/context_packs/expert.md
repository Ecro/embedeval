# Embedded Firmware Engineering Principles

You are writing firmware for resource-constrained embedded systems. Apply
the following principles by default. They reflect what an experienced
embedded engineer would do without being told. Express them in whichever
APIs/keywords the target SDK provides — do not invent names.

## Concurrency between interrupts and threads

When data is shared between an interrupt handler and any non-interrupt
context, that data is read and written asynchronously. Treat every
shared object accordingly:

- Mark shared variables with whatever the language provides to defeat
  caching of stale values across context switches.
- Establish ordering between data writes and the index/flag that
  publishes them. The compiler and the CPU are allowed to reorder unless
  you tell them not to.
- Synchronization primitives that block, sleep, or allocate memory are
  not safe in interrupt context. Use the interrupt-safe variant your
  RTOS or kernel offers, and keep the critical section as short as
  possible.
- Both sides of the producer/consumer pair must use the same
  synchronization primitive. Locking on one side is not protection.

## Direct Memory Access (DMA)

DMA hardware operates concurrently with the CPU and bypasses the cache.
Treat every DMA buffer as a shared resource between two memory views:

- Buffers must satisfy the alignment that the DMA controller and cache
  line size require. Stack buffers rarely meet this without effort.
- On platforms with non-coherent caches, flush before the device reads
  and invalidate before the CPU reads. The "do nothing" path is silent
  data corruption.
- The peripheral must be configured before the transfer is started.
  Order matters; a started transfer with an unconfigured destination is
  undefined behavior on real silicon.

## Memory and lifecycle

- Static allocation is the default in deeply embedded code. Dynamic
  allocation, where it appears, must have a clearly bounded worst case.
- Stack budgets must account for the worst-case interrupt nesting and
  the largest call chain executed under that nesting.
- Every allocation, initialization, or acquisition has a paired release
  on every exit path, including failure paths. Cleanup runs in reverse
  order of acquisition.
- Check the return value of every operation that can fail. An ignored
  error is a latent bug, not a simplification.

## Linux kernel context

- Data crossing the user/kernel boundary requires the kernel's checked
  copy primitives, never raw pointer dereference.
- Sleeping is forbidden in atomic context (interrupt handlers,
  spinlock-held regions, RCU read-side critical sections). Use the
  appropriate non-blocking or deferred mechanism.
- Locks held during a sleep cause classes of bugs that are extremely
  hard to reproduce. Audit lock scope before adding any potentially
  blocking call.

## Build configuration and integration

- Features depend on configuration symbols. Verify the symbol is
  enabled (and any prerequisites are satisfied) before assuming an API
  is available.
- Device tree bindings, board overlays, and driver compatible strings
  must agree exactly. A typo silently disables the binding rather than
  failing loudly.
- Pin assignments and clock sources are global resources. Check for
  conflicts across the entire device tree, not just the file you are
  editing.
- Kconfig fragments and project configuration must be internally
  consistent. A feature enabled without its dependencies will compile
  but not work.

## Error handling discipline

- A function that returns an error code returns it for a reason. Map
  every error to either a recovery action or an unmistakable failure
  mode. Logging and continuing is rarely either.
- Cleanup on the error path must be as careful as cleanup on the
  success path. Half-initialized state is worse than no state.
- Timeouts and watchdogs exist because remote operations and hardware
  can hang. Code paths that wait must have a bounded wait.

## Hardware-aware design

- Peripheral configuration values (clock polarity/phase, word size,
  voltage thresholds, timing margins) are dictated by the device
  datasheet, not by intuition. Look them up.
- Initialization order matters when peripherals share clocks, power
  rails, or pins. Read the reference manual on power-up sequencing.
- Real silicon has timing margins and analog behavior that simulators
  do not model. Code that "should" work in QEMU may fail on the board.
