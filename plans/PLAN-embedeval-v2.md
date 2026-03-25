# PLAN: EmbedEval v2 — Multi-Platform + Build Verification

**Project:** embedeval
**Created:** 2026-03-25

---

## Executive Summary

> **TL;DR:** "EmbedEval"이라는 이름에 걸맞게 5개 플랫폼으로 확대하고,
> 다른 SW 벤치마크(SWE-bench, EmbedAgent)처럼 실제 빌드 검증을 활성화한다.

### 현재 vs 목표

| 항목 | v1 (현재) | v2 (목표) |
|------|----------|----------|
| TC 수 | 210 | 250+ |
| 플랫폼 | 3 (Zephyr, ESP-IDF, Linux) | **5** (+STM32 HAL, bare-metal) |
| L1 빌드 검증 | 인프라만 (0% 실행) | **50%+ 실제 빌드 통과** |
| FreeRTOS 비율 | 5% (ESP-IDF만) | **25%+** (ESP-IDF + STM32) |
| Embedded Linux | 10% | **15%+** |
| pass@k | 1회 시행 | **3회 반복** |

### 왜 필요한가

1. **시장 현실**: FreeRTOS ~45%, Linux ~30%, Zephyr ~6%. 현재 Zephyr 71%는 편향.
2. **신뢰성**: 코드를 컴파일 안 하는 "코드 벤치마크"는 학술적으로 약함.
3. **변별력**: STM32 HAL은 Zephyr와 API가 완전히 달라 cross-platform 능력 테스트.

---

## 부족한 부분 전체 체크리스트

### 플랫폼 커버리지

| Platform | 시장 점유율 | 현재 TC | 목표 TC | Gap |
|----------|-----------|---------|---------|-----|
| FreeRTOS (ESP-IDF) | ~15% | 10 | 30 | +20 |
| FreeRTOS (STM32 HAL) | ~30% | **0** | **20** | **+20** |
| Zephyr | ~6% | 150 | 120 | -30 (비율 조정) |
| Embedded Linux | ~30% | 20 | 40 | +20 |
| bare-metal CMSIS | ~15% | **0** | **10** | **+10** |

### 빌드 검증 (L1/L2)

| Platform | Docker 이미지 | Build Command | 현재 | 목표 |
|----------|-------------|---------------|------|------|
| Zephyr | ghcr.io/zephyrproject-rtos/ci | `west build -b native_sim` | 준비됨 | **실행 검증** |
| ESP-IDF | espressif/idf:v5.3 | `idf.py build` | 준비됨 | **실행 검증** |
| STM32 HAL | ubuntu + arm-none-eabi-gcc | `arm-none-eabi-gcc -c` | **없음** | **신규** |
| Linux module | ubuntu + kernel headers | `make -C /lib/modules` | **없음** | **신규** |
| bare-metal | arm-none-eabi-gcc | `arm-none-eabi-gcc -nostdlib` | **없음** | **신규** |

### 통계적 검증

| 항목 | 현재 | 목표 |
|------|------|------|
| pass@k | pass@1 only (1회) | **pass@3** (3회 반복) |
| Confidence interval | 없음 | **95% CI 표시** |
| Negative tests | 0 | **30+ (10 TC × 3 오답)** |
| 모델 비교 | 2 (Sonnet, Haiku) | **4+ (+GPT-4o, Gemini)** |

---

## 4-Phase Implementation

### Phase 1: STM32 HAL + Docker 빌드 검증

**STM32 HAL TC 10개:**

| Case ID | 내용 | 핵심 체크 |
|---------|------|----------|
| stm32-gpio-001 | GPIO + EXTI 인터럽트 | HAL_GPIO_Init, 콜백 패턴 |
| stm32-uart-001 | UART 인터럽트 수신 | HAL_UART_Receive_IT, 에러 콜백 |
| stm32-spi-001 | SPI master 통신 | CS 핀 수동 제어, full-duplex |
| stm32-i2c-001 | I2C 센서 읽기 | HAL_I2C_IsDeviceReady, 에러 |
| stm32-timer-001 | 타이머 PWM | 프리스케일러/ARR 계산 |
| stm32-adc-001 | ADC DMA 연속 변환 | DMA 설정, 캘리브레이션 |
| stm32-freertos-001 | 태스크 + 큐 | xTaskCreate, xQueueSend |
| stm32-freertos-002 | 뮤텍스 + ISR | FromISR 버전, 우선순위 |
| stm32-dma-001 | DMA mem-to-mem | 정렬, 콜백, 에러 |
| stm32-lowpower-001 | Stop 모드 + RTC | SystemClock_Config 재호출 |

