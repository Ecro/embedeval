"""Factor-level context coverage diagnosis.

Takes a team benchmark run and an expert benchmark run, rolls each
failed check up to its FAILURE-FACTORS category, and tells the user
which categories their CLAUDE.md fails to cover compared to the expert
pack's ceiling.

This is the prescriptive layer on top of `context-compare`. Where
context-compare reports Lift and Gap numbers, context-diagnose points
at which category of embedded principles to add to the team's context.

Design notes
------------
- Comparison direction is team → expert (D2 in PLAN-context-diagnose).
  Bare is optional context; the residual gap-to-ceiling is the
  measurement we want to act on.
- Category-level only (D1). Factor-level would require hand-curated
  check → factor mapping (~100 check names); the value ships now with
  zero curation cost. `high_strength_factors` already lists the
  factor IDs within each flagged category as the action pointer.
- Unmapped checks in the tracker log a warning but never crash — new
  checks land in `cases/*/checks/static.py` before FAILURE-FACTORS gets
  updated, and hard-failing would block diagnosis for everyone else.
- Failure rate denominator = `(mapped checks in category) × n_cases`,
  sourced from the FAILURE-FACTORS mapping (not inferred from observed
  failures). This keeps a category with no failures visible at 0%/0%
  rather than being silently dropped — important for "no gaps found"
  to mean actual success rather than missing data.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel, Field

from embedeval.failure_factors import (
    Category,
    load_check_category_map,
    load_factors,
)
from embedeval.test_tracker import TrackerData, load_tracker

logger = logging.getLogger(__name__)

DEFAULT_GAP_THRESHOLD_PP = 10.0


class CategoryDiagnosis(BaseModel):
    """Per-category coverage diagnosis comparing team vs. expert runs.

    Failure rates are the fraction of mapped-check occurrences that
    failed in each tracker, NOT a per-case pass rate. Two trackers that
    run the same case set with identical check definitions have the
    same denominator, so `gap` is interpretable as "extra principles
    the team pack failed to cover, in percentage points".
    """

    category: str  # "D"
    category_title: str  # "Memory Model & Concurrency"
    team_failed_checks: list[str] = Field(default_factory=list)
    expert_failed_checks: list[str] = Field(default_factory=list)
    team_failed_occurrences: int = 0
    expert_failed_occurrences: int = 0
    total_check_occurrences: int = 0
    team_failure_rate: float = 0.0
    expert_failure_rate: float = 0.0
    gap: float = 0.0  # team_rate - expert_rate; positive = team is worse
    needs_coverage: bool = False
    high_strength_factors: list[str] = Field(default_factory=list)
    factor_names: dict[str, str] = Field(default_factory=dict)


class CoverageDiagnosis(BaseModel):
    """Full coverage diagnosis payload for one model."""

    model: str
    gap_threshold: float  # stored as a fraction (0.10 for 10pp)
    per_category: list[CategoryDiagnosis] = Field(default_factory=list)
    unmapped_checks: list[str] = Field(default_factory=list)


def _failed_check_occurrences_by_category(
    tracker: TrackerData,
    model: str,
    check_to_category: dict[str, str],
) -> tuple[dict[str, int], dict[str, set[str]], set[str]]:
    """For one model in one tracker, return:

    - `failed_counts[category_letter]` — number of (case, failed_check)
      pairs that mapped to the category.
    - `failed_names[category_letter]` — set of unique check names that
      failed at least once in that category.
    - `unmapped` — check names present in the tracker's failed_checks
      that are not in `check_to_category`.
    """
    failed_counts: dict[str, int] = defaultdict(int)
    failed_names: dict[str, set[str]] = defaultdict(set)
    unmapped: set[str] = set()
    for cr in tracker.results.get(model, {}).values():
        for check in cr.failed_checks:
            cat = check_to_category.get(check)
            if cat is None:
                unmapped.add(check)
                continue
            failed_counts[cat] += 1
            failed_names[cat].add(check)
    return dict(failed_counts), {k: v for k, v in failed_names.items()}, unmapped


def _total_check_occurrences_by_category(
    n_cases: int,
    check_to_category: dict[str, str],
) -> dict[str, int]:
    """Denominator for the failure rate: `(mapped checks in category) × n_cases`.

    The source of truth for "how many checks exist in this category"
    is the `**EmbedEval checks mapped:**` lines in FAILURE-FACTORS.md
    (already parsed into `check_to_category`). Using that instead of
    inferring from observed failures avoids the circularity where a
    category whose checks all pass would have denominator 0 and be
    dropped from the output — making the tool blind to its own success
    stories.

    The `× n_cases` multiplier keeps the rate comparable across runs
    with different case counts: a category with 10 checks that each
    fire once per case gets 10 × n_cases evaluations.
    """
    if n_cases == 0:
        return {}
    checks_per_cat: dict[str, int] = defaultdict(int)
    for _, cat in check_to_category.items():
        checks_per_cat[cat] += 1
    return {cat: count * n_cases for cat, count in checks_per_cat.items()}


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def diagnose_coverage(
    team_dir: Path,
    expert_dir: Path,
    model: str | None = None,
    gap_threshold_pp: float = DEFAULT_GAP_THRESHOLD_PP,
) -> CoverageDiagnosis:
    """Load the team + expert trackers and produce a CoverageDiagnosis.

    `gap_threshold_pp` is in percentage points (default 10.0 → 0.10
    fraction). Categories where team_failure_rate − expert_failure_rate
    exceeds the threshold are flagged `needs_coverage=True`.
    """
    team_tracker = load_tracker(team_dir)
    expert_tracker = load_tracker(expert_dir)

    if not team_tracker.results:
        raise ValueError(f"No tracker results in team dir: {team_dir}")
    if not expert_tracker.results:
        raise ValueError(f"No tracker results in expert dir: {expert_dir}")

    chosen = _resolve_model(team_tracker, expert_tracker, model)

    # Warn on same-pack-hash collisions so users can't silently diagnose
    # a pack against itself (see context_compare._resolve_model for
    # precedent).
    if (
        team_tracker.context_pack_hash is not None
        and team_tracker.context_pack_hash == expert_tracker.context_pack_hash
    ):
        logger.warning(
            "Team and expert dirs share context_pack_hash=%s — "
            "diagnosis is meaningless.",
            team_tracker.context_pack_hash,
        )

    # Warn on case-count mismatch — diagnosis compares rates, so
    # denominators diverging means per-category failure rates aren't
    # strictly comparable. Reuse the message shape from context_compare.
    team_n = len(team_tracker.results.get(chosen, {}))
    expert_n = len(expert_tracker.results.get(chosen, {}))
    if team_n != expert_n:
        logger.warning(
            "Case count mismatch: team=%d cases, expert=%d cases. "
            "Per-category failure rates mix denominators.",
            team_n,
            expert_n,
        )

    check_to_category = load_check_category_map()
    categories = load_factors()
    cat_by_letter: dict[str, Category] = {c.letter: c for c in categories}

    # Guard against FAILURE-FACTORS.md drift: a `**EmbedEval checks
    # mapped:**` line might reference a category letter whose `## X.`
    # section header was deleted mid-edit. Fail fast with a clear
    # ValueError so the CLI's catch path gives an actionable message
    # instead of a bare traceback.
    unknown_letters = set(check_to_category.values()) - set(cat_by_letter)
    if unknown_letters:
        raise ValueError(
            f"Checks mapped to unknown category letters {sorted(unknown_letters)}; "
            "docs/LLM-EMBEDDED-FAILURE-FACTORS.md is likely mid-edit."
        )

    team_failed, team_names, team_unmapped = _failed_check_occurrences_by_category(
        team_tracker, chosen, check_to_category
    )
    expert_failed, expert_names, expert_unmapped = (
        _failed_check_occurrences_by_category(expert_tracker, chosen, check_to_category)
    )
    # Denominator: `mapped_checks_in_category × n_cases`. Use max(team_n,
    # expert_n) so a tracker missing some cases doesn't inflate the
    # other side's rate. The case-count-mismatch warning above already
    # flagged this as a risk — here we pick a defensible scalar so the
    # two rates stay comparable on the larger case set.
    totals = _total_check_occurrences_by_category(
        n_cases=max(team_n, expert_n),
        check_to_category=check_to_category,
    )

    threshold_frac = gap_threshold_pp / 100.0

    per_category: list[CategoryDiagnosis] = []
    for cat in categories:
        total = totals.get(cat.letter, 0)
        team_fail = team_failed.get(cat.letter, 0)
        expert_fail = expert_failed.get(cat.letter, 0)
        team_rate = _rate(team_fail, total)
        expert_rate = _rate(expert_fail, total)
        gap = team_rate - expert_rate
        high = [f for f in cat.factors if f.strength == "High"]
        per_category.append(
            CategoryDiagnosis(
                category=cat.letter,
                category_title=cat.title,
                team_failed_checks=sorted(team_names.get(cat.letter, set())),
                expert_failed_checks=sorted(expert_names.get(cat.letter, set())),
                team_failed_occurrences=team_fail,
                expert_failed_occurrences=expert_fail,
                total_check_occurrences=total,
                team_failure_rate=team_rate,
                expert_failure_rate=expert_rate,
                gap=gap,
                # Gap strictly greater than threshold — exactly-at-the-
                # threshold is considered within budget. This matches
                # the PLAN note asking for an explicit semantics choice.
                needs_coverage=gap > threshold_frac,
                high_strength_factors=[f.factor_id for f in high],
                factor_names={f.factor_id: f.name for f in high},
            )
        )

    # Sort by gap descending so the worst offender is first; ties
    # preserve alphabetical category order (Python sort is stable).
    per_category.sort(key=lambda c: c.gap, reverse=True)

    unmapped = sorted(team_unmapped | expert_unmapped)
    if unmapped:
        logger.warning(
            "Unmapped checks (%d) — these are in the tracker but not "
            "mapped in FAILURE-FACTORS.md: %s. Consider adding them to "
            "the relevant category's '**EmbedEval checks mapped:**' "
            "line so future diagnoses see them.",
            len(unmapped),
            ", ".join(unmapped),
        )

    # Suppress "category has no data" empty rows: categories where
    # total_check_occurrences is 0 have no signal. With the mapping-
    # derived denominator this can only happen when no checks at all
    # map to a letter — meaning the category section lost its
    # `**EmbedEval checks mapped:**` line.
    per_category = [c for c in per_category if c.total_check_occurrences > 0]

    return CoverageDiagnosis(
        model=chosen,
        gap_threshold=threshold_frac,
        per_category=per_category,
        unmapped_checks=unmapped,
    )


def _resolve_model(
    team_tracker: TrackerData,
    expert_tracker: TrackerData,
    requested: str | None,
) -> str:
    """Pick the model to diagnose. Mirror of harmful_inspect's logic:
    require the model to exist in both trackers; exclude mock when a
    real model is also present because mock is context-independent."""
    shared = set(team_tracker.results.keys()) & set(expert_tracker.results.keys())
    if not shared:
        raise ValueError(
            "No model is present in both team and expert trackers; "
            f"team={sorted(team_tracker.results)}, "
            f"expert={sorted(expert_tracker.results)}"
        )
    if requested:
        if requested not in shared:
            raise ValueError(
                f"Model {requested!r} not present in both trackers. "
                f"Shared: {sorted(shared)}"
            )
        return requested
    non_mock = sorted(m for m in shared if m != "mock")
    if len(non_mock) == 1:
        return non_mock[0]
    if not non_mock and "mock" in shared:
        return "mock"
    raise ValueError(
        f"Multiple models shared ({sorted(shared)}); pass --model to disambiguate."
    )


def format_diagnosis(diagnosis: CoverageDiagnosis) -> str:
    """Render a human-readable stdout table from a CoverageDiagnosis."""
    threshold_pp = diagnosis.gap_threshold * 100.0
    lines: list[str] = []
    lines.append(f"Context Coverage Diagnosis (model: {diagnosis.model})")
    lines.append("")
    lines.append(
        f"  Gap threshold: {threshold_pp:.0f}pp  "
        "(categories above this need CLAUDE.md improvement)"
    )
    lines.append("")

    if not diagnosis.per_category:
        lines.append(
            "  No categories with check data — trackers appear empty "
            "or the check suite didn't exercise any mapped factor."
        )
        lines.append("")
        return "\n".join(lines)

    header = (
        f"  {'Category':<42} {'Team':>5} {'Expert':>6}  "
        f"{'Gap':>6}   High factors to cover"
    )
    lines.append(header)
    divider = "  " + "-" * (len(header) - 2)
    lines.append(divider)

    flagged: list[CategoryDiagnosis] = []
    for cd in diagnosis.per_category:
        title = f"{cd.category}. {cd.category_title}"
        team = f"{cd.team_failure_rate * 100:.0f}%"
        expert = f"{cd.expert_failure_rate * 100:.0f}%"
        gap = _fmt_gap(cd.gap)
        factors = (
            ", ".join(cd.high_strength_factors)
            if cd.needs_coverage
            else "(within threshold)"
        )
        lines.append(f"  {title:<42} {team:>5} {expert:>6}  {gap:>6}   {factors}")
        if cd.needs_coverage:
            flagged.append(cd)

    if flagged:
        lines.append("")
        lines.append("  To improve coverage:")
        for cd in flagged:
            ids = ", ".join(cd.high_strength_factors)
            anchor = _github_anchor(f"{cd.category}. {cd.category_title}")
            lines.append(
                f"    {cd.category}. {cd.category_title} → "
                f"add principles for factors {ids}"
            )
            lines.append(f"       See docs/LLM-EMBEDDED-FAILURE-FACTORS.md#{anchor}")
    else:
        lines.append("")
        lines.append(
            "  No gaps found — team context matches the expert reference ceiling."
        )

    if diagnosis.unmapped_checks:
        lines.append("")
        lines.append(f"  Unmapped checks (warning): {len(diagnosis.unmapped_checks)}")
        preview = ", ".join(diagnosis.unmapped_checks[:5])
        if len(diagnosis.unmapped_checks) > 5:
            preview += f" (+{len(diagnosis.unmapped_checks) - 5} more)"
        lines.append(f"    {preview}")
        lines.append(
            "    Add them to the relevant category's "
            "'**EmbedEval checks mapped:**' line in "
            "docs/LLM-EMBEDDED-FAILURE-FACTORS.md."
        )

    return "\n".join(lines)


def _fmt_gap(v: float) -> str:
    pp = v * 100.0
    sign = "+" if pp >= 0 else ""
    return f"{sign}{pp:.0f}pp"


# GitHub Flavored Markdown slug rules (as implemented by github-slugger):
# lowercase; drop any char that isn't a letter/digit/underscore/space/
# hyphen (this strips `.`, `&`, `,`, `(`, `)`); convert each whitespace
# char to `-`. Crucially, consecutive `-`s are NOT collapsed — "A & B"
# slugs to "a--b" (double dash) because the `&` leaves two spaces
# behind. Matching this exactly keeps the CLI's "See docs/..." link
# clickable on the actual rendered doc.
_ANCHOR_DROP_RE = re.compile(r"[^\w\s-]")
_ANCHOR_WS_RE = re.compile(r"\s")


def _github_anchor(heading: str) -> str:
    slug = _ANCHOR_DROP_RE.sub("", heading.lower())
    return _ANCHOR_WS_RE.sub("-", slug)
