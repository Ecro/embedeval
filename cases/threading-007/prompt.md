Write a Zephyr RTOS application implementing thread-safe one-time singleton initialization using the double-check locking pattern.

Requirements:
1. Include zephyr/kernel.h
2. Declare a k_mutex named init_mutex (K_MUTEX_DEFINE)
3. Declare a static bool variable initialized = false
4. Declare a static resource struct with at least one field (e.g., uint32_t value)
5. Implement get_resource() that returns a pointer to the singleton resource:
   - FIRST check: if (initialized) return &resource;  (fast path, no lock)
   - Lock init_mutex with k_mutex_lock(&init_mutex, K_FOREVER)
   - SECOND check: if (!initialized) { ... init ... initialized = true; }  (under lock)
   - Unlock init_mutex with k_mutex_unlock(&init_mutex)
   - Return &resource
6. Implement two threads that both call get_resource() and use the result
7. In main(): start threads (K_THREAD_DEFINE), sleep forever

WHY double-check: The first check avoids locking every call (performance). The second check under the lock prevents two threads both passing the first check and initializing twice.

Do NOT use:
- Global initialization at define-time only (must use runtime init pattern)
- k_once_t if it exists — implement the pattern manually

Use the Zephyr API: K_MUTEX_DEFINE, k_mutex_lock, k_mutex_unlock.

Output ONLY the complete C source file.
