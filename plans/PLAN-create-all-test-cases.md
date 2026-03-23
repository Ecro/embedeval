# PLAN: Create All Test Cases (17 Categories, 8 Phases)

**Project:** embedeval
**Task:** Create at least 1 test case for every category with no existing case (17 of 20)
**Priority:** High
**Created:** 2026-03-23

---

## Executive Summary

> **TL;DR:** Create 17 test cases across 8 LLM-sized phases, covering all 20 categories with reference solutions, static checks, and behavioral checks.

### What We're Doing
Creating one pilot test case per uncovered category. Each case includes: `metadata.yaml`, `prompt.md`, `reference/main.c`, `checks/static.py`, `checks/behavior.py`. Cases are grouped by domain similarity to share research context within each phase.

### Why It Matters
Currently only 3 of 20 categories have test cases. The benchmark cannot be used for real evaluation without coverage across all categories.

### Core Purpose: AI Failure Detection in Embedded Development

**이 벤치마크의 핵심 목적은 "AI가 임베디드 개발에서 실제로 어디서 실패하는지"를 정확히 판별하는 것이다.**

테스트 케이스를 설계할 때 반드시 다음을 염두에 둘 것:

**LLM이 임베디드 코드 생성 시 자주 틀리는 패턴:**
- **API 호출 순서 오류** — init → configure → start 같은 순서를 무시하거나 뒤바꿈 (예: wdt_setup 전에 wdt_feed 호출)
- **volatile/atomic 누락** — ISR이나 타이머 콜백에서 접근하는 공유 변수에 volatile 빠뜨림
- **device_is_ready 체크 누락** — 디바이스 사용 전 준비 상태 확인 없이 바로 API 호출
- **에러 핸들링 누락** — API 반환값 체크 없이 진행, 실패 시 무한루프나 크래시 유발
- **raw register 접근** — HAL/API 대신 직접 레지스터 조작, 이식성 파괴
- **DMA 주소 정합성 오류** — source == dest, 또는 alignment 무시
- **I2C/SPI 주소 범위 오류** — 7-bit vs 10-bit 주소 혼동, CS 핀 설정 누락
- **스레드 우선순위 역전** — mutex 사용 시 priority inheritance 미고려
- **ISR 컨텍스트 위반** — ISR에서 blocking 함수 호출 (k_malloc, printk, mutex lock)
- **Kconfig 의존성 누락** — CONFIG_SPI_DMA 활성화하면서 CONFIG_DMA 빠뜨림
- **Device Tree 구문 오류** — compatible 문자열 오타, reg 주소 누락, status 빠뜨림
- **메모리 누수** — alloc 후 free 경로 누락, 특히 에러 핸들링 경로에서
- **Yocto 레시피 오류** — LIC_FILES_CHKSUM 누락, SRC_URI 형식 오류, inherit 빠뜨림
- **Linux 드라이버 보안** — copy_to_user 대신 raw pointer 사용, module_exit에서 자원 해제 누락

**각 케이스의 checks는 이러한 "실제 AI 실패 패턴"을 검출하도록 설계해야 한다.** 단순히 "코드가 있는지" 체크하는 것이 아니라, "올바른 순서로, 올바른 맥락에서 사용되는지"를 검증해야 한다.

### Estimated Impact
- **Complexity:** High (17 cases, diverse domains)
- **Risk Level:** Medium (domain expertise needed for each)
- **Files Created:** ~85 new files (5 per case x 17 cases)
- **Phases:** 8 phases, 2-3 cases each

---

## Case Pattern (Template)

Every case follows this structure:
```
cases/<category>-001/
  metadata.yaml        # id, category, difficulty, title, tags, platform, estimated_tokens, sdk_version
  prompt.md            # Clear, specific LLM prompt (no answers)
  reference/main.c     # Verified solution that passes all checks
  checks/static.py     # 3-8 static checks (format, forbidden patterns, required elements)
  checks/behavior.py   # 2+ behavioral checks (metamorphic properties, domain invariants)
  context/.gitkeep     # Optional context files
```

**Check rules:**
- `static.py`: Structural validation (pattern matching, forbidden constructs, format)
- `behavior.py`: Semantic validation (dependency chains, invariants, correctness)
- Both return `list[CheckDetail]` from `run_checks(generated_code: str)`

---

## Phase Plan

### Phase 1: Basic Peripherals (3 cases) — Easy

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `gpio-basic-001` | `gpio-basic` | easy | GPIO interrupt callback with debounce |
| `timer-001` | `timer` | easy | Periodic kernel timer with callback |
| `watchdog-001` | `watchdog` | easy | Watchdog timer configuration and feeding |

**Reference Materials:**

