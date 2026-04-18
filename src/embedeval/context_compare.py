"""Context Quality Mode comparison reporter.

Compares benchmark runs done with different context packs and computes
per-category Context Lift (team − bare) and Context Gap (expert − team).
See docs/CONTEXT-QUALITY-MODE.md for interpretation.

Inputs are output_dir paths from prior `embedeval run` invocations. Each
must contain a test_tracker.json. The tracker's context_pack_hash field
identifies which pack the run used; comparison enforces that the bare/
team/expert dirs hold runs with distinct hashes (or no hash for bare),
preventing meaningless comparisons.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from embedeval.test_tracker import TrackerData, load_tracker

logger = logging.getLogger(__name__)


class CaseEffect(str, Enum):
    """How a context pack changed a single case's pass/fail status.

    Truth table (bare vs packed):
        F → T   HELPFUL         pack unblocked the case
        T → F   HARMFUL         pack broke the case (inspect for brittleness)
        F → F   NO_EFFECT_FAIL  both fail (likely LLM hard-limit)
        T → T   NO_EFFECT_PASS  both pass (no headroom to show effect)
    """

    HELPFUL = "helpful"
    HARMFUL = "harmful"
    NO_EFFECT_FAIL = "no-effect-fail"
    NO_EFFECT_PASS = "no-effect-pass"


def classify_effect(bare_passed: bool, packed_passed: bool) -> CaseEffect:
    """Classify the per-case effect of a pack against a bare baseline.

    n>1 attempts limitation: the tracker stores only the most recent
    attempt's pass status (see test_tracker.CaseResult.passed). When
    multi-attempt runs are compared, the effect reflects last-attempt
    behavior only. `RunSummary.max_attempts` surfaces this; for
    statistical robustness across attempts, pre-aggregate with
    scripts/aggregate_n_runs.py before calling context-compare.
    """
    if not bare_passed and packed_passed:
        return CaseEffect.HELPFUL
    if bare_passed and not packed_passed:
        return CaseEffect.HARMFUL
    if not bare_passed:
        return CaseEffect.NO_EFFECT_FAIL
    return CaseEffect.NO_EFFECT_PASS


class PerCaseComparison(BaseModel):
    """Per-case pass/fail across packs plus effect classification.

    `bare_to_expert_effect` is the dominant question ("did the pack
    help?"). `bare_to_team_effect` is only populated when compare_runs
    was called with include_team_effect=True and a team tracker exists.
    Either effect may be None when one side lacks the case (mixed case
    sets) or the input was not provided.

    `*_attempts` surface how many attempts populated the tracker for
    that case; n>1 means the `*_passed` value is last-attempt only.
    """

    case_id: str
    category: str
    bare_passed: bool | None = None
    team_passed: bool | None = None
    expert_passed: bool | None = None
    bare_attempts: int | None = None
    team_attempts: int | None = None
    expert_attempts: int | None = None
    bare_to_expert_effect: CaseEffect | None = None
    bare_to_team_effect: CaseEffect | None = None


class CategoryComparison(BaseModel):
    """Per-category pass-rate comparison across context packs."""

    category: str
    n_cases: int
    bare_pass_rate: float | None = None
    team_pass_rate: float | None = None
    expert_pass_rate: float | None = None
    # Counts of per-case effects, bare→expert dimension. Keys are
    # CaseEffect values ("helpful", "harmful", "no-effect-fail",
    # "no-effect-pass"). Sum may be less than n_cases when cases are
    # missing from one side (mixed case sets). Eagerly populated by
    # compare_runs — CategoryComparison doesn't hold per-case data so
    # @computed_field isn't viable here.
    effect_counts: dict[str, int] = Field(default_factory=dict)

    # @computed_field, not @property — Pydantic v2 only serializes
    # computed_field-decorated properties in model_dump_json(). Plain
    # @property would be invisible to JSON consumers, breaking the
    # primary CI integration use case.
    @computed_field  # type: ignore[prop-decorator]
    @property
    def lift(self) -> float | None:
        """team − bare. None if either is missing."""
        if self.bare_pass_rate is None or self.team_pass_rate is None:
            return None
        return self.team_pass_rate - self.bare_pass_rate

    @computed_field  # type: ignore[prop-decorator]
    @property
    def gap(self) -> float | None:
        """expert − team (or expert − bare if no team)."""
        if self.expert_pass_rate is None:
            return None
        anchor = self.team_pass_rate
        if anchor is None:
            anchor = self.bare_pass_rate
        if anchor is None:
            return None
        return self.expert_pass_rate - anchor


class RunSummary(BaseModel):
    """Top-line summary of one tracker for one model."""

    label: str  # "bare" / "team" / "expert"
    pack_hash: str | None
    model: str
    n_cases: int
    pass_rate: float
    # Maximum attempts seen across cases in this tracker, reflecting
    # the freshest update_tracker call per case (NOT a cumulative total
    # across repeat runs — see CaseResult.attempts). 1 means a single-
    # attempt run; >1 signals per-case `passed` values are last-attempt
    # only.
    max_attempts: int = 1


class ContextComparison(BaseModel):
    """Full comparison report — runs + per-category + overall."""

    model: str
    runs: list[RunSummary]
    per_category: list[CategoryComparison]
    overall: CategoryComparison
    # Every case with data in at least one tracker. Used by JSON
    # consumers (CI regression bots) to inspect which specific cases
    # flipped helpful/harmful when a pack was edited.
    per_case: list[PerCaseComparison] = Field(default_factory=list)


def _category_of(case_id: str) -> str:
    """Extract category from case_id (e.g. 'isr-001' -> 'isr')."""
    parts = case_id.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return case_id


def _per_category_pass_rates(
    tracker: TrackerData,
    model: str,
) -> dict[str, tuple[int, int]]:
    """Return {category: (passed, total)} for one model in one tracker."""
    cases = tracker.results.get(model, {})
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for case_id, cr in cases.items():
        cat = _category_of(case_id)
        counts[cat][1] += 1
        if cr.passed:
            counts[cat][0] += 1
    return {cat: (passed, total) for cat, (passed, total) in counts.items()}


def _resolve_model(tracker: TrackerData, requested: str | None) -> str:
    """Pick the model to compare. If requested, validate. Else, pick the
    only one in the tracker; error if ambiguous."""
    available = sorted(m for m in tracker.results.keys() if m != "mock")
    if not available:
        # Fall back to including mock so smoke tests can compare. But mock
        # is context-independent (returns the same code regardless of the
        # pack), so any lift/gap will be ~0 and indistinguishable from a
        # real zero-lift result. Surface that explicitly.
        available = sorted(tracker.results.keys())
        if "mock" in available:
            logger.warning(
                "Only mock model found in tracker; mock ignores context "
                "packs, so lift and gap values will be meaningless."
            )
    if requested:
        if requested not in tracker.results:
            raise ValueError(
                f"Model {requested!r} not found in tracker. "
                f"Available: {available}"
            )
        return requested
    if len(available) == 1:
        return available[0]
    raise ValueError(
        f"Multiple models in tracker ({available}); pass --model to disambiguate."
    )


def _build_per_case(
    bare_tracker: TrackerData,
    expert_tracker: TrackerData,
    team_tracker: TrackerData | None,
    model: str,
    include_team_effect: bool,
) -> list[PerCaseComparison]:
    """Assemble a PerCaseComparison for the union of case ids across trackers.

    `include_team_effect` is opt-in (D1): when False, `bare_to_team_effect`
    is left None even if team data is present. bare→expert is always the
    default answer to "did the pack help?"; team→bare duplicates that
    dimension only when the caller explicitly asks.
    """
    bare = bare_tracker.results.get(model, {})
    expert = expert_tracker.results.get(model, {})
    team = team_tracker.results.get(model, {}) if team_tracker else {}
    all_ids = sorted(set(bare) | set(expert) | set(team))
    out: list[PerCaseComparison] = []
    for cid in all_ids:
        b = bare.get(cid)
        e = expert.get(cid)
        t = team.get(cid)
        b_pass = b.passed if b else None
        e_pass = e.passed if e else None
        t_pass = t.passed if t else None
        be_eff = (
            classify_effect(b_pass, e_pass)
            if b_pass is not None and e_pass is not None
            else None
        )
        bt_eff: CaseEffect | None = None
        if include_team_effect and b_pass is not None and t_pass is not None:
            bt_eff = classify_effect(b_pass, t_pass)
        out.append(
            PerCaseComparison(
                case_id=cid,
                category=_category_of(cid),
                bare_passed=b_pass,
                team_passed=t_pass,
                expert_passed=e_pass,
                bare_attempts=b.attempts if b else None,
                team_attempts=t.attempts if t else None,
                expert_attempts=e.attempts if e else None,
                bare_to_expert_effect=be_eff,
                bare_to_team_effect=bt_eff,
            )
        )
    return out


def _aggregate_effect_counts(
    per_case: list[PerCaseComparison],
    category: str | None = None,
) -> dict[str, int]:
    """Count bare→expert effects over per_case, optionally filtered by category.

    Keys are all four CaseEffect string values so consumers don't need
    to handle missing keys. Cases with effect=None (mixed case sets)
    are excluded — the sum may therefore be less than the category's
    n_cases.
    """
    counts: dict[str, int] = {e.value: 0 for e in CaseEffect}
    for pc in per_case:
        if category is not None and pc.category != category:
            continue
        eff = pc.bare_to_expert_effect
        if eff is not None:
            counts[eff.value] += 1
    return counts


def compare_runs(
    bare_dir: Path,
    expert_dir: Path,
    team_dir: Path | None = None,
    model: str | None = None,
    include_team_effect: bool = False,
) -> ContextComparison:
    """Load trackers from each dir and compute per-category lift/gap.

    Args:
        include_team_effect: When True, classify each case's bare→team
            effect (opt-in; D1). Requires `team_dir`. Default False
            keeps per-case output focused on the dominant bare→expert
            question.
    """
    if include_team_effect and team_dir is None:
        # Silent no-op here would mislead programmatic callers: the
        # CLI rejects the same combination (cli.py), so enforce the
        # guard at the API layer too for notebooks/CI scripts.
        raise ValueError(
            "include_team_effect=True requires team_dir to be provided"
        )
    bare_tracker = load_tracker(bare_dir)
    expert_tracker = load_tracker(expert_dir)
    team_tracker = load_tracker(team_dir) if team_dir else None

    if not bare_tracker.results:
        raise ValueError(f"No tracker results in bare dir: {bare_dir}")
    if not expert_tracker.results:
        raise ValueError(f"No tracker results in expert dir: {expert_dir}")

    chosen = _resolve_model(bare_tracker, model)

    # Sanity: distinct pack hashes (bare may be None; expert must not equal bare)
    if bare_tracker.context_pack_hash is not None and (
        bare_tracker.context_pack_hash == expert_tracker.context_pack_hash
    ):
        logger.warning(
            "Bare and expert dirs share context_pack_hash=%s — "
            "comparison is meaningless.",
            bare_tracker.context_pack_hash,
        )
    if team_tracker is not None and (
        team_tracker.context_pack_hash == bare_tracker.context_pack_hash
        or team_tracker.context_pack_hash == expert_tracker.context_pack_hash
    ):
        logger.warning(
            "Team dir shares pack hash with bare or expert — "
            "comparison may be meaningless."
        )

    bare_rates = _per_category_pass_rates(bare_tracker, chosen)
    expert_rates = _per_category_pass_rates(expert_tracker, chosen)
    team_rates = (
        _per_category_pass_rates(team_tracker, chosen) if team_tracker else {}
    )

    # Warn (don't fail) if the runs covered different case sets — the OVERALL
    # micro-average then mixes denominators silently. Acceptable when the
    # user knows (e.g. piloting expert on a subset); bad when the user
    # forgot to run the same filter on every dir.
    bare_n = sum(n for _, n in bare_rates.values())
    expert_n = sum(n for _, n in expert_rates.values())
    if bare_n != expert_n:
        logger.warning(
            "Case count mismatch: bare=%d cases, expert=%d cases. "
            "OVERALL lift/gap is computed over different case sets.",
            bare_n, expert_n,
        )
    if team_rates:
        team_n = sum(n for _, n in team_rates.values())
        if team_n != bare_n:
            logger.warning(
                "Case count mismatch: bare=%d cases, team=%d cases.",
                bare_n, team_n,
            )

    all_categories = sorted(
        set(bare_rates) | set(expert_rates) | set(team_rates)
    )

    per_case = _build_per_case(
        bare_tracker,
        expert_tracker,
        team_tracker,
        chosen,
        include_team_effect=include_team_effect,
    )

    per_category: list[CategoryComparison] = []
    for cat in all_categories:
        bare = bare_rates.get(cat)
        expert = expert_rates.get(cat)
        team = team_rates.get(cat)
        n_cases = max(
            (bare or (0, 0))[1],
            (expert or (0, 0))[1],
            (team or (0, 0))[1],
        )
        per_category.append(
            CategoryComparison(
                category=cat,
                n_cases=n_cases,
                bare_pass_rate=bare[0] / bare[1] if bare and bare[1] > 0 else None,
                team_pass_rate=team[0] / team[1] if team and team[1] > 0 else None,
                expert_pass_rate=(
                    expert[0] / expert[1] if expert and expert[1] > 0 else None
                ),
                effect_counts=_aggregate_effect_counts(per_case, category=cat),
            )
        )

    runs = [
        _summarize_run("bare", bare_tracker, chosen),
        *([_summarize_run("team", team_tracker, chosen)] if team_tracker else []),
        _summarize_run("expert", expert_tracker, chosen),
    ]

    overall = _overall(
        per_category,
        bare_rates,
        team_rates,
        expert_rates,
        effect_counts=_aggregate_effect_counts(per_case),
    )

    return ContextComparison(
        model=chosen,
        runs=runs,
        per_category=per_category,
        overall=overall,
        per_case=per_case,
    )


def _summarize_run(label: str, tracker: TrackerData, model: str) -> RunSummary:
    cases = tracker.results.get(model, {})
    n = len(cases)
    passed = sum(1 for c in cases.values() if c.passed)
    max_attempts = max((c.attempts for c in cases.values()), default=1)
    return RunSummary(
        label=label,
        pack_hash=tracker.context_pack_hash,
        model=model,
        n_cases=n,
        pass_rate=passed / n if n else 0.0,
        max_attempts=max_attempts,
    )


def _overall(
    per_category: list[CategoryComparison],
    bare_rates: dict[str, tuple[int, int]],
    team_rates: dict[str, tuple[int, int]],
    expert_rates: dict[str, tuple[int, int]],
    effect_counts: dict[str, int] | None = None,
) -> CategoryComparison:
    """Aggregate via micro-average (per-case), not macro (per-category).
    Micro-averaging matches how the leaderboard reports overall pass rate."""

    def _micro(rates: dict[str, tuple[int, int]]) -> float | None:
        if not rates:
            return None
        total_passed = sum(p for p, _ in rates.values())
        total_cases = sum(n for _, n in rates.values())
        return total_passed / total_cases if total_cases else None

    n_total = sum(c.n_cases for c in per_category)
    return CategoryComparison(
        category="OVERALL",
        n_cases=n_total,
        bare_pass_rate=_micro(bare_rates),
        team_pass_rate=_micro(team_rates) if team_rates else None,
        expert_pass_rate=_micro(expert_rates),
        effect_counts=effect_counts or {},
    )


def _fmt_effects(counts: dict[str, int]) -> str:
    """Render bare→expert effect counts as '2H/1Hm/3F/4P'.

    Order fixed: Helpful / Harmful / no-effect-Fail / no-effect-Pass.
    Zeroes are kept (not elided) so columns stay width-stable across
    rows — scanning a table of effect cells requires alignment more
    than it requires compactness.
    """
    h = counts.get(CaseEffect.HELPFUL.value, 0)
    hm = counts.get(CaseEffect.HARMFUL.value, 0)
    f = counts.get(CaseEffect.NO_EFFECT_FAIL.value, 0)
    p = counts.get(CaseEffect.NO_EFFECT_PASS.value, 0)
    return f"{h}H/{hm}Hm/{f}F/{p}P"


def format_comparison_table(report: ContextComparison) -> str:
    """Render a human-readable comparison table for stdout."""
    lines: list[str] = []
    lines.append(
        f"Context Quality Comparison (model: {report.model})"
    )
    lines.append("")
    for run in report.runs:
        hash_str = run.pack_hash or "<none>"
        attempts_str = (
            f"  attempts_max={run.max_attempts}" if run.max_attempts > 1 else ""
        )
        lines.append(
            f"  {run.label:<6}  hash={hash_str:<16}  "
            f"n={run.n_cases:>3}  pass_rate={run.pass_rate:>6.1%}"
            f"{attempts_str}"
        )
    lines.append("")

    # Surface n>1 once (D3): per-case effect is last-attempt only, and
    # users comparing multi-attempt runs need to know before trusting
    # the helpful/harmful counts.
    any_multi = any(r.max_attempts > 1 for r in report.runs)
    if any_multi:
        lines.append(
            "  Note: n>1 attempts detected — per-case effect is "
            "computed on last-attempt pass status only."
        )
        lines.append(
            "  Use scripts/aggregate_n_runs.py for statistical "
            "robustness across attempts."
        )
        lines.append("")

    has_team = any(c.team_pass_rate is not None for c in report.per_category)
    effect_col = "Effect (H/Hm/F/P)"
    # Width 20 accommodates the worst-case 3-digit-per-bucket render
    # ("100H/100Hm/100F/100P" = 20 chars). The header label is 17 chars
    # and right-aligns into the 20-char slot, keeping headers + data
    # columns in sync even when a single bucket exceeds 99 cases.
    effect_width = 20
    if has_team:
        header = (
            f"  {'Category':<22} {'n':>4}  "
            f"{'Bare':>6} {'Team':>6} {'Expert':>6}  "
            f"{'Lift':>7} {'Gap':>7}  "
            f"{effect_col:>{effect_width}}"
        )
    else:
        header = (
            f"  {'Category':<22} {'n':>4}  "
            f"{'Bare':>6} {'Expert':>6}  {'Gap':>7}  "
            f"{effect_col:>{effect_width}}"
        )
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))

    for c in report.per_category:
        bare = _fmt_pct(c.bare_pass_rate)
        expert = _fmt_pct(c.expert_pass_rate)
        gap = _fmt_pp(c.gap)
        effects = _fmt_effects(c.effect_counts)
        if has_team:
            team = _fmt_pct(c.team_pass_rate)
            lift = _fmt_pp(c.lift)
            lines.append(
                f"  {c.category:<22} {c.n_cases:>4}  "
                f"{bare:>6} {team:>6} {expert:>6}  {lift:>7} {gap:>7}  "
                f"{effects:>{effect_width}}"
            )
        else:
            lines.append(
                f"  {c.category:<22} {c.n_cases:>4}  "
                f"{bare:>6} {expert:>6}  {gap:>7}  "
                f"{effects:>{effect_width}}"
            )

    lines.append("  " + "-" * (len(header) - 2))
    o = report.overall
    o_effects = _fmt_effects(o.effect_counts)
    if has_team:
        lines.append(
            f"  {'OVERALL':<22} {o.n_cases:>4}  "
            f"{_fmt_pct(o.bare_pass_rate):>6} {_fmt_pct(o.team_pass_rate):>6} "
            f"{_fmt_pct(o.expert_pass_rate):>6}  "
            f"{_fmt_pp(o.lift):>7} {_fmt_pp(o.gap):>7}  "
            f"{o_effects:>{effect_width}}"
        )
    else:
        lines.append(
            f"  {'OVERALL':<22} {o.n_cases:>4}  "
            f"{_fmt_pct(o.bare_pass_rate):>6} {_fmt_pct(o.expert_pass_rate):>6}  "
            f"{_fmt_pp(o.gap):>7}  "
            f"{o_effects:>{effect_width}}"
        )

    lines.append("")
    lines.append(
        "  Lift = team − bare  (effect of team's context pack)"
    )
    lines.append(
        "  Gap  = expert − team  (room to improve toward expert pack)"
    )
    lines.append(
        "  Gap < 5pp on a category → likely an LLM hard-limit, "
        "not a context problem."
    )
    lines.append(
        "  Effect (bare → expert): H=helpful (F→T), Hm=harmful (T→F), "
        "F=both fail, P=both pass."
    )
    lines.append(
        "  Hm cases: always inspect generated code — may be real "
        "trade-off or EmbedEval check brittleness."
    )
    return "\n".join(lines)


def _fmt_pct(v: float | None) -> str:
    return "—" if v is None else f"{v * 100:.0f}%"


def _fmt_pp(v: float | None) -> str:
    if v is None:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v * 100:.0f}pp"
