# PLAN: Implicit Prompts — Remove Explicit Hints

**Project:** embedeval
**Created:** 2026-03-24

---

## Executive Summary

> **TL;DR:** 프롬프트에서 안전 패턴의 exact API 이름/문법을 제거하여 LLM이 도메인
> 지식으로 스스로 도출하게 만든다. 100% 카테고리 + 핵심 힌트를 가진 ~40개 프롬프트 수정.

### Why

현재 프롬프트가 "답을 알려주는" 구조:
- "volatile int flag 선언해라" → LLM이 복사 → 통과 → 변별력 없음
- "device_is_ready() 호출해라" → 50+ 케이스에서 함수명 직접 제공

### 수정 원칙

| Before (Explicit) | After (Implicit) |
|-------------------|------------------|
| "Declare volatile int flag" | "ISR과 thread가 공유하는 flag" |
| "Call device_is_ready()" | "Verify the device is initialized before use" |
| "Use copy_to_user()" | "Safely transfer data to user space" |
| "Use __aligned(32)" | "Ensure buffers meet DMA alignment requirements" |
| "Use k_spin_lock()" | "Use ISR-safe synchronization" |
| "Use K_NO_WAIT" | "Must not block in ISR context" |
| "Call compiler_barrier()" | "Ensure memory ordering between data write and index update" |
| "Call sys_cache_data_flush_range()" | "Handle cache coherency for DMA transfers" |

### 수정하지 않는 것

| 유지하는 힌트 | 이유 |
|--------------|------|
| "Use bt_enable()" | BLE 태스크의 핵심 API — 이걸 모르면 과제 자체 불가 |
| "Include zephyr/kernel.h" | 헤더는 기능 요구사항, 안전 패턴이 아님 |
| "Call dma_config() then dma_start()" | DMA 설정의 기본 흐름 — 대부분의 튜토리얼에 있음 |
| "Error checking" 일반 언급 | "에러 체크하라"는 OK, "if (ret < 0) return ret" 까지 알려주면 과도 |

**판단 기준:** "임베디드 전문가라면 언급 없이도 알아서 하는가?" → Yes면 제거

---

## Scope: 40개 프롬프트 수정

### Priority 1: 안전 패턴 힌트 제거 (가장 큰 임팩트)

| Pattern | Cases to Fix | Action |
|---------|-------------|--------|
| `volatile` 직접 지시 | dma-008, timer-001, timer-006, timer-008, watchdog-005, isr-010, linux-driver-004 | "공유 변수" 설명으로 대체 |
| `__aligned(32)` 직접 지시 | dma-005, dma-006, memory-opt-010 | "DMA alignment 보장" 으로 대체 |
| `copy_to_user/from_user` 직접 지시 | linux-driver-001, 004, 006 | "안전한 kernel↔user 데이터 전송" 으로 대체 |
| `k_spinlock` 직접 지시 | isr-concurrency-003 | "ISR-safe 동기화" 로 대체 |
| `K_NO_WAIT` 직접 지시 | isr-concurrency-002, memory-opt-001/003 | "ISR에서 blocking 금지" 로 대체 |
| `compiler_barrier` 직접 지시 | isr-concurrency-008 | "메모리 순서 보장" 으로 대체 |
| `sys_cache_*` 직접 지시 | dma-005 | "캐시 코히어런시 보장" 으로 대체 |

### Priority 2: device_is_ready 힌트 축소

50+ 케이스에서 `device_is_ready()` 함수명을 직접 제공.
**전부 제거하면 과도** — 대신 **하위 10개 케이스**만 수정:

| Category | Cases to Fix | Strategy |
|----------|-------------|----------|
| dma | 008, 006, 005 | "Verify device readiness" (함수명 제거) |
| watchdog | 005, 007 | "Check device before use" |
| timer | 006, 007 | "Ensure device is available" |
| gpio-basic | 001 | "Check before GPIO operations" |
| sensor-driver | 003 | "Verify sensor available" |

나머지 40+ 케이스는 유지 (easy/medium 난이도에서는 힌트 OK)

### Priority 3: 에러 체크 상세 패턴 제거

현재: "Call X() and check return value (must be PSA_SUCCESS)"
변경: "Call X() and handle failures appropriately"

| Category | Cases | Action |
|----------|-------|--------|
| security | 001-003 | PSA_SUCCESS 등 구체적 에러코드 제거 |
| ota | 003, 005 | dfu_target_done(false) 롤백 패턴 직접 제시 → "handle failure" 로 |
| storage | 002 | settings_subsys_init 순서 직접 제시 → "initialize before use" 로 |

---

## Implementation Plan

### Phase 1: Priority 1 — 안전 패턴 힌트 제거 (~15 prompts)

volatile, __aligned, copy_to_user, k_spinlock, K_NO_WAIT, barrier, cache 힌트.
각 prompt.md를 읽고 exact API/syntax를 기능 설명으로 대체.

### Phase 2: Priority 2 — device_is_ready 축소 (~10 prompts)

선별된 hard 케이스에서만 함수명 제거.

### Phase 3: Priority 3 — 에러 체크 상세 제거 (~5 prompts)

구체적 에러 코드/패턴 제거, "handle failures" 로 일반화.

### Phase 4: 검증

1. `uv run pytest tests/` — 레퍼런스 솔루션 여전히 통과 확인
2. 프롬프트 변경이 TC 체크에 영향 없는지 확인 (체크는 안 바꿈)

### Phase 5: 재벤치마크

1. `uv run embedeval run --model claude-code://sonnet --cases cases/ -v`
2. 변경 전(91%) vs 변경 후 pass@1 비교
3. 카테고리별 변화 분석

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| 프롬프트가 너무 모호해져서 과제 자체가 불가능 | High | 기능 요구는 유지, 안전 패턴만 제거 |
| 레퍼런스 솔루션이 새 프롬프트와 불일치 | Medium | 레퍼런스는 수정 안 함 — 체크만 통과하면 됨 |
| easy 케이스까지 너무 어려워짐 | Medium | 001-005는 유지, 006-010 위주 수정 |

---

## Success Criteria

- [ ] ~30개 프롬프트에서 explicit safety hint 제거
- [ ] 685 pytest 전부 통과
- [ ] 재벤치마크 시 pass@1 하락 확인 (목표: 91% → 75-85%)
- [ ] INSIGHTS.md에 #6 추가 (before/after 비교)

---

## Estimated Effort

- Phase 1-3: ~2시간 (30개 프롬프트 수정)
- Phase 4: ~10분 (pytest)
- Phase 5: ~50분 (벤치마크)
- Total: ~3시간
