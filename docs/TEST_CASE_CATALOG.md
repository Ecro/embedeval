# EmbedEval Test Case Catalog

23 categories × ~10 cases = **200+ test cases** targeting LLM failure patterns in embedded firmware development.

## Difficulty Legend

| Difficulty | LLM pass@1 | Criteria |
|-----------|-----------|----------|
| Easy | >70% | 학습 데이터에 풍부한 패턴, 단일 API, 순서 무관 |
| Medium | 30-70% | API 순서/의존성/에러핸들링 필요, 덜 흔한 API |
| Hard | <30% | 동시성, 보안, 리소스 수명, 환각 유도, 크로스플랫폼 함정 |

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Cases | 200 |
| Categories | 23 |
| Easy | 28 |
| Medium | 88 |
| Hard | 84 |
| Total Checks | 2247 |

---

## ble

**10 cases** (Easy: 1, Medium: 4, Hard: 5)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `ble-001` | 🔴 hard | BLE GATT Custom Service with Read/Write | Define a custom BLE GATT service with read and write charact... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 2 | `ble-002` | 🟢 easy | BLE Observer (Scan) | Start BLE scanning and print discovered devices using a scan... | Baseline — LLM should pass this reliably | S:6 B:6 |
| 3 | `ble-003` | 🟡 medium | BLE Peripheral with Notifications | GATT service with a notifiable characteristic that sends val... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 4 | `ble-004` | 🟡 medium | BLE Connection Callbacks | Register connection and disconnection callbacks, track state... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 5 | `ble-005` | 🔴 hard | BLE Pairing with Security | Configure BLE pairing with MITM protection, register auth ca... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 6 | `ble-006` | 🔴 hard | BLE Secure OTA (DFU over BLE) | Implement a BLE GATT service for firmware update with authen... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 7 | `ble-007` | 🟡 medium | BLE Advertising with Manufacturer Data | Include manufacturer-specific data in BLE advertising packet... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 8 | `ble-008` | 🔴 hard | BLE Central (Scanner + Connect) | Scan for a specific BLE device, connect to it, and discover ... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:5 |
| 9 | `ble-009` | 🟡 medium | BLE Bond Management | Manage BLE bonded devices — list bonds, remove specific bond... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 10 | `ble-010` | 🔴 hard | BLE L2CAP Connection-Oriented Channel (CoC) | Register an L2CAP CoC server, accept connections, and send/r... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:5 |

## boot

**10 cases** (Easy: 2, Medium: 5, Hard: 3)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `boot-001` | 🟡 medium | MCUboot Image Confirmation Kconfig | Kconfig fragment enabling MCUboot with image confirmation an... | API ordering/dependencies needed — common LLM blind spot | S:4 B:4 |
| 2 | `boot-002` | 🟢 easy | U-Boot Environment Kconfig | Kconfig fragment configuring U-Boot with boot delay and envi... | Baseline — LLM should pass this reliably | S:4 B:4 |
| 3 | `boot-003` | 🟡 medium | Secure Boot with Signing Kconfig | Kconfig fragment enabling MCUboot with RSA signing and slot0... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 4 | `boot-004` | 🟡 medium | MCUboot Swap with Revert Kconfig | Kconfig fragment enabling MCUboot swap-move mode with automa... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 5 | `boot-005` | 🔴 hard | Multi-image Boot Configuration Kconfig | Kconfig fragment for MCUboot dual-core setup: main app and n... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 6 | `boot-006` | 🔴 hard | Encrypted MCUboot Image Kconfig | Kconfig fragment enabling MCUboot with RSA image encryption ... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 7 | `boot-007` | 🟡 medium | MCUboot Serial Recovery Mode Kconfig | Kconfig fragment enabling MCUboot serial recovery over USB C... | API ordering/dependencies needed — common LLM blind spot | S:5 B:4 |
| 8 | `boot-008` | 🟡 medium | MCUboot Downgrade Protection Kconfig | Kconfig fragment enabling MCUboot downgrade protection with ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:4 |
| 9 | `boot-009` | 🔴 hard | Dual-bank Boot with External Flash Kconfig | Kconfig fragment enabling MCUboot dual-bank updates using SP... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 10 | `boot-010` | 🟢 easy | Basic MCUboot Logging Kconfig | Kconfig fragment enabling MCUboot debug logging and boot ban... | Baseline — LLM should pass this reliably | S:6 B:3 |

## device-tree

