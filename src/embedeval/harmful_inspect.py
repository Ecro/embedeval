"""Harmful-case sub-classification for context-pack comparison.

When `context-compare` reports an `Hm` (harmful) count, each case is
either a real attention trade-off (pack distracted the LLM from
structural correctness) or EmbedEval check brittleness (pack led the
LLM to a valid API variant the case's checks don't accept).

These look identical in the Hm count but require opposite fixes —
editing the pack vs. editing `cases/<case>/checks/static.py`. This
module classifies each Hm case using a layer-failure heuristic, which
does NOT require loading the generated code: it reads only the
tracker's `failed_at_layer` and `failed_checks` fields.

Heuristic (reasoning in classify_harmful docstring):

    Layer  Name        Classification
    ─────  ──────────  ──────────────────────
    L0     Static      LIKELY_BRITTLENESS  (regex-based, rejects variants)
    L1     Compile     LIKELY_REAL         (code doesn't compile)
    L2     Runtime     LIKELY_REAL         (runtime divergence)
    L3     Behavioral  UNCERTAIN           (regex on output — could be either)
    L4     Mutation    LIKELY_REAL         (mutation meta-check failed)

`inspect_harmful` returns a list of classified cases for CI/JSON
consumers; `format_harmful_table` renders them to stdout.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from embedeval.context_compare import CaseEffect, classify_effect
from embedeval.test_tracker import TrackerData, load_tracker


class HarmfulClassification(str, Enum):
    """Sub-classification of a harmful case (bare passed, expert failed)."""

    LIKELY_BRITTLENESS = "likely-brittleness"
    LIKELY_REAL = "likely-real"
    UNCERTAIN = "uncertain"


class HarmfulCase(BaseModel):
    """One harmful case with layer-based sub-classification.

    `failed_at_layer` and `failed_checks` come directly from the expert
    tracker's CaseResult. `reasoning` is a human-readable note for the
    table / JSON consumer. `inspect_hint` points the user at the next
    action (pack edit vs. check edit) based on classification.
    """

    case_id: str
    category: str
    classification: HarmfulClassification
    failed_at_layer: int | None
    failed_checks: list[str] = Field(default_factory=list)
    reasoning: str
    inspect_hint: str


def classify_harmful(
    failed_at_layer: int | None,
    failed_checks: list[str],
) -> tuple[HarmfulClassification, str, str]:
    """Classify a harmful case by its L0-L4 failure layer.

    Returns (classification, reasoning, inspect_hint).

    - L0 (static, regex-based): LIKELY_BRITTLENESS. The most common
      false-positive mode is a valid API variant that static regex
      doesn't accept (`dma_config` vs `dma_configure`, `printf` vs
      `printk`). Bare passed the same regex on different code, so the
      LLM did produce DIFFERENT code — the question is whether the new
      code is semantically worse.
    - L1 (compile): LIKELY_REAL. Code physically doesn't compile. The
      pack steered the LLM to broken code.
    - L2 (runtime): LIKELY_REAL. Code compiles but diverges at runtime
      (crash, wrong output).
    - L3 (behavioral, regex on output): UNCERTAIN. Same brittleness
      risk as L0 but on printed output patterns. Could be a valid
      rewording of the log line or a real behavior change.
    - L4 (mutation meta-verification): LIKELY_REAL. The case's own
      mutation checks caught that the generated code is
      non-discriminating.
    - None (no layer recorded): UNCERTAIN.
    """
    if failed_at_layer is None:
        return (
            HarmfulClassification.UNCERTAIN,
            "no failed_at_layer recorded",
            "manual inspection required — check expert run logs",
        )
    if failed_at_layer == 0:
        return (
            HarmfulClassification.LIKELY_BRITTLENESS,
            "L0 (static) failure: regex-based checks often reject valid API variants",
            "inspect cases/<case>/checks/static.py — may need to "
            "accept additional API variants via check_utils helpers",
        )
    if failed_at_layer == 1:
        return (
            HarmfulClassification.LIKELY_REAL,
            "L1 (compile) failure: generated code does not compile",
            "edit the context pack — it steered the LLM to broken code",
        )
    if failed_at_layer == 2:
        return (
            HarmfulClassification.LIKELY_REAL,
            "L2 (runtime) failure: generated code diverges at runtime",
            "edit the context pack — runtime divergence is a real regression",
        )
    if failed_at_layer == 3:
        return (
            HarmfulClassification.UNCERTAIN,
            "L3 (behavioral) failure: regex on output — could be a "
            "reworded log line or a real behavior change",
            "manually compare bare vs expert generated.c — if the "
            "output difference is semantic, edit pack; if cosmetic, "
            "loosen the behavior regex",
        )
    if failed_at_layer == 4:
        return (
            HarmfulClassification.LIKELY_REAL,
            "L4 (mutation) failure: mutation meta-check rejected the "
            "solution as non-discriminating",
            "edit the context pack — the generated code is too generic",
        )
    return (
        HarmfulClassification.UNCERTAIN,
        f"unknown failed_at_layer={failed_at_layer}",
        "manual inspection required",
    )


def _category_of(case_id: str) -> str:
    parts = case_id.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return case_id


def inspect_harmful(
    bare_dir: Path,
    expert_dir: Path,
    model: str | None = None,
) -> list[HarmfulCase]:
    """Find all harmful cases (bare pass → expert fail) and classify
    each by its expert-tracker failure layer.

    Returns the list sorted by (category, case_id) for stable output.
    """
    bare_tracker = load_tracker(bare_dir)
    expert_tracker = load_tracker(expert_dir)

    if not bare_tracker.results:
        raise ValueError(f"No tracker results in bare dir: {bare_dir}")
    if not expert_tracker.results:
        raise ValueError(f"No tracker results in expert dir: {expert_dir}")

    chosen_model = _resolve_model(bare_tracker, expert_tracker, requested=model)

    bare_cases = bare_tracker.results.get(chosen_model, {})
    expert_cases = expert_tracker.results.get(chosen_model, {})

    harmful: list[HarmfulCase] = []
    for cid in sorted(set(bare_cases) & set(expert_cases)):
        b = bare_cases[cid]
        e = expert_cases[cid]
        if classify_effect(b.passed, e.passed) != CaseEffect.HARMFUL:
            continue
        classification, reasoning, hint = classify_harmful(
            e.failed_at_layer, e.failed_checks
        )
        harmful.append(
            HarmfulCase(
                case_id=cid,
                category=_category_of(cid),
                classification=classification,
                failed_at_layer=e.failed_at_layer,
                failed_checks=e.failed_checks,
                reasoning=reasoning,
                inspect_hint=hint,
            )
        )
    return sorted(harmful, key=lambda h: (h.category, h.case_id))


def _resolve_model(
    bare_tracker: TrackerData,
    expert_tracker: TrackerData,
    requested: str | None,
) -> str:
    """Pick the model to inspect. Requires the same model be present in
    both trackers; errors if the bare and expert dirs don't share one."""
    shared = set(bare_tracker.results.keys()) & set(expert_tracker.results.keys())
    if not shared:
        raise ValueError(
            "No model is present in both bare and expert trackers; "
            f"bare={sorted(bare_tracker.results)}, "
            f"expert={sorted(expert_tracker.results)}"
        )
    if requested:
        if requested not in shared:
            raise ValueError(
                f"Model {requested!r} not present in both trackers. "
                f"Shared: {sorted(shared)}"
            )
        return requested
    # Exclude mock unless nothing else is available — mock is
    # context-independent and can't produce a meaningful harmful case.
    non_mock = sorted(m for m in shared if m != "mock")
    if len(non_mock) == 1:
        return non_mock[0]
    if not non_mock and "mock" in shared:
        return "mock"
    raise ValueError(
        f"Multiple models shared ({sorted(shared)}); pass --model to disambiguate."
    )


