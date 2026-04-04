# PLAN: Fix L1/L2 Testing Methodology

**Project:** embedeval
**Created:** 2026-03-31
**Priority:** Critical
**Status:** in-progress

---

## Executive Summary

> **TL;DR:** L1/L2 (Docker build + runtime) 테스트 결과가 구조적으로 신뢰할 수 없음. Reference solution 미검증, 프롬프트에 타겟 보드 미명시, 불가능한 L2 케이스 존재 등 7개 근본 문제 수정.

### Sonnet Retest 결과 분석 (2026-03-30)

| Metric | Value |
|--------|-------|
| Retested Cases | 120/179 (changed since last run) |
| pass@1 | 22.5% (vs 이전 84.9% — L0+L3 only) |
| L1 Build Fail | 51 (55% of failures) |
| L2 Runtime Fail | 33 (35% of failures) |
| L0+L3 Fail | 9 (10% of failures) |

---

## 발견된 문제 (심각도 순)

### CRITICAL-1: Reference Solution이 L1을 통과하지 못함

**증거:**
- `sensor-driver-001/reference/main.c` → `DT_NODELABEL(temp_sensor)` 사용
- `build_board: nrf52840dk/nrf52840`이지만 nrf52840dk DTS에 `temp_sensor` 노드 없음
- **Reference 자체가 컴파일 불가능** → 이 케이스는 어떤 LLM도 통과 불가
- `adc-001` reference도 동일 패턴 (`DT_PATH(zephyr_user)`)

**영향 범위:**
- sensor-driver 8/8, adc 2/2, 일부 watchdog, spi-i2c 케이스
- L1 실패 51건 중 최소 23건이 nrf52840dk 타겟 (reference도 실패 가능성)

**원인:** DT overlay 파일이 케이스에 포함되지 않음. LLM에게 overlay 생성도 요구하지 않음.

### CRITICAL-2: verify_results.py가 L1/L2를 검증하지 않음

**증거:**
- `scripts/verify_results.py`는 Python check module (static.py, runtime.py)만 실행
- Docker 빌드(L1)나 QEMU 실행(L2)은 re-run하지 않음
- Reference solution의 compilability를 전혀 검증하지 않음
- 결과: "All 120 results verified OK" → **false confidence**

### CRITICAL-3: 케이스 셋이 다른 모델 간 비교

**증거:**
```
Sonnet: 227 cases (179 public + 48 private)
Haiku:  179 cases (public only)
```
- 48개 추가 케이스(009-010 variants, ESP, STM32)가 Sonnet에만 있음
- pass@1 비교 자체가 무의미 (55.1% vs 34.1%은 다른 시험지)

### MAJOR-4: 프롬프트에 타겟 보드 미명시

**증거:**
- 모든 `prompt.md`에 "native_sim" 또는 보드 이름 없음
- 예: adc-001 prompt = "Write a Zephyr RTOS application that reads a single ADC channel..."
- LLM은 어떤 보드용 코드를 써야 하는지 모름
- `metadata.yaml`의 `build_board`는 테스트 인프라만 사용, LLM에게 전달 안 됨

**모순:** `metadata.yaml`에 `platform: native_sim` AND `build_board: nrf52840dk/nrf52840` 동시 존재 (adc-001)

### MAJOR-5: native_sim에서 물리적으로 불가능한 L2 케이스

**증거:**
- BLE: `Bluetooth init failed (err -19)` — native_sim에 BT controller 없음
- Networking: `mqtt_connect failed: -96` — 네트워크 스택 미구성
- 이 케이스들의 `build_board`는 native_sim(기본값)
- **어떤 LLM이든 100% 실패** → 변별력 제로

**해당 케이스:** ble-001/003/004/007 (native_sim), networking-001/002/003/006

### MAJOR-6: nrf52840dk L2 auto-pass 스코어링 비대칭

**증거:**
- `evaluator.py:527-546`: nrf52840dk → L2 자동 PASS ("board requires hardware")
- native_sim → L2 실행 후 PASS/FAIL 판정
- 결과: nrf52840dk 케이스는 L1만 통과하면 L2 무조건 PASS, native_sim 케이스는 L2 추가 허들
- power-mgmt-001: L1 PASS → L2 "skipped (board requires hardware)" → 최종 PASS

### MINOR-7: Haiku 미재테스트

- Haiku는 03-29 결과 그대로, 케이스 변경 후 재테스트 안 됨
- Sonnet만 03-30에 retest → 비교 시점 불일치

---

## 실제 L1 실패 분류

```
L1 실패 51건:
├── native_sim 타겟: 28건
│   ├── 코드가 native_sim에서 지원 안 되는 HW 기능 사용
│   └── BLE, DMA, ISR, networking, security, storage, threading, timer
│
└── nrf52840dk 타겟: 23건
    ├── DT 노드/alias 미존재 (overlay 없음): ~15건
    │   └── Reference solution도 동일 문제 → 구조적 결함
    ├── LLM 코드 자체 오류: ~8건
    └── sensor-driver 8/8, adc 2/2, ota 6/8, spi-i2c 3/8, watchdog 2/8
```

---

## 수정 계획

### Phase 1: 데이터 정합성 (즉시)