**10 cases** (Easy: 2, Medium: 4, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `device-tree-001` | 🟡 medium | I2C Sensor Node with Interrupt GPIO Overlay | Write a Device Tree overlay adding an I2C sensor node with i... | API ordering/dependencies needed — common LLM blind spot | S:4 B:6 |
| 2 | `device-tree-002` | 🟢 easy | SPI NOR Flash Node Overlay | Write a Device Tree overlay adding a SPI NOR flash node on t... | Baseline — LLM should pass this reliably | S:6 B:6 |
| 3 | `device-tree-003` | 🟢 easy | PWM LED Node Overlay | Write a Device Tree overlay adding a PWM LED node referencin... | Baseline — LLM should pass this reliably | S:5 B:6 |
| 4 | `device-tree-004` | 🟡 medium | CAN Bus Controller Overlay | Write a Device Tree overlay enabling the CAN controller with... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 5 | `device-tree-005` | 🔴 hard | Multi-Peripheral Board Overlay | Write a Device Tree overlay enabling I2C with BME680 sensor,... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:10 |
| 6 | `device-tree-006` | 🔴 hard | Pinctrl Configuration for UART Pins | Write a Device Tree overlay configuring pin control for UART... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 7 | `device-tree-007` | 🟡 medium | Clock Source Configuration | Write a Device Tree overlay configuring a peripheral clock s... | API ordering/dependencies needed — common LLM blind spot | S:4 B:5 |
| 8 | `device-tree-008` | 🔴 hard | DMA Channel Assignment in Device Tree | Write a Device Tree overlay assigning DMA channels to UART v... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 9 | `device-tree-009` | 🟡 medium | Voltage Regulator Node Definition | Write a Device Tree overlay defining a fixed voltage regulat... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 10 | `device-tree-010` | 🔴 hard | Chosen Node and Aliases | Write a Device Tree overlay setting /chosen console/shell-ua... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |

## dma

**10 cases** (Easy: 1, Medium: 5, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `dma-001` | 🟡 medium | Memory-to-Memory DMA Transfer | Configure and execute a memory-to-memory DMA transfer with c... | API ordering/dependencies needed — common LLM blind spot | S:5 B:7 |
| 2 | `dma-002` | 🟢 easy | DMA Peripheral-to-Memory Transfer | Configure DMA for peripheral-to-memory direction with fixed ... | Baseline — LLM should pass this reliably | S:5 B:6 |
| 3 | `dma-003` | 🟡 medium | DMA Circular Buffer | Configure DMA in circular mode for continuous data collectio... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 4 | `dma-004` | 🟡 medium | DMA Scatter-Gather Multi-block Transfer | Chain multiple DMA blocks for scatter-gather transfer using ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:6 |
| 5 | `dma-005` | 🔴 hard | DMA with Cache Coherency | Flush cache before DMA start and invalidate after completion... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 6 | `dma-006` | 🔴 hard | DMA with Buffer Alignment Requirements | Allocate cache-line aligned DMA buffers using __aligned(32) ... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 7 | `dma-007` | 🟡 medium | DMA Channel Priority Configuration | Configure two DMA channels with different priorities so the ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 8 | `dma-008` | 🔴 hard | DMA Error Handling with Callback Status Check | Implement DMA callback that checks status parameter and stop... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 9 | `dma-009` | 🟡 medium | DMA Linked List Multi-Block with Stop Condition | Chain three DMA blocks where the last block has next_block N... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 10 | `dma-010` | 🔴 hard | Zero-Copy DMA Double Buffer Swap | Implement ping-pong DMA with two buffers: while DMA fills on... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |

## gpio-basic

**4 cases** (Easy: 1, Medium: 1, Hard: 2)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `gpio-basic-001` | 🟢 easy | GPIO Button Interrupt with LED Toggle | Configure a GPIO button interrupt callback that toggles an L... | Baseline — LLM should pass this reliably | S:6 B:6 |
| 2 | `gpio-basic-005` | 🟡 medium | Multi-LED Sequential Blink | Toggle 4 LEDs in sequence using GPIO pin configuration and i... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 3 | `gpio-basic-006` | 🔴 hard | GPIO Interrupt Debounce with Timer | Button interrupt triggers a k_timer for 50ms debounce; timer... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 4 | `gpio-basic-010` | 🔴 hard | GPIO Wakeup from Deep Sleep | Configure a GPIO as wakeup source, force deep sleep power st... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |

## isr-concurrency

**10 cases** (Easy: 0, Medium: 3, Hard: 7)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `isr-concurrency-001` | 🔴 hard | ISR-safe Ring Buffer Implementation | Implement a lock-free ring buffer for ISR-to-thread data tra... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:8 |
| 2 | `isr-concurrency-002` | 🟡 medium | ISR-to-Thread Communication with k_msgq | ISR puts sensor data into a Zephyr message queue; a thread c... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 3 | `isr-concurrency-003` | 🟡 medium | Spinlock-Protected Shared State | Use k_spinlock to protect shared data accessed from both ISR... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 4 | `isr-concurrency-004` | 🔴 hard | Double-Buffer (Ping-Pong) Pattern | Two buffers alternate: ISR fills one while the thread proces... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 5 | `isr-concurrency-005` | 🔴 hard | ISR-Deferred Processing with k_work | ISR triggers k_work_submit for deferred heavy processing; IS... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 6 | `isr-concurrency-006` | 🔴 hard | ISR-Safe FIFO with k_fifo | ISR puts items into k_fifo, thread gets them; items must be ... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:5 |
| 7 | `isr-concurrency-007` | 🔴 hard | Nested Interrupt Priority Management | Configure two interrupt sources with different priorities so... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 8 | `isr-concurrency-008` | 🔴 hard | Lock-Free Single-Producer Single-Consumer Queue | Wait-free ring buffer using atomic indices; no locks, no sem... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 9 | `isr-concurrency-009` | 🟡 medium | ISR to Thread via k_poll | ISR signals k_poll_signal; thread uses k_poll to wait on mul... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 10 | `isr-concurrency-010` | 🔴 hard | Interrupt-Safe Deferred Logging | ISR writes log data to volatile buffer; thread drains buffer... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |

## kconfig

**10 cases** (Easy: 2, Medium: 4, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `kconfig-001` | 🟢 easy | SPI with DMA Mode Kconfig Fragment | Write a Kconfig fragment to enable SPI with DMA mode in Zeph... | Baseline — LLM should pass this reliably | S:5 B:3 |
| 2 | `kconfig-002` | 🟡 medium | BLE Mesh Kconfig Fragment | Write a Kconfig fragment to enable BLE Mesh with relay suppo... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 3 | `kconfig-003` | 🟢 easy | USB CDC ACM Kconfig Fragment | Write a Kconfig fragment to enable USB CDC ACM serial in Zep... | Baseline — LLM should pass this reliably | S:4 B:3 |
| 4 | `kconfig-004` | 🟡 medium | Logging with Multiple Backends Kconfig Fragment | Write a Kconfig fragment to enable deferred logging with UAR... | API ordering/dependencies needed — common LLM blind spot | S:6 B:4 |
| 5 | `kconfig-005` | 🔴 hard | TLS Networking Kconfig Fragment | Write a Kconfig fragment to enable TLS networking with MbedT... | Concurrency/security/hallucination trap — LLM frontier | S:8 B:6 |
| 6 | `kconfig-006` | 🔴 hard | Secure Boot Hardening Kconfig Fragment | Write a Kconfig fragment to enable secure boot hardening wit... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:7 |
| 7 | `kconfig-007` | 🟡 medium | WiFi and BLE Coexistence Kconfig Fragment | Write a Kconfig fragment to enable WiFi and BLE with coexist... | API ordering/dependencies needed — common LLM blind spot | S:7 B:5 |
| 8 | `kconfig-008` | 🔴 hard | Memory Protection Unit Kconfig Fragment | Write a Kconfig fragment to enable USERSPACE with MPU and co... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 9 | `kconfig-009` | 🟡 medium | Shell with Logging Backend Kconfig Fragment | Write a Kconfig fragment to enable Zephyr shell with logging... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 10 | `kconfig-010` | 🔴 hard | Hardware Crypto Acceleration Kconfig Fragment | Write a Kconfig fragment to enable PSA hardware crypto with ... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |

## linux-driver

**10 cases** (Easy: 0, Medium: 4, Hard: 6)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `linux-driver-001` | 🔴 hard | Linux Character Device Driver with Read/Write | Implement a minimal Linux kernel char device driver with fil... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 2 | `linux-driver-002` | 🟡 medium | Platform Driver with Device Tree Binding | Implement a Linux platform driver that matches a Device Tree... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 3 | `linux-driver-003` | 🟡 medium | IIO ADC Driver Skeleton | Minimal Industrial I/O driver exposing an ADC channel via sy... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 4 | `linux-driver-004` | 🔴 hard | Interrupt-Driven Character Device | Char device with IRQ handler that wakes up blocked read() on... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 5 | `linux-driver-005` | 🔴 hard | Sysfs Attribute Interface | Create a device with custom sysfs show/store attributes usin... | Concurrency/security/hallucination trap — LLM frontier | S:8 B:6 |
| 6 | `linux-driver-006` | 🔴 hard | Input Validation in ioctl Handler | Implement a Linux driver ioctl handler with _IOC_TYPE valida... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 7 | `linux-driver-007` | 🔴 hard | DMA-Coherent Buffer Allocation | Allocate and manage a DMA-coherent buffer using dma_alloc_co... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 8 | `linux-driver-008` | 🟡 medium | Proc/Sysfs File for Driver Debug Info | Create a /proc entry using proc_ops to expose driver status ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:6 |
| 9 | `linux-driver-009` | 🔴 hard | GPIO Consumer Driver with gpiolib | Request and control GPIO using the modern gpiod API with dev... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 10 | `linux-driver-010` | 🟡 medium | Workqueue-Based Deferred Processing | Schedule deferred work from interrupt context using Linux wo... | API ordering/dependencies needed — common LLM blind spot | S:5 B:6 |

## memory-opt

**10 cases** (Easy: 1, Medium: 5, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `memory-opt-001` | 🟡 medium | Static Memory Slab Allocation (No Heap) | Use K_MEM_SLAB_DEFINE for fixed-size block allocation withou... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 2 | `memory-opt-002` | 🟢 easy | Stack Size Optimization Kconfig | Kconfig fragment with minimal stack sizes and MINIMAL_LIBC t... | Baseline — LLM should pass this reliably | S:5 B:5 |
| 3 | `memory-opt-003` | 🟡 medium | K_HEAP vs K_MEM_SLAB Selection | Demonstrate correct use of K_HEAP_DEFINE for variable-size a... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 4 | `memory-opt-004` | 🟡 medium | Thread Stack Analyzer | Enable CONFIG_THREAD_ANALYZER and call thread_analyzer_print... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 5 | `memory-opt-005` | 🔴 hard | Memory Domain with Partitions | Create a memory domain with k_mem_domain_init, add partition... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 6 | `memory-opt-006` | 🔴 hard | Stack Overflow Detection via Kconfig and Runtime Check | Enable Zephyr stack analysis Kconfig options and use k_threa... | Concurrency/security/hallucination trap — LLM frontier | S:4 B:5 |
| 7 | `memory-opt-007` | 🟡 medium | Fixed-Size Object Pool (No Heap) | Implement a static object pool using a free list to avoid dy... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 8 | `memory-opt-008` | 🔴 hard | Memory Footprint Minimization via Kconfig | Disable unused subsystems via Kconfig to minimize RAM and fl... | Concurrency/security/hallucination trap — LLM frontier | S:4 B:5 |
| 9 | `memory-opt-009` | 🟡 medium | Compile-Time Buffer Size Validation with BUILD_ASSERT | Use BUILD_ASSERT to validate buffer sizes and struct layouts... | API ordering/dependencies needed — common LLM blind spot | S:4 B:5 |
| 10 | `memory-opt-010` | 🔴 hard | Linker Section Placement for DMA Buffers | Place DMA buffers in a named linker section using GCC sectio... | Concurrency/security/hallucination trap — LLM frontier | S:4 B:5 |

## networking

**10 cases** (Easy: 1, Medium: 5, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `networking-001` | 🟡 medium | MQTT Client Publish with Connection Handling | Connect to MQTT broker and publish a message with proper eve... | API ordering/dependencies needed — common LLM blind spot | S:5 B:6 |
| 2 | `networking-002` | 🟢 easy | UDP Socket Send/Receive | Create a UDP socket, send data to a server, and receive a re... | Baseline — LLM should pass this reliably | S:8 B:6 |
| 3 | `networking-003` | 🟡 medium | TCP Client with Connection Retry | Connect to a TCP server with retry logic using exponential b... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 4 | `networking-004` | 🟡 medium | CoAP Client GET Request | Send a CoAP GET request to a resource and parse the response | API ordering/dependencies needed — common LLM blind spot | S:8 B:6 |
| 5 | `networking-005` | 🔴 hard | HTTP Client with TLS | Perform an HTTPS GET request using the Zephyr HTTP client AP... | Concurrency/security/hallucination trap — LLM frontier | S:8 B:6 |
| 6 | `networking-006` | 🔴 hard | TCP Server with Buffer Overflow Protection | Accept TCP connections and receive data into a bounded buffe... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 7 | `networking-007` | 🔴 hard | DNS Resolution with Timeout | Resolve a hostname using Zephyr dns_resolve_name with timeou... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 8 | `networking-008` | 🟡 medium | MQTT with Last Will and Testament | Configure an MQTT client with a Last Will and Testament mess... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 9 | `networking-009` | 🔴 hard | WebSocket Client over TLS | Establish a WebSocket connection over TLS with credentials a... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 10 | `networking-010` | 🟡 medium | Network Interface Status Monitoring | Monitor network interface up/down events using net_mgmt even... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |

## ota

**10 cases** (Easy: 1, Medium: 4, Hard: 5)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `ota-001` | 🔴 hard | MCUboot Image Swap Confirmation After OTA | Check MCUboot swap type on boot and confirm image if test pa... | Concurrency/security/hallucination trap — LLM frontier | S:4 B:4 |
| 2 | `ota-002` | 🟢 easy | MCUboot Swap Type Check | Query the current MCUboot swap type and print a human-readab... | Baseline — LLM should pass this reliably | S:7 B:5 |
| 3 | `ota-003` | 🟡 medium | DFU Target Flash Write | Receive firmware chunks and write to flash using the dfu_tar... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 4 | `ota-004` | 🟡 medium | Image Version Check Before Update | Read current image version from bank header and only proceed... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 5 | `ota-005` | 🔴 hard | Full OTA Flow with Rollback Safety | State-machine OTA: IDLE→DOWNLOADING→VERIFYING→REBOOTING→CONF... | Concurrency/security/hallucination trap — LLM frontier | S:8 B:6 |
| 6 | `ota-006` | 🔴 hard | OTA with Image Hash Verification | Download OTA image, compute SHA-256 hash, compare with expec... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:5 |
| 7 | `ota-007` | 🟡 medium | OTA Progress Reporting | Track download progress with bytes received / total, report ... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 8 | `ota-008` | 🔴 hard | OTA Rollback with Timeout | Start a 60-second timer after boot into new image; if not co... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:5 |
| 9 | `ota-009` | 🟡 medium | OTA Image Slot Status Query | Query primary and secondary MCUboot slot status using mcuboo... | API ordering/dependencies needed — common LLM blind spot | S:7 B:5 |
| 10 | `ota-010` | 🔴 hard | Differential (Delta) OTA Patch Application | Apply a binary delta patch to the current image, verify patc... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:5 |

## power-mgmt

**10 cases** (Easy: 2, Medium: 5, Hard: 3)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `power-mgmt-001` | 🟡 medium | Device Power Management Action Handler | Implement a PM device action callback handling suspend and r... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 2 | `power-mgmt-002` | 🟢 easy | Simple System Sleep | Demonstrate CPU yielding with k_sleep, printing timestamps b... | Baseline — LLM should pass this reliably | S:5 B:5 |
| 3 | `power-mgmt-003` | 🟡 medium | Device PM with State Tracking | PM callback tracks device state in a variable and rejects du... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 4 | `power-mgmt-004` | 🟡 medium | PM Device Runtime Enable/Disable | Use pm_device_runtime_enable and pm_device_runtime_get/put f... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 5 | `power-mgmt-005` | 🔴 hard | Multi-device PM Ordering with Rollback | Suspend 3 devices in dependency order, resume in reverse; ha... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 6 | `power-mgmt-006` | 🔴 hard | Peripheral Power Gating via Clock Control | Disable peripheral clock when idle, re-enable before next ac... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 7 | `power-mgmt-007` | 🟡 medium | System PM Policy Override | Acquire and release pm_policy_state_lock to prevent deep sle... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 8 | `power-mgmt-008` | 🔴 hard | Wake Timer from Deep Sleep | Set a k_timer wakeup alarm before entering PM suspend; timer... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 9 | `power-mgmt-009` | 🟡 medium | Battery-Aware PM Transitions | Read battery ADC level and select PM policy based on charge ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 10 | `power-mgmt-010` | 🟢 easy | PM Device State Query Before Use | Query device power state with pm_device_state_get before API... | Baseline — LLM should pass this reliably | S:6 B:5 |

## security

**10 cases** (Easy: 0, Medium: 4, Hard: 6)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `security-001` | 🔴 hard | PSA Crypto AES-256-CBC Encrypt/Decrypt | Use PSA Crypto API to perform AES-256-CBC encryption and dec... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 2 | `security-002` | 🟡 medium | PSA Crypto SHA-256 Hash | Hash a message using PSA Crypto API and verify the result ma... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 3 | `security-003` | 🟡 medium | PSA Crypto Random Number Generation | Generate cryptographically secure random bytes using PSA Cry... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 4 | `security-004` | 🔴 hard | PSA Key Derivation with HKDF | Derive a key from a password using HKDF-SHA-256 with salt vi... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 5 | `security-005` | 🔴 hard | TF-M PSA Protected Storage | Store and retrieve a secret using PSA Protected Storage (psa... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 6 | `security-006` | 🔴 hard | Secure Key Storage with Anti-Tamper (Non-Extractable) | Import a key into PSA Crypto with non-extractable attributes... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 7 | `security-007` | 🔴 hard | TLS Mutual Authentication (Client Certificate) | Load CA cert, client cert, and client key via tls_credential... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 8 | `security-008` | 🟡 medium | HMAC-SHA256 Message Authentication (PSA MAC API) | Compute HMAC-SHA256 using PSA MAC API: psa_mac_sign_setup, p... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 9 | `security-009` | 🔴 hard | Cryptographically Secure Random Number Generation | Use sys_csrand_get (or psa_generate_random) for CSPRNG, neve... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:4 |
| 10 | `security-010` | 🟡 medium | PSA ECDSA P-256 Key Pair Generation | Generate ECDSA P-256 key pair using PSA; export public key o... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |

## sensor-driver

**10 cases** (Easy: 1, Medium: 5, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `sensor-driver-001` | 🟡 medium | Zephyr Sensor API Temperature Read | Read temperature from a sensor using Zephyr sensor API with ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 2 | `sensor-driver-002` | 🟢 easy | Sensor with Data-Ready Trigger Callback | Configure a sensor data-ready trigger and handle new samples... | Baseline — LLM should pass this reliably | S:6 B:5 |
| 3 | `sensor-driver-003` | 🟡 medium | Multi-Channel Accelerometer Read (XYZ) | Fetch once from an accelerometer then read all three acceler... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 4 | `sensor-driver-004` | 🟡 medium | Sensor Attribute Configuration Before Read | Set sensor sampling frequency and full-scale range via senso... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 5 | `sensor-driver-005` | 🔴 hard | Custom Sensor Driver Registration | Implement a minimal custom sensor driver with sample_fetch a... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 6 | `sensor-driver-006` | 🔴 hard | Custom Sensor Driver with I2C Backend | Implement sensor driver: init reads WHO_AM_I over I2C, sampl... | Concurrency/security/hallucination trap — LLM frontier | S:8 B:6 |
| 7 | `sensor-driver-007` | 🟡 medium | Sensor Batch Read with FIFO | Read sensor FIFO watermark, then burst-read all available sa... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 8 | `sensor-driver-008` | 🔴 hard | Sensor Fusion (Accel + Gyro to Orientation) | Fetch accelerometer and gyroscope data separately, then comp... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 9 | `sensor-driver-009` | 🟡 medium | Sensor Power Management (Low-Power Mode) | Put sensor into low-power mode between reads using sensor_at... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 10 | `sensor-driver-010` | 🔴 hard | Sensor Calibration Offset Storage in NVS | Read calibration offsets from sensor, persist in NVS, restor... | Concurrency/security/hallucination trap — LLM frontier | S:8 B:5 |

## spi-i2c

**10 cases** (Easy: 1, Medium: 5, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `spi-i2c-001` | 🟡 medium | I2C Sensor Register Read with Error Handling | Read a WHO_AM_I register from an I2C sensor with proper bus ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 2 | `spi-i2c-002` | 🟢 easy | SPI Loopback Test | Configure SPI bus, transmit and receive buffer, verify loopb... | Baseline — LLM should pass this reliably | S:5 B:5 |
| 3 | `spi-i2c-003` | 🟡 medium | I2C Multi-register Burst Read | Read 6 bytes from accelerometer registers 0x28-0x2D in a bur... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 4 | `spi-i2c-004` | 🟡 medium | SPI Flash Write and Read Verify | Write data to SPI flash with write-enable and busy-wait, rea... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 5 | `spi-i2c-005` | 🔴 hard | I2C Bus Scan | Scan all valid 7-bit I2C addresses (0x08-0x77) and report fo... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 6 | `spi-i2c-006` | 🔴 hard | I2C with Clock Stretching Timeout | Read from a slow I2C device handling clock stretching with a... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 7 | `spi-i2c-007` | 🟡 medium | SPI Full-Duplex Transfer | Perform simultaneous TX and RX using spi_transceive with sep... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 8 | `spi-i2c-008` | 🔴 hard | I2C Target (Slave) Mode Implementation | Configure device as I2C target and implement all four i2c_ta... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 9 | `spi-i2c-009` | 🟡 medium | Multi-Device SPI Bus with CS GPIO | Configure two SPI devices on a shared bus, each with its own... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 10 | `spi-i2c-010` | 🔴 hard | I2C Register Block Write with Repeated Start | Write multiple bytes to consecutive I2C registers using i2c_... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |

## storage

**10 cases** (Easy: 2, Medium: 5, Hard: 3)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `storage-001` | 🟡 medium | NVS Key-Value Store Read/Write | Mount NVS and perform key-value write then read-back verific... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 2 | `storage-002` | 🟢 easy | Settings Subsystem Load/Save | Initialize settings subsystem, save a config value, and load... | Baseline — LLM should pass this reliably | S:5 B:5 |
| 3 | `storage-003` | 🟡 medium | LittleFS File Read/Write | Mount LittleFS filesystem, write data to a file, and read it... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 4 | `storage-004` | 🟡 medium | Flash Area Erase and Write | Open flash area, erase a sector, write data, and read back t... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 5 | `storage-005` | 🔴 hard | NVS Wear-Leveling Awareness | Write multiple NVS entries, delete old ones, check remaining... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 6 | `storage-006` | 🔴 hard | Wear-Aware Flash Write with Sector Rotation | Track write count per sector and rotate to next sector when ... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 7 | `storage-007` | 🟡 medium | LittleFS Mount with Format-on-Failure Recovery | Mount LittleFS; if mount fails, format with fs_mkfs then rem... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 8 | `storage-008` | 🔴 hard | Atomic Config Update (Write-then-Commit) | Write new config to temp NVS key, verify readback, then comm... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 9 | `storage-009` | 🟡 medium | Flash Area Boundary Validation Before Write | Validate offset + size against flash area bounds using flash... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 10 | `storage-010` | 🟢 easy | Settings Key-Value Load with Default Fallback | Load a setting using the Zephyr settings subsystem; use a de... | Baseline — LLM should pass this reliably | S:6 B:5 |

## threading

**10 cases** (Easy: 1, Medium: 4, Hard: 5)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `threading-001` | 🟡 medium | Producer-Consumer with Message Queue | Two threads communicating via a Zephyr message queue in prod... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 2 | `threading-002` | 🟢 easy | Mutex-Protected Shared Counter | Two threads increment a shared counter protected by a k_mute... | Baseline — LLM should pass this reliably | S:6 B:5 |
| 3 | `threading-003` | 🟡 medium | Semaphore-Based Event Signaling | Producer thread signals an event via k_sem_give, consumer wa... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 4 | `threading-004` | 🔴 hard | Priority Inheritance Mutex | High-priority thread blocked on mutex held by low-priority t... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 5 | `threading-005` | 🔴 hard | Work Queue with Delayed Submission | Custom work queue thread with delayed work items submitted v... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 6 | `threading-006` | 🔴 hard | Deadlock-Free Multi-Mutex Acquisition | Two threads acquire two mutexes always in the same order to ... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |
| 7 | `threading-007` | 🟡 medium | Thread-Safe Singleton Initialization | Double-check locking pattern for one-time resource initializ... | API ordering/dependencies needed — common LLM blind spot | S:5 B:5 |
| 8 | `threading-008` | 🔴 hard | Real-Time Thread with Deadline Measurement | High-priority thread measures its own execution time with k_... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:5 |
| 9 | `threading-009` | 🟡 medium | Thread Pool Pattern with System Work Queue | Submit N work items to system workqueue, use counting semaph... | API ordering/dependencies needed — common LLM blind spot | S:7 B:5 |
| 10 | `threading-010` | 🔴 hard | Reader-Writer Lock Pattern | Multiple concurrent readers with exclusive writer using k_se... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:5 |

## timer

**10 cases** (Easy: 3, Medium: 4, Hard: 3)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `timer-001` | 🟢 easy | Periodic Kernel Timer with Counter | Implement a periodic kernel timer that increments a counter ... | Baseline — LLM should pass this reliably | S:5 B:5 |
| 2 | `timer-002` | 🟡 medium | One-shot Timer with Work Queue Submission | Fire a one-shot kernel timer that submits a work item to the... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 3 | `timer-003` | 🟡 medium | Hardware Counter with Alarm Callback | Use the counter driver API to set a one-shot alarm that fire... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 4 | `timer-004` | 🟢 easy | Delayed Work Item Scheduling | Schedule a delayable work item to execute after a 500ms dela... | Baseline — LLM should pass this reliably | S:5 B:5 |
| 5 | `timer-005` | 🔴 hard | Multi-timer Coordination with Atomic Shared State | Three timers at different rates (100ms, 250ms, 1000ms) updat... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 6 | `timer-006` | 🔴 hard | Precise Timing with Hardware Counter and ISR | Use the Zephyr counter API for precise microsecond timing; I... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 7 | `timer-007` | 🟡 medium | Watchdog Fed by Timer (Cascaded Safety) | A k_timer periodically feeds the watchdog; if the timer stop... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 8 | `timer-008` | 🔴 hard | High-Resolution Timestamp with k_cycle_get_32 | Use k_cycle_get_32() for sub-microsecond measurements and co... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |
| 9 | `timer-009` | 🟡 medium | Timeout Pattern with k_sem and k_timer | Wait for an event semaphore with timeout; handle both timeou... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 10 | `timer-010` | 🟢 easy | Simple Uptime Counter with k_uptime_get | Use k_uptime_get() to read and print system uptime periodica... | Baseline — LLM should pass this reliably | S:5 B:6 |

## watchdog

**10 cases** (Easy: 3, Medium: 4, Hard: 3)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `watchdog-001` | 🟢 easy | Watchdog Timer Setup and Periodic Feed | Configure a watchdog timer with timeout and feed it periodic... | Baseline — LLM should pass this reliably | S:5 B:6 |
| 2 | `watchdog-002` | 🟡 medium | Task Watchdog for Thread Health Monitoring | Use the task watchdog API to monitor a thread and trigger a ... | API ordering/dependencies needed — common LLM blind spot | S:6 B:5 |
| 3 | `watchdog-003` | 🟢 easy | Watchdog with Warning Callback Before Reset | Install a watchdog timeout with a callback that prints a war... | Baseline — LLM should pass this reliably | S:6 B:6 |
| 4 | `watchdog-004` | 🟡 medium | Dual-channel Watchdog with Different Timeouts | Configure two watchdog channels with different timeouts (1s ... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 5 | `watchdog-005` | 🔴 hard | Watchdog with Thread Health Flag Monitoring | Main thread monitors worker thread liveness via a shared fla... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 6 | `watchdog-006` | 🔴 hard | Watchdog with Pre-timeout ISR Warning Callback | Configure watchdog with a pre-timeout ISR callback that logs... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 7 | `watchdog-007` | 🟡 medium | Multi-Thread Watchdog Monitoring Pattern | Three worker threads set health flags; supervisor thread che... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 8 | `watchdog-008` | 🔴 hard | Watchdog Disable Attempt Detection | Code must NOT disable the watchdog after start; wdt_disable(... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 9 | `watchdog-009` | 🟡 medium | Window Watchdog with Min and Max Feed Constraints | Configure watchdog with both minimum (window.min > 0) and ma... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 10 | `watchdog-010` | 🟢 easy | Simple Task Watchdog for Main Thread | Use the Zephyr task watchdog (task_wdt) API to monitor the m... | Baseline — LLM should pass this reliably | S:6 B:6 |

## yocto

**10 cases** (Easy: 1, Medium: 5, Hard: 4)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `yocto-001` | 🟡 medium | BitBake Recipe for a Simple C Application | Write a Yocto BitBake recipe that builds and installs a simp... | API ordering/dependencies needed — common LLM blind spot | S:5 B:6 |
| 2 | `yocto-002` | 🟢 easy | Yocto Recipe with CMake Build System | Write a BitBake recipe that uses the cmake class to build a ... | Baseline — LLM should pass this reliably | S:7 B:6 |
| 3 | `yocto-003` | 🟡 medium | Yocto Recipe with Systemd Service | BitBake recipe that installs a systemd service unit file usi... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 4 | `yocto-004` | 🟡 medium | Yocto Recipe with Build and Runtime Dependencies | BitBake recipe with correctly specified DEPENDS (build-time)... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 5 | `yocto-005` | 🔴 hard | Yocto Out-of-Tree Kernel Module Recipe | BitBake recipe for building an out-of-tree kernel module usi... | Concurrency/security/hallucination trap — LLM frontier | S:6 B:6 |
| 6 | `yocto-006` | 🔴 hard | Yocto Recipe with Patch Application | Write a BitBake recipe that applies a patch to the source be... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 7 | `yocto-007` | 🟡 medium | Yocto Custom Image Recipe | Create a custom Yocto image recipe inheriting core-image wit... | API ordering/dependencies needed — common LLM blind spot | S:4 B:5 |
| 8 | `yocto-008` | 🔴 hard | Yocto Recipe with Multi-License Parsing | Write a BitBake recipe with multiple SPDX licenses and corre... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |
| 9 | `yocto-009` | 🟡 medium | Yocto Machine Configuration Fragment | Write a machine .conf fragment with MACHINE_FEATURES, KERNEL... | API ordering/dependencies needed — common LLM blind spot | S:4 B:5 |
| 10 | `yocto-010` | 🔴 hard | Yocto Recipe with Runtime Tests (ptest) | Write a BitBake recipe that implements Yocto ptest for runti... | Concurrency/security/hallucination trap — LLM frontier | S:5 B:6 |

## adc

**2 cases** (Easy: 0, Medium: 1, Hard: 1)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `adc-001` | 🟡 medium | ADC Single Channel Read | Read a single ADC channel and convert the raw sample to mill... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |
| 2 | `adc-002` | 🔴 hard | ADC with Hardware Averaging and Oversampling | Configure ADC oversampling before reading, validate resoluti... | Concurrency/security/hallucination trap — LLM frontier | S:7 B:6 |

## pwm

**1 case** (Easy: 1, Medium: 0, Hard: 0)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `pwm-001` | 🟢 easy | PWM LED Brightness Control | Control LED brightness by varying PWM duty cycle using the Z... | Baseline — LLM should pass this reliably | S:6 B:6 |

## uart

**3 cases** (Easy: 1, Medium: 2, Hard: 0)

| # | Case ID | Difficulty | Title | What It Tests | Why Included | Checks |
|---|---------|-----------|-------|--------------|-------------|--------|
| 1 | `uart-001` | 🟢 easy | UART Echo | Read bytes from UART and echo them back using the Zephyr UAR... | Baseline — LLM should pass this reliably | S:7 B:6 |
| 2 | `uart-002` | 🟡 medium | UART Async API with DMA | Use the Zephyr async UART API (uart_tx/uart_rx_enable) with ... | API ordering/dependencies needed — common LLM blind spot | S:7 B:6 |
| 3 | `uart-003` | 🟡 medium | Multi-UART with Runtime Baudrate Change | Configure two UARTs with different baudrates and change one ... | API ordering/dependencies needed — common LLM blind spot | S:6 B:6 |