def format_harmful_table(cases: list[HarmfulCase]) -> str:
    """Render harmful cases as a compact stdout table."""
    lines: list[str] = []
    if not cases:
        lines.append("No harmful cases found (bare pass → expert fail).")
        return "\n".join(lines)

    # Summary counts by classification
    counts = {c.value: 0 for c in HarmfulClassification}
    for hc in cases:
        counts[hc.classification.value] += 1

    lines.append(f"Harmful cases: {len(cases)} total")
    lines.append(
        f"  likely-brittleness: {counts['likely-brittleness']}  "
        f"(inspect cases/*/checks/static.py)"
    )
    lines.append(
        f"  likely-real:        {counts['likely-real']}  (edit the context pack)"
    )
    lines.append(f"  uncertain:          {counts['uncertain']}  (manual inspection)")
    lines.append("")

    header = f"  {'Case':<28} {'L':>2}  {'Classification':<20}  Failed checks"
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))
    for hc in cases:
        layer = f"L{hc.failed_at_layer}" if hc.failed_at_layer is not None else "?"
        checks = ", ".join(hc.failed_checks[:3])
        if len(hc.failed_checks) > 3:
            checks += f" (+{len(hc.failed_checks) - 3})"
        lines.append(
            f"  {hc.case_id:<28} {layer:>2}  {hc.classification.value:<20}  {checks}"
        )
    return "\n".join(lines)
