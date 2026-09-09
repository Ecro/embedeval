# Changelog

All notable changes to EmbedEval are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Benchmark results

- **Opus 5, 267 cases (public + held-out private), n=1, full Docker L1/L2 gate:
  pass@1 70.0%** (187/267, CI [64.3%, 75.2%]), quality (L0+L3) 83.5%. Public
  slice 73.1%, private slice 56.2%. Ahead of claude-sonnet-5 (67.3%), but only
  Opus 5 is scored with the fixed checks below — the other rows replay old-check
  verdicts and are a floor. 61.8% → 70.0% on identical public generations plus a
  fresh private slice.
- **12 of the 48 private cases cannot be passed by any model in this
  environment** — their reference solutions do not build (nrf52840dk DT aliases
  absent, `zephyr/dfu/dfu_target.h` missing, link failures). Only 16 of 28
  compilable private cases have a building reference, and all 12 of Opus 5's
  private-slice L1 failures are exactly those cases, so the private slice is a
  case-health number as much as a capability number. Opus 5's four genuine
  compile failures are all public: isr-concurrency-004/006/011, threading-012.

### Fixed

- **L3 checks scored coding style, not correctness** — 22 cases recovered after
  fixing four defect classes (comment-as-call ordering across 97 files, literal
  idioms rejecting `atomic_t`/`#define`/`k_msleep`, whole-file offsets breaking
  on helper extraction, and two checks that were factually wrong — systemd
  `StartLimit*` belongs in `[Unit]`, not `[Service]`). References still 219/219,
  mutation oracle still 77/77, 0 pass→fail regressions. Two checks got stricter.
  See `docs/CHECK-QUALITY-AUDIT-2026-09.md`.
- **`claude -p --output-format json` parsing** — the CLI returns a single result
  object, not a list of events; the mismatch silently scored every case FAIL@L0.
- **aarch64 hosts could not run L1/L2** — 32-bit `native_sim` fails CMake
  configure; `EMBEDEVAL_NATIVE_SIM_BOARD=native_sim/native/64` plus board-overlay
  aliasing fixes it, and L2 no longer treats the qualified board as hardware
  (which auto-passed runtime for ~60 cases).
- **`scripts/sync_docs.py`** aborts instead of silently rewriting case counts to
  public-only when `../embedeval-private` is missing.

- **L2 leaked one Docker container per runtime case.** Embedded firmware loops
  forever; `subprocess`'s timeout killed only the local `docker run` client
  while the container kept executing. Past 100 orphans the host ran out of
  memory and killed the benchmark mid-run. The container command now carries
  `timeout --signal=KILL`, and exit codes 124/137 count as a normal firmware
  stop. Re-scoring also got ~4x faster.
- **Run archives no longer write detail files for tracker-merged results.** A
  partial run synthesised 219 stubs with empty `generated_code`; copied into a
  re-score input set they overwrote the real details and scored pass@1 10.1%
  with 223 L0 failures. `scripts/rescore_run.py` now aborts on such a record.

### Added

- `scripts/rescore_run.py` — replay an archived run's stored generations through
  the current evaluator (no API spend) when a check or environment fix
  invalidates layer results but not the generations.
- `check_utils`: `blank_comments`, `find_in_code`, `find_in_yocto`,
  `expand_string_defines`, `function_bodies`, `ordered_in_same_function`.

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