**gpio-basic-001:**
- Zephyr GPIO API: https://docs.zephyrproject.org/latest/hardware/peripherals/gpio.html
- Zephyr GPIO sample (button): https://docs.zephyrproject.org/latest/samples/basic/button/README.html
- Key APIs: `gpio_pin_configure()`, `gpio_pin_interrupt_configure()`, `gpio_init_callback()`, `gpio_add_callback()`
- Static checks: includes `zephyr/drivers/gpio.h`, uses `GPIO_INT_*` flags, has callback function signature
- Behavior checks: callback registered before interrupt enabled, pin configured as input

**timer-001:**
- Zephyr Timer API: https://docs.zephyrproject.org/latest/kernel/services/timing/timers.html
- Key APIs: `k_timer_init()`, `k_timer_start()`, `k_timer_stop()`, expiry function signature
- Static checks: includes `zephyr/kernel.h`, uses `K_MSEC()` or `K_SECONDS()`, defines expiry function
- Behavior checks: timer period > 0, stop called or duration set, no blocking in expiry

**watchdog-001:**
- Zephyr Watchdog API: https://docs.zephyrproject.org/latest/hardware/peripherals/watchdog.html
- Key APIs: `wdt_install_timeout()`, `wdt_setup()`, `wdt_feed()`
- Static checks: includes `zephyr/drivers/watchdog.h`, uses `WDT_FLAG_*`, calls `wdt_setup()`
- Behavior checks: timeout installed before setup, feed called in main loop

**Commit after Phase 1.**

---

### Phase 2: Bus Protocols (2 cases) — Medium

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `spi-i2c-001` | `spi-i2c` | medium | I2C sensor read with bus configuration |
| `dma-001` | `dma` | medium | Memory-to-memory DMA transfer |

**Reference Materials:**

**spi-i2c-001:**
- Zephyr I2C API: https://docs.zephyrproject.org/latest/hardware/peripherals/i2c.html
- I2C shell sample: https://docs.zephyrproject.org/latest/samples/drivers/i2c/target/README.html
- Key APIs: `i2c_write_read()`, `i2c_reg_read_byte()`, `DEVICE_DT_GET()`
- Static checks: includes `zephyr/drivers/i2c.h`, uses device binding macro, has target address
- Behavior checks: device ready check before read, address in valid 7-bit range (0x00-0x7F)

**dma-001:**
- Zephyr DMA API: https://docs.zephyrproject.org/latest/hardware/peripherals/dma.html
- Key APIs: `dma_config()`, `dma_start()`, `dma_stop()`, `struct dma_config`, `struct dma_block_config`
- Static checks: includes `zephyr/drivers/dma.h`, defines block config, sets source/dest addresses
- Behavior checks: source != dest address, block size > 0, channel configured before start

**Commit after Phase 2.**

---

### Phase 3: RTOS Core (2 cases) — Medium/Hard

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `threading-001` | `threading` | medium | Producer-consumer with message queue |
| `power-mgmt-001` | `power-mgmt` | medium | PM device callback implementation |

**Reference Materials:**

**threading-001:**
- Zephyr Threads: https://docs.zephyrproject.org/latest/kernel/services/threads/index.html
- Zephyr Message Queues: https://docs.zephyrproject.org/latest/kernel/services/data_passing/message_queues.html
- Key APIs: `K_THREAD_DEFINE()`, `k_msgq_init()`, `k_msgq_put()`, `k_msgq_get()`
- Static checks: includes `zephyr/kernel.h`, defines at least 2 threads, uses message queue
- Behavior checks: producer puts data, consumer gets data, queue size > 0, thread priorities differ

**power-mgmt-001:**
- Zephyr PM Guide: https://docs.zephyrproject.org/latest/services/pm/index.html
- Zephyr Device PM: https://docs.zephyrproject.org/latest/services/pm/device.html
- Key APIs: `PM_DEVICE_DT_DEFINE()`, `pm_device_action_run()`, `enum pm_device_action`
- Static checks: includes `zephyr/pm/device.h`, has PM action callback, handles SUSPEND/RESUME
- Behavior checks: both SUSPEND and RESUME handled, returns 0 on success, no blocking in callback

**Commit after Phase 3.**

---

### Phase 4: Data & Memory (2 cases) — Medium

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `storage-001` | `storage` | medium | NVS key-value store read/write |
| `memory-opt-001` | `memory-opt` | medium | Static memory pool allocation (no heap) |

**Reference Materials:**

**storage-001:**
- Zephyr NVS: https://docs.zephyrproject.org/latest/services/storage/nvs/nvs.html
- NVS sample: https://docs.zephyrproject.org/latest/samples/subsys/nvs/README.html
- Key APIs: `nvs_mount()`, `nvs_write()`, `nvs_read()`, `struct nvs_fs`
- Static checks: includes `zephyr/fs/nvs.h`, defines flash partition, mounts NVS
- Behavior checks: mount before read/write, NVS ID > 0, write data matches expected size

