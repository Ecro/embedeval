Write a Zephyr RTOS application that uses the thread stack analyzer to report per-thread stack usage.

Requirements:
1. Include zephyr/kernel.h and zephyr/debug/thread_analyzer.h
2. Enable CONFIG_THREAD_ANALYZER=y in prj.conf (include the prj.conf content as a comment block at the top of the C file, like: /* prj.conf: CONFIG_THREAD_ANALYZER=y ... */)
3. Define a secondary thread stack: K_THREAD_STACK_DEFINE(worker_stack, 512)
4. Define a struct k_thread worker_thread
5. Implement a worker thread function that does some work (e.g., a counting loop) then calls k_sleep(K_FOREVER)
6. In main():
   - Create the worker thread with k_thread_create(), set it runnable
   - Sleep for 100ms with k_sleep(K_MSEC(100)) to let threads run
   - Call thread_analyzer_print() to print stack usage for all threads
   - Print "Stack analysis complete" with printk
7. The prj.conf comment block must include:
   - CONFIG_THREAD_ANALYZER=y
   - CONFIG_THREAD_ANALYZER_USE_PRINTK=y
   - CONFIG_THREAD_NAME=y

IMPORTANT: thread_analyzer_print() must be called AFTER threads have run.
Calling it immediately at boot gives zero usage (no stack has been used yet).
The correct API is thread_analyzer_print() — NOT thread_analyze() or
stack_analyzer_print().

Output ONLY the complete C source file (with prj.conf settings as a comment).
