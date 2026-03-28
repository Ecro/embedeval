Write a Linux kernel platform driver that controls a GPIO output using the modern gpiolib consumer API.

Requirements:
1. Define proper module metadata (license, author, description)
2. Implement a platform driver with probe and remove functions
3. In probe, request a GPIO descriptor, set it as output, toggle it, and read back the value
4. Use managed device resource APIs so cleanup is automatic on driver removal
5. Log the GPIO state transitions

Output ONLY the complete C source file.