**memory-opt-001:**
- Zephyr Memory Pools: https://docs.zephyrproject.org/latest/kernel/services/data_passing/index.html
- Zephyr heap alternatives: `K_MEM_SLAB_DEFINE`, `K_HEAP_DEFINE`
- Key APIs: `K_MEM_SLAB_DEFINE()`, `k_mem_slab_alloc()`, `k_mem_slab_free()`
- Static checks: no `malloc`/`calloc`/`k_malloc`, uses `K_MEM_SLAB_DEFINE`, includes kernel.h
- Behavior checks: slab block size aligns to 4 bytes, free called for every alloc, no heap usage

**Commit after Phase 4.**

---

### Phase 5: Networking (2 cases) — Medium/Hard

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `networking-001` | `networking` | medium | MQTT client publish with connection handling |
| `ble-001` | `ble` | hard | BLE GATT custom service with read/write characteristics |

**Reference Materials:**

**networking-001:**
- Zephyr MQTT: https://docs.zephyrproject.org/latest/connectivity/networking/api/mqtt.html
- MQTT publisher sample: https://docs.zephyrproject.org/latest/samples/net/mqtt_publisher/README.html
- Key APIs: `mqtt_client_init()`, `mqtt_connect()`, `mqtt_publish()`, `mqtt_input()`, `mqtt_live()`
- Static checks: includes `zephyr/net/mqtt.h`, defines broker address, has event handler
- Behavior checks: connect before publish, topic not empty, QoS 0/1/2, event handler covers CONNACK/PUBACK

**ble-001:**
- Zephyr BLE GATT: https://docs.zephyrproject.org/latest/connectivity/bluetooth/api/gatt.html
- BLE peripheral sample: https://docs.zephyrproject.org/latest/samples/bluetooth/peripheral/README.html
- Key APIs: `BT_GATT_SERVICE_DEFINE()`, `BT_GATT_CHARACTERISTIC()`, `bt_enable()`, `bt_le_adv_start()`
- Static checks: includes `zephyr/bluetooth/gatt.h`, defines UUID, has read/write callbacks
- Behavior checks: bt_enable before adv_start, UUID is 128-bit custom, GATT has both read+write chars

**Commit after Phase 5.**

---

### Phase 6: Security & Boot (3 cases) — Medium/Hard

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `security-001` | `security` | hard | PSA Crypto API: AES-256 encrypt/decrypt |
| `boot-001` | `boot` | medium | MCUboot image header validation check |
| `ota-001` | `ota` | hard | DFU over UART with image confirmation |

**Reference Materials:**

**security-001:**
- PSA Crypto API: https://arm-software.github.io/psa-api/crypto/1.1/api/ops/ciphers.html
- Zephyr TF-M crypto sample: https://docs.zephyrproject.org/latest/samples/tfm_integration/tfm_psa_crypto/README.html
- Key APIs: `psa_crypto_init()`, `psa_import_key()`, `psa_cipher_encrypt()`, `psa_cipher_decrypt()`
- Static checks: includes `psa/crypto.h`, calls `psa_crypto_init()`, uses AES-256 algo constant
- Behavior checks: init before key import, key attributes set (PSA_KEY_TYPE_AES, 256 bits), encrypt/decrypt pair present

**boot-001:**
- MCUboot docs: https://docs.mcuboot.com/
- Zephyr MCUboot: https://docs.zephyrproject.org/latest/services/device_mgmt/dfu.html
- Kconfig: `CONFIG_BOOTLOADER_MCUBOOT=y`, `CONFIG_MCUBOOT_IMG_MANAGER=y`
- Static checks: CONFIG_BOOTLOADER_MCUBOOT=y present, uses image manager or boot util headers
- Behavior checks: image validation API called, slot 0/1 awareness, no conflicting boot options

**ota-001:**
- Zephyr DFU: https://docs.zephyrproject.org/latest/services/device_mgmt/dfu.html
- MCUboot image management: https://docs.zephyrproject.org/latest/services/device_mgmt/dfu.html#image-management
- Key APIs: `boot_write_img_confirmed()`, `mcuboot_swap_type()`, flash write APIs
- Static checks: includes MCUboot headers, calls image confirm, has flash partition references
- Behavior checks: swap type checked on boot, image confirmed after validation, rollback path exists

**Commit after Phase 6.**

---

### Phase 7: Drivers (2 cases) — Medium/Hard

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `sensor-driver-001` | `sensor-driver` | medium | Zephyr sensor API: temperature sensor read |
| `linux-driver-001` | `linux-driver` | hard | Linux character device driver (read/write) |

**Reference Materials:**

