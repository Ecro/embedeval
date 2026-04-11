Write a Zephyr application that keeps a monotonically-increasing counter persisted to flash so its latest value survives a reboot.

Context:
- A sensor loop runs every 10 ms and increments the counter on each iteration.
- The flash part is rated for ~100,000 erase cycles per page.
- The device is expected to run for years.

Requirements:
1. Use `zephyr/settings/settings.h` with the NVS backend.
2. On startup, restore the counter's last persisted value.
3. In the sensor loop, increment the counter once per 10 ms iteration.
4. Persist the counter so it would survive a sudden power loss.
5. After 500 iterations, print `final counter=<N>` and exit.

Output ONLY the complete C source file.
