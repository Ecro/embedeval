# EmbedEval Methodology

## 5-Layer Evaluation Architecture

EmbedEval evaluates LLM-generated embedded firmware code through five progressively deeper verification layers. Each layer targets a distinct class of defects. Code must pass all layers sequentially — failure at any layer halts evaluation for that case.

### Layer 0: Static Analysis

**Purpose:** Catch structural and syntactic issues without compilation.

**What it catches:**
- Code that "looks like" firmware but violates fundamental format rules
- Missing required configuration symbols (e.g., `CONFIG_SPI=y`)
- Device tree syntax violations (missing `compatible`, wrong node structure)
- ISR handler signature errors
- Conflicting or contradictory configuration options

**Implementation:** Each case provides a `checks/static.py` module with a `run_checks(generated_code: str) -> list[CheckDetail]` function. Checks are domain-specific: Kconfig cases validate `CONFIG_` prefix formatting, device tree cases validate node structure, ISR cases validate volatile qualifiers and atomic operations.

**Why it matters:** Static analysis filters out responses where the LLM produced plausible-looking but fundamentally malformed output. This is the "does it even look right?" gate.

### Layer 1: Compilation

**Purpose:** Verify that generated code compiles against the Zephyr build system.

**What it catches:**
- Missing includes and undefined symbols
- Type errors and incompatible function signatures
- Linker errors from missing dependencies
- Build system configuration errors

**Implementation:** Runs `west build` inside a Docker container with the Zephyr SDK. The build target matches the case's `platform` field (e.g., `native_sim`, `qemu_arm`).

**Why it matters:** Many LLM responses produce syntactically valid C that references APIs or macros that do not exist in the target Zephyr version. Compilation catches these hallucinated APIs.

### Layer 2: Runtime Execution

**Purpose:** Execute the compiled firmware and detect runtime failures.

**What it catches:**
- Segmentation faults and null pointer dereferences
- Stack overflows in ISR context
- Deadlocks and priority inversions
- Infinite loops and hangs (via timeout)
- QEMU/native_sim assertion failures

**Implementation:** Executes the compiled binary under `native_sim` or QEMU with a configurable timeout. Exit code and stdout/stderr are captured for analysis.

**Why it matters:** Code that compiles cleanly may still crash at runtime due to incorrect memory access patterns, uninitialized peripherals, or concurrency bugs that only manifest during execution.

### Layer 3: Behavioral Verification

**Purpose:** Verify that the code produces correct behavior, not just absence of crashes.

**What it catches:**
- Kconfig fragments that compile but enable wrong options
- Device tree overlays that parse but bind to wrong compatibles
- ISR handlers that run but corrupt shared state
- DMA configurations that transfer but to wrong addresses
- Code that satisfies syntax but violates domain invariants

**Implementation:** Each case provides a `checks/behavior.py` module with domain-specific assertions and metamorphic properties. Metamorphic testing checks invariants that must hold regardless of specific implementation choices (e.g., "if SPI_DMA is enabled, both SPI and DMA must also be enabled").

**Why it matters:** This is the most critical layer. Code that compiles and runs without crashing can still be completely wrong. Layer 3 catches the "compiles but wrong" class of bugs that are endemic to LLM-generated firmware code.

### Layer 4: Mutation Testing (Planned for v1.1)

**Purpose:** Verify that the evaluation itself is rigorous enough to catch bugs.

**What it will catch:**
- Weak or insufficient Layer 3 checks that pass obviously broken code
- Missing edge case coverage in behavioral assertions
- Overly permissive static checks

**Implementation:** Systematically introduces known mutations (seeded bugs) into reference solutions and verifies that at least one evaluation layer detects each mutation. Cases where mutations pass undetected indicate gaps in the check suite.

**Why it matters:** Mutation testing is a meta-verification layer that ensures the benchmark itself maintains high quality. Without it, there is no guarantee that passing all layers actually means the code is correct.

## Case Design Principles

### Self-Contained Verification

Every case must be verifiable without external dependencies beyond the Zephyr SDK Docker image. Cases must not require physical hardware, external services, or manual inspection.

### Domain Grounding

Each case targets a specific, well-defined embedded firmware task drawn from real-world Zephyr development patterns. Prompts include sufficient context (board definitions, existing code, requirements) to make the task unambiguous to a domain expert.

### Reference Solution Required

Every case includes a verified reference solution (`reference/main.c`) that passes all evaluation layers. This serves as both a correctness oracle and a sanity check for the evaluation pipeline itself.

### Deterministic Evaluation

All checks produce deterministic pass/fail results. There is no subjective scoring, no "partial credit," and no LLM-as-judge. A case either passes all layers or it does not.

## Difficulty Tiers

Cases are classified into three difficulty tiers based on the depth of domain knowledge and reasoning required:

### Easy

- Single-concept tasks (e.g., "enable SPI with DMA via Kconfig")
- Minimal context needed beyond the prompt
- Straightforward mapping from requirements to code
- Expected pass@1 for strong models: >80%

### Medium

- Multi-concept tasks requiring integration (e.g., "configure device tree overlay for I2C sensor with interrupt")
- Requires understanding dependency chains and side effects
- May involve coordinating multiple configuration files
- Expected pass@1 for strong models: 40-70%

### Hard

- Complex tasks requiring deep domain reasoning (e.g., "implement ISR-safe ring buffer with proper synchronization")
- Requires understanding concurrency primitives, memory ordering, hardware constraints
- May involve subtle correctness requirements that are easy to overlook
- Expected pass@1 for strong models: <30%

## Scoring: pass@k

EmbedEval uses the **pass@k** metric, the standard for code generation benchmarks.

**pass@k** measures the probability that at least one of k generated samples passes all evaluation layers for a given case.

For a case with `n` total samples and `c` correct samples:

```
pass@k = 1 - C(n-c, k) / C(n, k)
```

Where `C(a, b)` is the binomial coefficient "a choose b."

**Why pass@k?**

- **pass@1** measures first-attempt accuracy — critical for interactive use where developers expect a working solution on the first try
- **pass@5** measures whether the model can produce a correct solution given multiple attempts — relevant for batch generation workflows
- The unbiased estimator avoids the selection bias of "best of k" approaches

**Reporting:** EmbedEval reports pass@1 and pass@5 for each model, broken down by category and difficulty tier.

## How EmbedEval Differs from SWE-bench

| Dimension | SWE-bench | EmbedEval |
|-----------|-----------|-----------|
| **Domain** | General Python software engineering | Embedded firmware (Zephyr RTOS) |
| **Verification** | Unit test pass/fail | 5-layer progressive verification |
| **Mislabeling** | ~48% mislabeled instances reported | Reference solutions verified through all 5 layers |
| **Hardware concerns** | None | ISR safety, DMA, register access, real-time constraints |
| **Build system** | pip install | west build (Zephyr SDK) |
| **Runtime** | Python interpreter | native_sim, QEMU ARM |
| **Behavioral checks** | Existing project tests | Custom domain-specific assertions + metamorphic properties |

SWE-bench's reliance on existing project test suites means its evaluation quality varies with the quality of each project's tests. Research has identified a ~48% mislabeling rate where "gold" patches do not actually resolve the stated issues. EmbedEval addresses this by designing custom, multi-layer verification for every case and requiring all reference solutions to pass the complete evaluation pipeline.
