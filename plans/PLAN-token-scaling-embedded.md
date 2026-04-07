# PLAN: LLM Token Scaling — Embedded vs General SW

**Project:** embedeval
**Task:** Create comprehensive document analyzing token scaling economics and optimal workflow architecture for LLM-driven embedded development
**Priority:** High (strategic document, informs project direction)
**Created:** 2026-04-07
**Status:** completed

---

## 🎯 Executive Summary

> **TL;DR:** Create `docs/LLM-EMBEDDED-TOKEN-SCALING.md` — a strategic companion document that formalizes WHY token scaling works differently for embedded vs general SW, WHAT is automatable vs not, and HOW to architect the optimal human-AI workflow.

### What We're Doing
Adding the fourth companion document to the EmbedEval docs ecosystem. The existing three documents cover:
- **FAILURE-FACTORS.md** — WHERE LLMs fail (42 factors, diagnostic)
- **CONSIDERATIONS.md** — WHY they fail at production scale (14 patterns, analytical)
- **DEVELOPMENT-GUIDE.md** — HOW to use LLMs for embedded (7-phase workflow, tactical)

The new document adds:
- **TOKEN-SCALING.md** — THE ECONOMICS of token investment (strategic/architectural)

### Why It Matters
This is the "meta-question" behind the entire EmbedEval project: given that LLMs can now autonomously develop general software with minimal human input, why can't they do the same for embedded? Answering this rigorously — with data from our benchmarks, arxiv papers, and the existing doc ecosystem — positions EmbedEval as not just a benchmark but a strategic framework.