**Docker 빌드 인프라:**
- `Dockerfile.stm32` — arm-none-eabi-gcc + STM32F4 HAL
- evaluator.py에 STM32 빌드 dispatch 추가
- 빌드: 컴파일만 (`-c` flag), 링크/실행은 하지 않음

**Zephyr L1 실제 검증:**
- `docker-compose run embedeval` 으로 10개 TC 빌드 테스트
- 실패하면 prj.conf 수정

### Phase 2: bare-metal CMSIS + 통계 검증

**bare-metal TC 10개:**

| Case ID | 내용 | 핵심 체크 |
|---------|------|----------|
| baremetal-gpio-001 | 레지스터 직접 접근 GPIO | GPIOA->MODER, BSRR |
| baremetal-clock-001 | 클럭 트리 설정 | RCC->CFGR, PLL 설정 |
| baremetal-uart-001 | UART 레지스터 직접 | USART1->BRR 보드레이트 계산 |
| baremetal-nvic-001 | NVIC 인터럽트 설정 | NVIC_EnableIRQ, 우선순위 |
| baremetal-systick-001 | SysTick 타이머 | SysTick->LOAD, CTRL |
| baremetal-dma-001 | DMA 레지스터 직접 | DMA1_Stream0->CR |
| baremetal-flash-001 | 플래시 쓰기 | FLASH->CR unlock/lock |
| baremetal-startup-001 | 스타트업 코드 | vector table, Reset_Handler |
| baremetal-linker-001 | 링커 스크립트 | MEMORY, SECTIONS |
| baremetal-bitband-001 | 비트 밴딩 접근 | Cortex-M4 bit-band alias |

**통계 검증:**
- Sonnet pass@3 벤치마크 실행
- Haiku pass@3 벤치마크 실행
- Negative test: 10개 TC × 3가지 오답 변형

### Phase 3: ESP-IDF + Linux 확대

**ESP-IDF +10개:**
- esp-mqtt-001: MQTT client
- esp-https-001: HTTPS client
- esp-spiffs-001: 파일시스템
- esp-mesh-001: ESP-MESH 네트워킹
- esp-camera-001: 카메라 드라이버
- esp-touch-001: 터치 센서
- esp-ledc-001: LED PWM
- esp-pcnt-001: 펄스 카운터
- esp-rmt-001: IR 리모컨
- esp-sdcard-001: SD 카드 SPI

**Linux +10개:**
- linux-platform-001: platform driver
- linux-iio-001: IIO subsystem sensor
- linux-sysfs-001: sysfs 인터페이스
- linux-dt-binding-001: DT binding yaml
- linux-irq-001: threaded IRQ handler
- linux-dma-001: DMA engine client
- linux-regmap-001: regmap I2C/SPI
- linux-gpio-001: GPIO descriptor API
- linux-pwm-001: PWM subsystem
- linux-power-001: runtime PM

### Phase 4: 마무리

- 전체 L1 빌드 검증 (Docker에서 모든 빌드 가능 TC 통과)
- difficulty weighting 적용
- GPT-4o, Gemini 벤치마크 (API key 필요)
- 논문/블로그 작성
- README 최종 업데이트

---

## Success Criteria (v2 전체)

- [ ] 250+ TC
- [ ] 5개 플랫폼 (Zephyr, ESP-IDF, STM32 HAL, Linux, bare-metal)
- [ ] L1 빌드 검증 50%+ TC에서 실제 통과
- [ ] pass@3 데이터 (Sonnet + Haiku)
- [ ] Negative test 30+개 검증
- [ ] 4+ 모델 비교 데이터
- [ ] pytest 전부 통과

---

## 이번 세션 범위 (Phase 1만)

| 작업 | 예상 시간 |
|------|----------|
| STM32 HAL TC 10개 생성 | 1.5시간 |
| Dockerfile.stm32 생성 | 30분 |
| evaluator.py STM32 빌드 dispatch | 30분 |
| Zephyr Docker 빌드 실제 검증 (10개) | 30분 |
| pytest 확인 | 10분 |
| **Total** | **~3시간** |
