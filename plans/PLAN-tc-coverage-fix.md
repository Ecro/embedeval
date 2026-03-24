# PLAN: TC Coverage Fix — L1/L2 빌드 + ESP-IDF 확대 + Implicit 완료

**Project:** embedeval
**Created:** 2026-03-24

---

## Executive Summary

> **TL;DR:** L1/L2 빌드 파일 7%→73%, ESP-IDF 5→10개, implicit 잔여 5개 제거.

### 현재 vs 목표

| 항목 | 현재 | 목표 | 방법 |
|------|------|------|------|
| L1/L2 빌드 파일 | 15/205 (7%) | 155/210 (73%) | 스크립트 일괄 생성 |
| ESP-IDF cases | 5 | 10 | 5개 신규 (i2c, ble, ota, sleep, adc) |
| Implicit 잔여 | 5개 | 0개 | 5개 프롬프트 수정 |

### 핵심 설계 결정

1. **CMakeLists.txt는 모든 Zephyr 케이스에서 동일** — 템플릿 1개 복사
2. **prj.conf는 카테고리별 동일** — -001의 prj.conf를 002~010에 복사
3. **비-C 케이스 (kconfig, device-tree, boot, yocto, linux-driver)는 빌드 스킵이 정상**
4. **ESP-IDF 새 케이스도 implicit prompt 원칙 적용**

---

## Phase 1: Implicit 전환 완료 (5분)

잔여 5개 프롬프트 수정:

| File | Hint | Action |
|------|------|--------|
| dma-006/prompt.md | `device_is_ready()` | "Verify device initialized" |
| timer-006/prompt.md | `device_is_ready()` | "Verify device initialized" |
| watchdog-005/prompt.md | `device_is_ready()` | "Verify device initialized" |
| esp-nvs-001/prompt.md | `volatile` | 설명적 표현으로 대체 |
| storage-001/prompt.md | `volatile` | 설명적 표현으로 대체 |

---

## Phase 2: ESP-IDF 5개 추가 (1시간)

| Case | 내용 | 핵심 체크 |
|------|------|----------|
| esp-i2c-001 | I2C master read/write | i2c_master_bus_add_device, 에러 체크, no Zephyr |
| esp-ble-001 | BLE GATT server | Bluedroid API, 이벤트 핸들러, no NimBLE |
| esp-ota-001 | OTA via HTTPS | esp_https_ota, 롤백 경로, 에러 처리 |
| esp-sleep-001 | Deep sleep + wakeup | esp_deep_sleep_start, wakeup source, GPIO config |
| esp-adc-001 | ADC + calibration | adc_oneshot, adc_cali, raw→mV 변환 |

각 케이스 구조:
```
esp-xxx-001/
├── metadata.yaml
├── prompt.md        (implicit — API 이름 제거)
├── reference/main.c
├── checks/static.py (헤더, 엔트리포인트, cross-platform)
├── checks/behavior.py (에러 처리, 순서, 도메인 지식)
└── context/.gitkeep
```

---

## Phase 3: L1/L2 빌드 파일 일괄 생성 (30분)

### 전략

```
Step 1: 기존 -001/prj.conf를 같은 카테고리 002~010에 복사
Step 2: CMakeLists.txt도 동일하게 복사
Step 3: 새 ESP-IDF 케이스에 CMakeLists.txt + sdkconfig.defaults 추가
Step 4: 비-C 케이스 (kconfig, device-tree, boot, yocto)는 건너뜀
```

### 빌드 대상 분류

| 빌드 시스템 | 카테고리 | 케이스 수 |
|------------|---------|----------|
| west build | gpio, spi-i2c, dma, isr, threading, timer, sensor, networking, ble, security, storage, ota, power-mgmt, watchdog, memory-opt | 150 |
| idf.py build | esp-* | 10 |
| **빌드 불가** | kconfig, device-tree, boot, yocto, linux-driver | **50** |
| **합계** | | **210** |

빌드 가능 케이스 중 커버리지: 160/160 = **100%**

---

## 실행 순서

```
Phase 1 (trivial): Implicit 전환 5개 → 즉시 검증
  ↓
Phase 2 (medium): ESP-IDF 5개 추가 → pytest 검증
  ↓
Phase 3 (scripted): 빌드 파일 일괄 생성 → pytest 검증
  ↓
최종: 전체 상태 리포트
```

---

## Success Criteria

- [ ] Implicit 잔여 = 0
- [ ] ESP-IDF = 10개
- [ ] 빌드 파일 커버리지 = 빌드 가능 케이스 100%
- [ ] pytest 전부 통과
- [ ] 전체 TC = 210개
