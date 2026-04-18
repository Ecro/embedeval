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
from pathlib import Path

from pydantic import BaseModel, computed_field

from embedeval.test_tracker import TrackerData, load_tracker

logger = logging.getLogger(__name__)


class CategoryComparison(BaseModel):
    """Per-category pass-rate comparison across context packs."""

    category: str
    n_cases: int
    bare_pass_rate: float | None = None
    team_pass_rate: float | None = None
    expert_pass_rate: float | None = None

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


class ContextComparison(BaseModel):
    """Full comparison report — runs + per-category + overall."""

    model: str
    runs: list[RunSummary]
    per_category: list[CategoryComparison]
    overall: CategoryComparison


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
        # Fall back to including mock so smoke tests can compare
        available = sorted(tracker.results.keys())
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


def compare_runs(
    bare_dir: Path,
    expert_dir: Path,
    team_dir: Path | None = None,
    model: str | None = None,
) -> ContextComparison:
    """Load trackers from each dir and compute per-category lift/gap."""
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
            )
        )

    runs = [
        _summarize_run("bare", bare_tracker, chosen),
        *([_summarize_run("team", team_tracker, chosen)] if team_tracker else []),
        _summarize_run("expert", expert_tracker, chosen),
    ]

    overall = _overall(per_category, bare_rates, team_rates, expert_rates)

    return ContextComparison(
        model=chosen,
        runs=runs,
        per_category=per_category,
        overall=overall,
    )


def _summarize_run(label: str, tracker: TrackerData, model: str) -> RunSummary:
    cases = tracker.results.get(model, {})
    n = len(cases)
    passed = sum(1 for c in cases.values() if c.passed)
    return RunSummary(
        label=label,
        pack_hash=tracker.context_pack_hash,
        model=model,
        n_cases=n,
        pass_rate=passed / n if n else 0.0,
    )


def _overall(
    per_category: list[CategoryComparison],
    bare_rates: dict[str, tuple[int, int]],
    team_rates: dict[str, tuple[int, int]],
    expert_rates: dict[str, tuple[int, int]],
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
    )


def format_comparison_table(report: ContextComparison) -> str:
    """Render a human-readable comparison table for stdout."""
    lines: list[str] = []
    lines.append(
        f"Context Quality Comparison (model: {report.model})"
    )
    lines.append("")
    for run in report.runs:
        hash_str = run.pack_hash or "<none>"
        lines.append(
            f"  {run.label:<6}  hash={hash_str:<16}  "
            f"n={run.n_cases:>3}  pass_rate={run.pass_rate:>6.1%}"
        )
    lines.append("")

    has_team = any(c.team_pass_rate is not None for c in report.per_category)
    if has_team:
        header = (
            f"  {'Category':<22} {'n':>4}  "
            f"{'Bare':>6} {'Team':>6} {'Expert':>6}  "
            f"{'Lift':>7} {'Gap':>7}"
        )
    else:
        header = (
            f"  {'Category':<22} {'n':>4}  "
            f"{'Bare':>6} {'Expert':>6}  {'Gap':>7}"
        )
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))

    for c in report.per_category:
        bare = _fmt_pct(c.bare_pass_rate)
        expert = _fmt_pct(c.expert_pass_rate)
        gap = _fmt_pp(c.gap)
        if has_team:
            team = _fmt_pct(c.team_pass_rate)
            lift = _fmt_pp(c.lift)
            lines.append(
                f"  {c.category:<22} {c.n_cases:>4}  "
                f"{bare:>6} {team:>6} {expert:>6}  {lift:>7} {gap:>7}"
            )
        else:
            lines.append(
                f"  {c.category:<22} {c.n_cases:>4}  "
                f"{bare:>6} {expert:>6}  {gap:>7}"
            )

    lines.append("  " + "-" * (len(header) - 2))
    o = report.overall
    if has_team:
        lines.append(
            f"  {'OVERALL':<22} {o.n_cases:>4}  "
            f"{_fmt_pct(o.bare_pass_rate):>6} {_fmt_pct(o.team_pass_rate):>6} "
            f"{_fmt_pct(o.expert_pass_rate):>6}  "
            f"{_fmt_pp(o.lift):>7} {_fmt_pp(o.gap):>7}"
        )
    else:
        lines.append(
            f"  {'OVERALL':<22} {o.n_cases:>4}  "
            f"{_fmt_pct(o.bare_pass_rate):>6} {_fmt_pct(o.expert_pass_rate):>6}  "
            f"{_fmt_pp(o.gap):>7}"
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
    return "\n".join(lines)


def _fmt_pct(v: float | None) -> str:
    return "—" if v is None else f"{v * 100:.0f}%"


def _fmt_pp(v: float | None) -> str:
    if v is None:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v * 100:.0f}pp"