### Key Decisions
- **Language:** English (consistent with all existing docs/)
- **Location:** `docs/LLM-EMBEDDED-TOKEN-SCALING.md`
- **Scope:** Strategic/economic/architectural analysis (NOT a how-to guide — that's DEVELOPMENT-GUIDE.md)
- **Data sources:** EmbedEval benchmark data, 15+ arxiv papers (2024-2026), existing docs

### Estimated Impact
- **Complexity:** Medium (synthesis of existing research + new framing)
- **Risk Level:** Low (new document, no code changes)
- **Files Changed:** 1 new file + minor cross-references in existing docs
- **Estimated Time:** 2-3 hours

---

## ⚠️ REVIEW CHECKLIST - Action Required

> **📌 These items require your explicit verification before /execute**

### Structure & Scope
- [ ] **Document outline (Section 3 below):** Does the proposed 12-section structure cover everything you want?
- [ ] **Audience:** Is this for embedded engineers evaluating LLM adoption? Or for LLM researchers understanding embedded constraints? Or both?
- [ ] **Depth vs breadth:** Should we go deep on specific areas (e.g., detailed HIL-as-a-service analysis) or keep it high-level strategic?

### Content Decisions
- [ ] **The "Physical Ceiling" model:** Q(embedded) = min(Q_digital(tokens), Q_physical_ceiling) — is this framing correct and useful?
- [ ] **Percentage estimates:** "~70% automatable" for embedded — should we qualify this more carefully or is directional accuracy sufficient?
- [ ] **Korean summary section:** Should we include a Korean executive summary at the top for accessibility?

### Cross-References
- [ ] **Update existing docs:** Should we add "See also: TOKEN-SCALING.md" to the other three companion docs?
- [ ] **README.md:** Should this be listed in the main README?

### Business Logic
- [ ] **Implications section:** Should we include specific recommendations for team structure / investment priorities?
- [ ] **EmbedEval positioning:** Should we explicitly position EmbedEval's role in the token-scaling ecosystem?

**✋ Stop here if ANY checkbox is unclear - ask questions before proceeding!**

---

## 📚 Prior Work (Knowledge Retrieval)

### Existing Companion Documents
| Document | Content | Relevance to New Doc |
|----------|---------|---------------------|
| `docs/LLM-EMBEDDED-FAILURE-FACTORS.md` | 42 code factors, 6 categories, meta-properties M1-M6 | Core data source — M1 (training sparsity), M2 (silent failure), M3 (implicit gap) directly explain token scaling limits |
| `docs/LLM-EMBEDDED-CONSIDERATIONS.md` | 14 production failure patterns, 3-tier trust model, benchmark self-critique | Production-scale evidence for "non-tokenizable" section; trust tiers map to automation zones |
| `docs/LLM-EMBEDDED-DEVELOPMENT-GUIDE.md` | 7-phase workflow, knowledge base, context templates, prompt engineering, maturity model | The existing workflow IS the "how" — new doc explains the "why" behind the human/AI split in each phase |
| `docs/BENCHMARK-COMPARISON-2026-04-05.md` | Haiku vs Sonnet quantitative comparison | Pass rates by category = direct evidence for token scaling effectiveness per domain |

### Research Sources (from /research phase)
| Paper | Key Contribution |
|-------|-----------------|
| arXiv 2408.03314 — Scaling Test-Time Compute | "Scaling inference compute optimally > 14x larger model" — foundational for token-scaling thesis |
| arXiv 2502.14382 — S*: Test Time Scaling for Code | Non-reasoning models surpass reasoning models via test-time scaling |
| arXiv 2503.23803 — Thinking Longer, Not Larger | SWE-SynInfer+ with patch verification phase — directly applicable |
| arXiv 2506.11003 — EmbedAgent (ICSE 2026) | 29.4% → 65.1% with RAG + compiler feedback — embedded-specific token scaling evidence |
| arXiv 2509.09970 — Securing LLM-Generated Firmware | 92.4% vulnerability remediation with iterative agent-driven validation |
| arXiv 2603.25928 — Self-Organizing Multi-Agent for SW Dev | Multi-agent coordination for extended development efforts |
| arXiv 2507.00421 — Embedded DevOps Survey | CI feasible, CD rare due to physical constraints — quantifies the deployment gap |
| Electronic Design — "Don't Vibe Code Your Embedded System" | Industry perspective on token-scaling limits |
| Anthropic — Measuring Agent Autonomy | Trust builds gradually, autonomy increases with experience |
| DORA 2025 Report | "AI is an amplifier, not a fix" — applies directly to embedded |

### EmbedEval Benchmark Data
| Metric | Value | Implication for Token Scaling |
|--------|-------|------------------------------|
| Haiku pass@1 | 62.6% (112/179) | Baseline: what "moderate tokens" achieves |
| Sonnet pass@1 | ~85% | Baseline: what "more capable model" achieves |
| DMA pass@1 | 0% (Haiku), 44% (Sonnet) | Physical ceiling: no amount of tokens helps without datasheet context |
| ISR-concurrency | 11-33% | Implicit knowledge gap: token scaling limited by training data |
| Explicit vs Implicit gap | 35%p | The gap that RAG/context engineering can close |
| kconfig pass@1 | 75-88% | Digital-friendly domain: token scaling works well |

---

## 📋 Document Outline

### Proposed Structure for `docs/LLM-EMBEDDED-TOKEN-SCALING.md`

```
# Token Scaling in Embedded Development: Why Infinite Tokens Aren't Enough

Companion documents:
- FAILURE-FACTORS.md (WHERE LLMs fail)
- CONSIDERATIONS.md (WHY at production scale)
- DEVELOPMENT-GUIDE.md (HOW to use LLMs)
- → THIS DOCUMENT (THE ECONOMICS of token investment)

## 1. The Token-Scaling Thesis
   - General SW: closed digital feedback loop
   - The virtuous cycle: generate → test → fix → deploy → feedback → iterate
   - Why token investment scales quality (test-time compute research)
   - Evidence: S*, CodeMonkeys, SWE-SynInfer+ results

## 2. The Physical Ceiling
   - Formalization: Q(embedded) = min(Q_digital(tokens), Q_physical_ceiling)
   - The asymptotic scaling curve (diagram)
   - Why general SW has no ceiling but embedded does
   - The 5-layer verification map:
     - L0 Static: 100% automatable ✓
     - L1 Compile: ~90% automatable ✓
     - L2 Runtime/Emulation: ~50% of real behavior
     - L3 Behavioral/HIL: requires hardware
     - L4 Physical stress: not automatable
   - EmbedEval data as evidence

## 3. The Feedback Loop Gap
   - General SW: seconds-minutes feedback loop
   - Embedded: minutes-to-months feedback loop
   - Five broken links in the embedded autonomous cycle:
     1. Code generation (degraded but improvable)
     2. Test-fix inner loop (slow + limited)
     3. Deployment (physical, risky, regulated)
     4. User feedback (noisy, physical, slow)
     5. Feedback-to-token conversion (partially manual)

## 4. Token-Scalable Activities (The Digital 70%)
   - Code generation with compiler feedback (EmbedAgent: +35%p)
   - Static analysis: exhaustive multi-pattern scanning
   - Test case generation: thousands of emulator-testable cases
   - Code review: multi-agent adversarial review (92.4% vuln remediation)
   - Design space exploration: architecture alternatives
   - Configuration optimization: Kconfig/DT space search
   - Documentation generation
   - Table: activity × token strategy × expected ROI

## 5. Non-Tokenizable Activities (The Physical 30%)
   - Real-time timing verification (WCET, jitter, interrupt latency)
   - Electrical/analog behavior (EMI/EMC, signal integrity)
   - Manufacturing variance (component tolerance, PCB defects)
   - Environmental conditions (-40°C to +85°C, vibration)
   - Safety certification (ISO 26262, IEC 61508, DO-178C)
   - Silicon errata handling
   - Multi-device integration testing
   - Why this 30% contains the most critical bugs

## 6. The Speed Mismatch Trap
   - Code generation speed >> verification speed
   - The "quality debt" accumulation model
   - DORA 2025: "AI amplifies existing practices"
   - Risk: teams ship faster than they can validate
   - Mitigation: gate deployment on physical verification

## 7. Pushing the Ceiling Higher (Bridge Technologies)
   - Digital Twins: 50% → 70-80% fidelity
   - HIL-as-a-Service: remote hardware farms
   - RAG with datasheets: closing the 35%p implicit gap
   - LLM + Formal Verification: addressing silent failures
   - Self-evolving agents for embedded
   - Projected ceiling trajectory: now ~60%, 2-3yr ~80%, theoretical max ~90%

## 8. The Optimal Workflow Architecture
   - Three-zone model diagram:
     - Token Zone (maximize token investment)
     - Bridge Zone (invest in infrastructure)
     - Human Zone (maximize expert involvement)
   - Mapping to DEVELOPMENT-GUIDE 7-phase workflow
   - Per-phase human/AI/infra allocation
   - How EmbedEval fits as the quality gate

## 9. Comparison: General SW vs Embedded — Full Matrix
   - Side-by-side comparison table (12+ dimensions)
   - The "1-person startup" thought experiment
   - Why LLMs democratize web dev but not embedded dev
   - The fixed-cost problem (hardware labs, test equipment, certification)

## 10. Implications for Teams & Organizations
   - What kind of teams benefit most from token-scaling?
   - Investment priorities: infrastructure > tokens
   - The "bridge builder" role (neither pure SW nor pure HW)
   - When NOT to invest in token scaling (small fleet, regulated, safety-critical)

## 11. Open Questions & Future Research
   - Can digital twins reach 95% fidelity?
   - Will LLMs learn to ask for datasheets?
   - Can formal verification scale to system-level?
   - Is there a token scaling law for embedded? (no evidence yet)

## 12. Sources
   - All 15+ arxiv papers cited
   - EmbedEval benchmark data references
   - Industry reports (DORA, Anthropic autonomy research)
```

---

## 🏗️ Technical Design

### Architecture
This is a standalone markdown document. No code changes required. It synthesizes existing data into a new analytical framework.

### Design Decisions
1. **Companion document pattern** — Same level as the other three docs, not a sub-document
   - **Rationale:** This is an independent analytical dimension (economics/strategy) not covered by existing docs
   - **Alternative:** Could be a new section in CONSIDERATIONS.md, but it's too large (~3000+ words) and different in focus

2. **English language** — Consistent with all existing docs
   - **Rationale:** Repository is public, English is the lingua franca for technical docs
   - **Alternative:** Korean version — could be added later if needed

3. **Data-driven** — Every claim backed by EmbedEval data or arxiv citations
   - **Rationale:** This isn't an opinion piece; it's a research synthesis
   - **Alternative:** Could be more speculative/visionary, but data grounds it

### Cross-References
- Add "See also: TOKEN-SCALING.md" link to:
  - `docs/LLM-EMBEDDED-FAILURE-FACTORS.md` (top, companion section)
  - `docs/LLM-EMBEDDED-CONSIDERATIONS.md` (top, companion section)
  - `docs/LLM-EMBEDDED-DEVELOPMENT-GUIDE.md` (top, companion section)

### Diagrams
ASCII art diagrams (consistent with existing docs style):
1. General SW feedback loop (closed cycle)
2. Embedded asymptotic scaling curve with ceiling
3. Three-zone model (Token/Bridge/Human)
4. 5-layer verification automation map

---

## 📝 Implementation Plan

### Phase 1: Document Creation
- [ ] Create `docs/LLM-EMBEDDED-TOKEN-SCALING.md` with full 12-section structure
- [ ] Write Section 1 (Token-Scaling Thesis) — General SW model with arxiv citations
- [ ] Write Section 2 (Physical Ceiling) — Formalization with EmbedEval L0-L4 data
- [ ] Write Section 3 (Feedback Loop Gap) — 5 broken links analysis
- [ ] Write Section 4 (Token-Scalable Activities) — with ROI table and evidence
- [ ] Write Section 5 (Non-Tokenizable Activities) — with evidence from CONSIDERATIONS.md
- [ ] Write Section 6 (Speed Mismatch Trap) — DORA data + risk model
- [ ] Write Section 7 (Bridge Technologies) — Digital twin, HIL, RAG, formal verification
- [ ] Write Section 8 (Optimal Workflow) — Three-zone model + DEVELOPMENT-GUIDE mapping
- [ ] Write Section 9 (Comparison Matrix) — Full side-by-side table
- [ ] Write Section 10 (Team Implications) — Practical recommendations
- [ ] Write Section 11 (Open Questions) — Future research directions
- [ ] Write Section 12 (Sources) — Complete bibliography

### Phase 2: Cross-References
- [ ] Update FAILURE-FACTORS.md companion section
- [ ] Update CONSIDERATIONS.md companion section
- [ ] Update DEVELOPMENT-GUIDE.md companion section

### Phase 3: Sync & Verification
- [ ] Run `uv run python scripts/sync_docs.py` for doc counts
- [ ] Verify all internal cross-references are correct
- [ ] Verify all arxiv links are valid
- [ ] Read through for consistency with existing doc style and terminology

---

## 🧪 Testing Strategy

### Content Verification
- All EmbedEval data points match `docs/BENCHMARK-COMPARISON-2026-04-05.md`
- All arxiv citations have valid paper IDs
- Cross-references between documents resolve correctly
- ASCII diagrams render correctly in GitHub markdown

### Style Consistency
- Matches the formal-but-accessible tone of existing docs
- Uses same table formatting patterns
- Uses same "What LLM generates" vs "What engineer writes" comparison style where applicable
- No Korean in the document (English only per feedback memory)

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Percentage estimates (70% automatable) feel arbitrary | Medium — undermines credibility | Qualify all numbers as directional estimates, cite EmbedEval layer mapping as basis |
| Overlap with existing CONSIDERATIONS.md Section 3 (Practical Guidance) | Low — different focus | Reference CONSIDERATIONS.md for detailed guidance, keep TOKEN-SCALING at strategic level |
| Overlap with DEVELOPMENT-GUIDE Phase 0-6 human/AI split | Low — complementary | TOKEN-SCALING explains the WHY behind the split that DEVELOPMENT-GUIDE describes |
| Document becomes too long | Medium — won't be read | Target ~3000-4000 words (similar to CONSIDERATIONS.md), use executive summary + tables |

---

## ✅ Success Criteria

- [ ] Document exists at `docs/LLM-EMBEDDED-TOKEN-SCALING.md`
- [ ] All 12 sections complete with data and citations
- [ ] Cross-references added to all 3 companion documents
- [ ] Consistent with existing doc ecosystem terminology (M1-M6, L0-L4, Tier 1-3)
- [ ] All arxiv citations are valid and correctly attributed
- [ ] ASCII diagrams render correctly
- [ ] Document answers the core question: "Why can't you just throw tokens at embedded?"

---

## 📊 Estimated Effort

- **Complexity:** Medium
- **Estimated Time:** 2-3 hours
- **Files Changed:** 1 new + 3 updated (cross-references)

---

## ➡️ Next Step

After review approval:
```
/execute token-scaling-embedded
```
