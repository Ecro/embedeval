# EmbedEval Roadmap

EmbedEval is in active development. This document tracks the direction of the next minor releases. Items closer to the top are more likely to land sooner; items at the bottom are exploratory.

> **How to influence this roadmap:** open a [GitHub Issue](https://github.com/Ecro/embedeval/issues) describing your use case. Pull requests for any of these items are welcome — see [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).

---

## v0.1 — Public Release (current)

The first version focused on producing a benchmark with **n=3 reproducible results**, **statistical confidence intervals**, and a **5-layer evaluation pipeline** that goes beyond simple `pass/fail` scoring.

- 233 cases (185 public + 48 private held-out)
- 23 categories across 6 platforms (Zephyr, ESP-IDF, STM32 HAL, FreeRTOS, Linux drivers, Yocto)
- 5-layer evaluation: L0 Static → L1 Compile → L2 Runtime → L3 Heuristic → L4 Mutation
- pass@k (unbiased Chen et al. 2021) + Wilson 95% CI
- n=3 baseline runs published with stability analysis
- `--scenario bugfix`, `--feedback-rounds`, `--retest-only`, `agent` mode

---

## v0.2 — Coverage & Reproducibility

**Theme:** make EmbedEval easier for outside contributors to extend, and broaden empirical coverage where the v0.1 baseline is thinnest.

### Likely

- **Expand model coverage.** v0.1 published n=3 results for two models. v0.2 aims to onboard additional models — both proprietary and open-weight — through a contribution-friendly evaluation harness rather than a hard-coded list. Specific model picks will follow community demand.
- **HF Space — submission flow.** The current Space is a static leaderboard. v0.2 plans an opt-in submission form that runs L0+L3 evaluation on a hosted runner so external contributors can add results without standing up the full Docker stack.
- **FreeRTOS expansion.** v0.1 has only 5 STM32+FreeRTOS cases. v0.2 plans 15+ pure FreeRTOS cases (queue safety, ISR-to-task notification, task notification vs queue trade-offs, etc.) to reduce the Zephyr platform bias.
- **More Linux kernel driver cases.** Bring `linux-driver` from 8 → 20+ cases covering platform_driver, character device, sysfs, netlink, and dma_buf patterns.
- **Better failure taxonomy.** The current 8-pattern classifier (`happy_path_bias`, `semantic_mismatch`, …) is rule-based. v0.2 plans a calibration study against human-labeled failure causes.

### Exploratory

- **Tech report / arXiv preprint.** A 4-6 page tech report is on the wishlist if the community finds the methodology worth citing.
- **Cost-vs-performance scoring.** Add per-model `$/case` and `tokens/case` columns so practitioners can pick on the Pareto frontier.
- **Sensitivity expansion.** Run the existing prompt sensitivity suite at `--sample 100 --variants 5` and publish per-category robustness numbers.

---

## v0.3 — Beyond Single-File Generation

**Theme:** push past one-shot single-file code generation toward how engineers actually use LLMs in embedded work.

### Likely

- **Multi-file project scaffolding.** v0.1 cases are single-file. Add cases that require generating a coherent set of headers, source files, Kconfig, and CMakeLists across a small subsystem.
- **Agent mode hardening.** The `embedeval agent` command exists but is not heavily tested. v0.3 plans n=3 baselines for multi-turn agent runs with comparison to single-shot.
- **Cross-platform migration cases.** "Port this Zephyr driver to ESP-IDF" — measures the 'cross_domain' reasoning type more directly than v0.1 cases do.

### Exploratory

- **Hardware-in-the-loop layer (L5).** Optional layer that flashes generated code to a real board (nrf52840dk, esp32-s3) and reads back signals via Renode or a USB-attached logic analyzer. Heavy infra, but the only way to catch register-level hallucinations end-to-end.
- **FPGA / RTL generation.** Verilog/SystemVerilog for soft-core peripherals. Adjacent to the embedded firmware target audience but requires its own toolchain.

---

## v1.0 — Stability and Long-Term Maintenance

**Theme:** v1.0 happens when the schema is stable enough that case authors and model evaluators can rely on it for years.

- Frozen `metadata.yaml` schema with semantic versioning
- Migration guides for any breaking schema changes
- Public CI that runs the canonical n=3 baseline on every release
- Citation-grade documentation (versioned methodology, per-release changelogs)
- Long-term maintenance commitment statement

---

## Out of Scope (for now)

These are not on the roadmap — but PRs that change our minds are welcome.

- **Generic Python or web framework benchmarks.** EmbedEval stays embedded-focused. Use HumanEval, SWE-bench, or Aider Polyglot for general code.
- **MCU-side LLM inference.** Running an LLM on a microcontroller is a separate concern; EmbedEval evaluates LLMs *that generate firmware*, not LLMs *that run on firmware*.
- **Closed-source case set.** All 185 public cases stay open. The 48 private cases stay private *only* for contamination control, and their metadata (category, difficulty) is published.

---

## Tracking

- [GitHub Milestones](https://github.com/Ecro/embedeval/milestones) — concrete tasks per release
- [GitHub Discussions](https://github.com/Ecro/embedeval/discussions) — roadmap input from users
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — current methodology
- [`docs/LLM-EMBEDDED-CONSIDERATIONS.md`](docs/LLM-EMBEDDED-CONSIDERATIONS.md) — research findings driving the roadmap

Last updated: 2026-04-16
