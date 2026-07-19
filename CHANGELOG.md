# Changelog

All notable changes to EmbedEval are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-07-19

### Benchmark results

- **Sonnet 5 n=3 benchmark** (263 unique cases, incl. held-out private, real
  Docker L1/L2 compile): mean pass@1 **67.0%** (95% CI [63.7%, 70.2%], stdev
  0.29%p — the most stable model measured to date).
- **Sonnet 5 vs Sonnet 4.6: −0.9%p on the 232 common cases** (68.1% → 67.2%,
  majority-vote) — statistically tied, inside 4.6's own run range. A newer model
  generation delivered **no measurable improvement on embedded firmware**;
  weakest categories (dma, isr-concurrency, threading) are unchanged. Reports:
  `docs/BENCHMARK-n3-sonnet5.md`, `docs/BENCHMARK-DELTA-sonnet5-vs-sonnet46.md`,
  `docs/BENCHMARK-COMPARISON-2026-04-05.md` §10.

### Added

- **Embedded-Linux case expansion** (Phase A/B/C): kernel drivers, kernel
  networking, OTA (SWUpdate/RAUC), userspace, U-Boot, Yocto — public case count
  grew 185 → 219 (267 total with private).
- **Context Quality Mode** — measure a CLAUDE.md/context pack's effect on
  generation, with per-case effect classification (`context-compare`) and
  factor-level coverage feedback (`context-diagnose`).
- **Negatives / mutation oracle** (`/negatives`) — subtle-mutation cases that
  must *fail* checks, with an oracle verifier and progress auto-sync.
- **Hiloop integration** — per-check metrics, coverage gate, report schema
  version, and a stable `check_name` contract.
- `scripts/compare_models_intersection.py` — isolate pure model delta on the
  case set common to two runs (used for the Sonnet 5 vs 4.6 comparison).

### Changed

- **2-level SDK-bucket case layout** — `cases/<sdk>/<case-id>/` across 5 SDK
  buckets (zephyr, embedded-linux, freertos, esp-idf, stm32-hal); every
  `metadata.yaml` carries an `sdk:` field. Use `iter_case_dirs()` to walk cases.
- `scoped_contains` scope migration (REQ-03) — check substring matching is now
  comment/string-literal aware per file type.

### Fixed

- **`scripts/verify_results.py`** resolved case dirs as flat `cases/<id>` and
  silently verified 0 cases (false all-clear) under the 2-level layout — now
  resolves via `iter_case_dirs`, supports `--private-cases`, and fails loud
  (exit 2) on 0 verified.
- **case_id collisions** — 4 held-out private cases reused public IDs
  (`linux-driver-009/010`, `yocto-009/010`), silently shadowing results; the
  private cases were renumbered so all 267 case_ids are unique.
- Docker compile image (`embedeval-zephyr:latest`) rebuild documented — a
  missing image otherwise produces spurious L1 env-failures.

## [0.1.0] — 2026-04-18

- First public release: 5-layer evaluation pipeline (L0 static → L1 compile →
  L2 runtime → L3 behavioral → L4 mutation), Zephyr/FreeRTOS/ESP-IDF/STM32
  support, n=3 aggregate benchmarking with Wilson CIs, and the initial
  Haiku 4.5 vs Sonnet 4.6 comparison (233 cases).

[0.2.0]: https://github.com/Ecro/embedeval/releases/tag/v0.2.0
[0.1.0]: https://github.com/Ecro/embedeval/releases/tag/v0.1.0