**sensor-driver-001:**
- Zephyr Sensor API: https://docs.zephyrproject.org/latest/hardware/peripherals/sensor.html
- Sensor sample: https://docs.zephyrproject.org/latest/samples/sensor/bme280/README.html
- Key APIs: `sensor_sample_fetch()`, `sensor_channel_get()`, `SENSOR_CHAN_AMBIENT_TEMP`, `struct sensor_value`
- Static checks: includes `zephyr/drivers/sensor.h`, uses DEVICE_DT_GET or device_get_binding, fetches before get
- Behavior checks: device_is_ready() checked, fetch before channel_get, uses correct SENSOR_CHAN_*

**linux-driver-001:**
- Linux kernel char driver: https://linux-kernel-labs.github.io/refs/heads/master/labs/device_drivers.html
- LDD3 (free online): https://lwn.net/Kernel/LDD3/
- Key APIs: `module_init()`, `module_exit()`, `register_chrdev()`, `struct file_operations`, `copy_to_user()`, `copy_from_user()`
- Static checks: has `MODULE_LICENSE`, defines file_operations struct, has init/exit functions
- Behavior checks: register in init/unregister in exit, uses copy_to_user (not raw pointer), file_operations has .read and .write

**Commit after Phase 7.**

---

### Phase 8: Build System (1 case) — Medium

| Case | Category | Difficulty | Description |
|------|----------|------------|-------------|
| `yocto-001` | `yocto` | medium | BitBake recipe for a simple C application |

**Reference Materials:**

**yocto-001:**
- Yocto recipe writing: https://docs.yoctoproject.org/dev/dev-manual/new-recipe.html
- Recipe syntax: https://docs.yoctoproject.org/dev/dev-manual/new-recipe.html#recipe-syntax
- Hello world recipe template: `poky/meta-skeleton/recipes-skeleton/hello-single/hello.bb`
- Key elements: `SUMMARY`, `LICENSE`, `LIC_FILES_CHKSUM`, `SRC_URI`, `do_compile()`, `do_install()`
- Static checks: has SUMMARY, LICENSE, SRC_URI, do_install, inherits correct class
- Behavior checks: LIC_FILES_CHKSUM matches LICENSE, install path uses ${D}${bindir}, SRC_URI scheme valid

**NOTE:** This case outputs a `.bb` recipe file, not C code. The reference is a `.bb` file, and checks validate BitBake recipe syntax rather than C code. `platform` should be `yocto_build`.

**Commit after Phase 8.**

---

## Execution Order & Dependencies

```
Phase 1 (Easy, 3 cases)      ──┐
Phase 2 (Bus, 2 cases)        │  Can run sequentially
Phase 3 (RTOS, 2 cases)       │  Each phase: 1 commit
Phase 4 (Data, 2 cases)       │
Phase 5 (Network, 2 cases)    │  Each phase is independent
Phase 6 (Security, 3 cases)   │  of others
Phase 7 (Drivers, 2 cases)    │
Phase 8 (Build, 1 case)      ──┘
                                   Total: 17 cases, 8 commits
```

---

## E2E Test Update (After All Phases)

After all 17 cases are created:
- Update `tests/test_e2e.py` `PILOT_CASE_IDS` to include all 20 case IDs
- Update expected case count assertions (3 → 20)
- Run full validation: `uv run embedeval validate --cases cases/`

---

## Per-Phase Checklist

For each phase:
- [ ] Create case directories with all 5 required files
- [ ] Reference solution passes `checks/static.py`
- [ ] Reference solution passes `checks/behavior.py`
- [ ] `uv run embedeval validate --cases cases/` passes
- [ ] `uv run pytest tests/` still passes
- [ ] `uv run ruff check src/ tests/ cases/` clean
- [ ] Commit and push

---

## Difficulty Distribution

| Difficulty | Count | Cases |
|------------|-------|-------|
| Easy | 5 | kconfig-001, gpio-basic-001, timer-001, watchdog-001, + existing |
| Medium | 10 | spi-i2c-001, dma-001, threading-001, power-mgmt-001, storage-001, memory-opt-001, networking-001, boot-001, sensor-driver-001, yocto-001 |
| Hard | 5 | isr-concurrency-001, ble-001, security-001, ota-001, linux-driver-001, + existing |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Domain expertise gaps | Checks may be too loose/strict | Reference material + iterative testing |
| Yocto case: non-C output | Evaluator expects C code | Use `platform: yocto_build`, adapt checks for .bb syntax |
| Linux driver case: no west build | L1/L2 layers skip | Use `platform: docker_only`, focus on L0/L3 |
| BLE case complexity | Hard to verify without hardware | Focus on API usage patterns, use `babblesim` platform |

---

## Success Criteria

- [ ] All 20 categories have at least 1 case
- [ ] `uv run embedeval list --cases cases/` shows 20 cases
- [ ] `uv run embedeval validate --cases cases/` passes for all 20
- [ ] All pytest tests pass
- [ ] Each reference solution passes its own static + behavioral checks
