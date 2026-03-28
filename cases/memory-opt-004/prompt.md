Write a Zephyr RTOS application that reports per-thread stack usage using the built-in thread analysis facility.

Requirements:
1. Include the necessary headers for kernel and thread analysis
2. The required Kconfig options should be listed as a comment block at the top of the C file (in /* prj.conf: ... */ format), enabling thread analysis with printk output and thread names
3. Define a secondary worker thread with a 512-byte stack
4. The worker thread function should do some work (e.g., a counting loop) then sleep forever
5. In main():
   - Create and start the worker thread
   - Wait long enough for the worker to run and use some stack
   - Print stack usage statistics for all threads
   - Print "Stack analysis complete"

Output ONLY the complete C source file (with prj.conf settings as a comment).
