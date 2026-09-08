# Benchmark Delta — claude-code://claude-opus-5 vs claude-code://claude-sonnet-5

**Pure model improvement is the INTERSECTION row.** The two models ran
different case sets; only the common cases isolate model capability
from case-set change. Cases unique to the newer run are reported
separately (absolute performance only — no baseline to diff against).

## Per-case verdict method

- claude-code://claude-opus-5: majority vote of 1 runs (>= 1 of 1 passing = pass)
- claude-code://claude-sonnet-5: majority vote of 3 runs (>= 2 of 3 passing = pass)

## Case-set overlap

| Set | Cases |
|-----|-------|
| Intersection (both models) | 263 |
| New-only (in claude-code://claude-opus-5) | 4 |
| Dropped (only in claude-code://claude-sonnet-5) | 0 |

## Pure model improvement (intersection only)

| Model | pass@1 (majority) | passed / total |
|-------|-------------------|----------------|
| claude-code://claude-sonnet-5 | 67.7% | 178 / 263 |
| claude-code://claude-opus-5 | 61.2% | 161 / 263 |
| **Delta** | **-6.5%p** | — |

### Per-run pass@1 (each over its own full case set, for reference)

- claude-code://claude-sonnet-5: 66.9%, 66.9%, 67.3% (mean 67.0%)
- claude-code://claude-opus-5: 61.8% (mean 61.8%)

## New-only cases (4) — claude-code://claude-opus-5 absolute performance

- pass@1 (majority): **100.0%** (4 / 4)
- No baseline: these cases did not exist in the older run.

## Improved: claude-code://claude-sonnet-5 fail -> claude-code://claude-opus-5 pass (15)

| Category | Cases |
|----------|-------|
| dma | dma-003, dma-009, dma-012 |
| kconfig | kconfig-002 |
| linux-driver | linux-driver-009, linux-driver-013 |
| linux-userspace | linux-userspace-008 |
| memory-opt | memory-opt-001 |
| networking | networking-008 |
| ota | ota-003, ota-swupdate-003 |
| power-mgmt | power-mgmt-010 |
| security | security-007 |
| sensor-driver | sensor-driver-003 |
| yocto | yocto-003 |

## Regressed: claude-code://claude-sonnet-5 pass -> claude-code://claude-opus-5 fail (32)

| Category | Cases |
|----------|-------|
| adc | adc-002 |
| ble | ble-006 |
| dma | dma-005 |
| isr-concurrency | isr-concurrency-004 |
| linux-driver | linux-driver-004, linux-driver-010, linux-driver-011 |
| linux-userspace | linux-userspace-003, linux-userspace-006, linux-userspace-007 |
| networking | networking-004, networking-005 |
| ota | ota-001, ota-004, ota-005, ota-006, ota-008, ota-swupdate-001, ota-swupdate-004 |
| power-mgmt | esp-sleep-001, power-mgmt-004, power-mgmt-005 |
| security | security-003, security-005 |
| spi-i2c | esp-i2c-001 |
| threading | threading-002, threading-006 |
| timer | stm32-timer-001, timer-008 |
| uart | uart-002 |
| watchdog | watchdog-007 |
| yocto | yocto-006 |

---

## Caveats — read before quoting the delta

1. **Asymmetric sampling.** Opus 5 is a single run (n=1); Sonnet 5 is a
   majority vote over n=3. A single Opus 5 run carries the full flakiness
   of the case set — Sonnet 5's own three runs spanned 66.9–67.3%, and
   Haiku's spanned 55.4–58.4%. The −6.5%p gap is larger than Sonnet 5's
   run-to-run spread, but it has not been shown to survive n=3 for Opus 5.

2. **A large share of the "regressions" are check artifacts, not defects.**
   Spot-checking 8 of the cases where Opus 5 fails L3 (`static_heuristic`)
   and Sonnet 5 passes found **0 real code defects** — every one was a check
   problem (see the 2026-09-08 entries in `CLAUDE.md`). Two recurring causes:
   - Ordering checks that call `generated_code.find(...)` on **raw text
     including comments** invert when the model documents the API in a
     header comment. This is exactly the `ota` cluster below
     (`ota-001`, `ota-005`, `ota-006`, `power-mgmt-004`).
   - Checks demanding a literal idiom reject valid or better variants
     (`atomic_t` + `atomic_set` instead of `volatile`; `#define` constants
     instead of literal digits; a symbolic device path instead of
     `"/dev/spidev0.0"`).

   Opus 5 comments its code more heavily than Sonnet 5, so it is
   structurally more exposed to (a). **L3 pass rates are not
   model-comparable until the failures are inspected.**

3. **Four case IDs shifted meaning between the two runs.** At the time of
   the Sonnet 5 run, `linux-driver-009/010` and `yocto-009/010` collided
   public↔private and the private case shadowed the public one. The private
   repo has since renamed those to `linux-driver-017/018` and
   `yocto-013/014`, so for those four IDs the intersection compares a
   public case (Opus 5) against a private case (Sonnet 5). They appear as
   the 4 "new-only" cases plus a handful of the improved/regressed rows.

4. **`compile_gate` failures are case-set-driven, not environment drift.**
   Opus 5 failed L1 on 11 of the 48 private cases; Sonnet 5's three runs
   failed L1 on 10, 14 and 11 of the same set. Both runs used the same
   `embedeval-zephyr:latest` image with `EMBEDEVAL_ENABLE_BUILD=docker`.
