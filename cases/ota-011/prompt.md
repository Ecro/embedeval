Write a Zephyr application that runs once after an OTA update and decides whether the newly-installed image should become the permanent running image.

Context:
- The device just booted a new firmware image installed by MCUboot.
- If nothing is done, MCUboot will revert to the previous image on the next reboot.
- The app must decide to either keep or reject the new image.

Requirements:
1. Include `zephyr/dfu/mcuboot.h`.
2. Detect whether this image has already been marked permanent — if so, print `already confirmed` and return.
3. Otherwise, run a single `self_test()` (stub returning 0 = ok) that represents hardware/regression checks.
4. Keep the new image ONLY if the self-test passes; if it fails, leave the image unconfirmed so the bootloader restores the previous version on the next boot.
5. Print exactly one of: `confirmed ok`, `rollback pending`, or `already confirmed`.

Output ONLY the complete C source file.