#### 1.1 Reference Solution L1 검증 스크립트 추가
- `scripts/verify_references_build.py` 신규 생성
- 모든 reference solution을 해당 `build_board`로 Docker 빌드 시도
- 실패하는 reference = **케이스 버그** (L1 테스트 자격 없음)
- 예상 결과: sensor-driver 8건, adc 2건 등 다수 reference 빌드 실패 발견

#### 1.2 DT Overlay 추가 또는 L1 스킵 마킹
- Reference가 빌드 실패하는 케이스: `overlay.dts` 파일 추가
  - nrf52840dk에 `temp_sensor`, `zephyr,user` 등 필요 노드 정의
  - Docker 빌드 시 `-DDTC_OVERLAY_FILE=overlay.dts` 적용
- 또는: 해당 케이스에 `l1_skip: true` 메타데이터 추가, L0+L3만 평가

#### 1.3 verify_results.py에 L1 reference 검증 추가
- Reference solution도 Docker 빌드 가능한지 확인
- Reference L1 실패 = FALSE NEGATIVE로 보고
- 현재 "All verified OK"가 실제로는 불완전 검증임을 수정

### Phase 2: 테스트 공정성 (단기)

#### 2.1 프롬프트에 빌드 타겟 정보 추가
- `runner.py`에서 프롬프트 구성 시 `build_board` 정보 주입
- 형식: `Target board: nrf52840dk/nrf52840` 또는 `Target: native_sim`
- LLM이 타겟에 맞는 코드를 쓸 수 있게 함
- **또는**: 프롬프트에 명시하지 않되, 이를 "implicit knowledge" 테스트로 명확히 문서화

#### 2.2 L2 불가능 케이스 처리
옵션 A: BLE/networking 케이스의 `build_board`를 `nrf52840dk`로 변경 → L2 auto-skip
옵션 B: native_sim용 mock/stub 추가 (BLE controller emulation 등)
옵션 C: L2 실패가 예상되는 케이스에 `l2_expected_fail: true` 마킹

**권장: 옵션 A** — BLE/networking은 native_sim에서 실행 불가능이 자명

#### 2.3 스코어 이중 보고
```
pass@1 (full):     L0 + L1 + L2 + L3 + L4 (현재 방식)
pass@1 (quality):  L0 + L3 only (코드 품질만)
pass@1 (build):    L1 only (컴파일 가능성)
pass@1 (runtime):  L2 only (실행 가능성, native_sim만)
```

### Phase 3: 비교 공정성 (단기)

#### 3.1 동일 케이스셋 강제
- LEADERBOARD.md 비교 시 공통 케이스만으로 계산
- 또는 Haiku도 227 전체 실행
- `--retest-only` 시 모델별 독립 해시 트래킹 확인

#### 3.2 Haiku 재테스트
- 케이스 변경 후 Haiku `--retest-only` 실행
- 동일 Docker 환경, 동일 시점에서 비교

### Phase 4: 메타데이터 정리

#### 4.1 `platform` vs `build_board` 모순 해결
- `platform: native_sim` + `build_board: nrf52840dk` → 하나로 통일
- `platform`은 "어떤 OS/RTOS"를, `build_board`는 "어떤 보드 타겟"으로 의미 분리 명확화

#### 4.2 카테고리별 L1/L2 적용 가능성 문서화
```
| Category | L1 가능? | L2 가능? | 비고 |
|----------|---------|---------|------|
| adc | O (overlay 필요) | X (HW) | nrf52840dk |
| ble | O (native_sim) | X (BT 없음) | L2 구조적 불가 |
| boot | X (config) | X | L0+L3만 |
| dma | O (native_sim) | O | |
| gpio-basic | O (nrf52840dk) | X (HW) | |
| isr-concurrency | O (native_sim) | O | |
| kconfig | X (config) | X | L0+L3만 |
| sensor-driver | O (overlay 필요) | X (HW) | nrf52840dk |
| ... | | | |
```

---

## 성공 기준

- [ ] 모든 reference solution이 해당 build_board로 L1 통과
- [ ] verify_results.py가 L1 reference 검증 포함
- [ ] LEADERBOARD 비교가 동일 케이스셋 기반
- [ ] L2 구조적 불가 케이스가 명확히 처리됨
- [ ] 프롬프트에 빌드 타겟 정보 존재 (또는 미포함이 의도적임이 문서화)
- [ ] pass@1이 "full" + "quality" 이중 보고

---

## 현재 결과의 올바른 해석

현 상태에서 신뢰할 수 있는 수치:

| Metric | Value | 신뢰도 |
|--------|-------|--------|
| Sonnet L0+L3 pass@1 | ~85% (03-29) | **높음** (이전 검증됨) |
| Sonnet full pass@1 | 55.1% (227 cases) | **낮음** (reference 미검증, overlay 미제공) |
| Haiku L0+L3 pass@1 | ~34% (179 cases) | **중간** (미재테스트) |
| Sonnet-Haiku gap | +21%p | **낮음** (다른 케이스셋) |
| L1 build 실패율 | 51/227 = 22.5% | **해석 주의** — 환경 문제와 코드 문제 혼재 |

**결론: L1/L2 테스트는 유의미하지만, 현재 인프라로는 "LLM 코드 품질"과 "테스트 환경 한계"를 분리할 수 없음. Phase 1 수정 후 재측정 필요.**
