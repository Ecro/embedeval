"""EmbedEval CLI."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer

from embedeval.models import CaseCategory, DifficultyTier, Visibility

if TYPE_CHECKING:
    from embedeval.models import CaseMetadata, EvalResult
    from embedeval.test_tracker import TrackerData

app = typer.Typer(help="EmbedEval: Embedded firmware LLM benchmark")

logger = logging.getLogger(__name__)

# Matches LAYER_ORDER in reporter.py — kept here to synthesize per-layer
# result fields when rebuilding EvalResults from tracker entries.
_LAYER_NAMES: list[str] = [
    "static_analysis",
    "compile_gate",
    "runtime_execution",
    "static_heuristic",
    "test_quality_proof",
]


def _build_comprehensive_results(
    new_results: list["EvalResult"],
    tracker: "TrackerData",
    model: str,
    all_cases_meta: dict[str, "CaseMetadata"],
) -> list["EvalResult"]:
    """Merge the current run's EvalResults with prior tracker state.

    Leaderboard/run-archive consumers expect a *comprehensive* per-model
    snapshot, not just the cases that happened to be retested this run.
    For every case in the tracker that isn't in `new_results`, this
    synthesizes a minimal EvalResult from the stored pass/failed_layer
    plus CaseMetadata (category/tier/reasoning types). New results take
    priority when a case_id overlaps.

    Cases with orphaned tracker entries (no matching CaseMetadata,
    e.g. deleted TCs) are skipped to avoid polluting aggregates.
    """
    from embedeval.models import EvalResult, LayerResult, TokenUsage

    new_ids = {r.case_id for r in new_results}
    merged: list[EvalResult] = list(new_results)

    prior = tracker.results.get(model, {})
    for case_id, cr in prior.items():
        if case_id in new_ids:
            continue
        meta = all_cases_meta.get(case_id)
        if meta is None:
            continue

        failed_layer = cr.failed_at_layer
        layers: list[LayerResult] = []
        for idx, name in enumerate(_LAYER_NAMES):
            if cr.passed:
                layer_passed = True
                layer_error: str | None = None
            elif failed_layer is None:
                layer_passed = False
                layer_error = None
            elif idx < failed_layer:
                layer_passed = True
                layer_error = None
            elif idx == failed_layer:
                layer_passed = False
                layer_error = None
            else:
                # Layers after the failing one get the same "skipped
                # due to earlier failure" marker that the real evaluator
                # emits — scorer._count_quality_passes keys off this
                # marker to avoid penalising L3 when L1/L2 broke.
                layer_passed = False
                layer_error = f"Skipped: layer {failed_layer} failed"
            layers.append(
                LayerResult(
                    layer=idx,
                    name=name,
                    passed=layer_passed,
                    details=[],
                    duration_seconds=0.0,
                    error=layer_error,
                )
            )

        merged.append(
            EvalResult(
                case_id=case_id,
                category=meta.category,
                model=model,
                attempt=1,
                generated_code="",
                layers=layers,
                failed_at_layer=failed_layer,
                passed=cr.passed,
                total_score=1.0 if cr.passed else 0.0,
                duration_seconds=0.0,
                token_usage=TokenUsage(
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                ),
                cost_usd=0.0,
                tier=meta.tier,
                reasoning_types=meta.reasoning_types,
            )
        )

    return merged


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """EmbedEval benchmark tool."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    if ctx.invoked_subcommand is None:
        typer.echo("EmbedEval v0.1.0 — use --help for commands")


@app.command()
def run(
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", help="Path to cases directory"),
    ] = Path("cases"),
    model: Annotated[
        str,
        typer.Option("--model", "-m", help="LLM model to evaluate"),
    ] = "mock",
    category: Annotated[
        Optional[str],
        typer.Option("--category", "-c", help="Filter by category"),
    ] = None,
    difficulty: Annotated[
        Optional[str],
        typer.Option("--difficulty", "-d", help="Filter by difficulty"),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", "-o", help="Output directory for results"),
    ] = Path("results"),
    attempts: Annotated[
        int,
        typer.Option("--attempts", "-a", help="Number of attempts per case"),
    ] = 1,
    tier: Annotated[
        Optional[str],
        typer.Option(
            "--tier",
            help="Filter by tier: sanity, core, challenge (comma-separated)",
        ),
    ] = None,
    visibility: Annotated[
        str | None,
        typer.Option("--visibility", help="Filter by visibility (public/private)"),
    ] = None,
    after_date: Annotated[
        str | None,
        typer.Option(
            "--after-date",
            help="Only include cases created after this date (YYYY-MM-DD)",
        ),
    ] = None,
    feedback_rounds: Annotated[
        int,
        typer.Option(
            "--feedback-rounds", "-f", help="Compiler feedback rounds (0=disabled)"
        ),
    ] = 0,
    temperature: Annotated[
        float,
        typer.Option(
            "--temperature", "-t", help="LLM temperature (recorded in report metadata)"
        ),
    ] = 0.0,
    scenario: Annotated[
        str,
        typer.Option(
            "--scenario",
            "-s",
            help="Evaluation scenario: generation or bugfix",
        ),
    ] = "generation",
    include_private: Annotated[
        bool,
        typer.Option(
            "--include-private",
            help="Include private held-out cases (default: public only)",
        ),
    ] = False,
    private_cases: Annotated[
        Optional[Path],
        typer.Option(
            "--private-cases",
            help="Path to private cases directory (separate repo)",
        ),
    ] = None,
    retest_only: Annotated[
        bool,
        typer.Option(
            "--retest-only",
            help="Only run cases that changed since last test or were never tested",
        ),
    ] = False,
    run_id: Annotated[
        Optional[str],
        typer.Option(
            "--run-id",
            help=(
                "Distinct tag appended to the run archive directory "
                "(e.g. 'n1', 'n2') so multiple runs of the same model on "
                "the same day don't overwrite each other — required when "
                "collecting n>=2 samples for CI analysis"
            ),
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Run benchmark evaluation on cases."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    if scenario not in ("generation", "bugfix"):
        typer.echo(f"Unknown scenario: {scenario}. Use 'generation' or 'bugfix'.")
        raise typer.Exit(code=1)

    from embedeval.models import CaseTier
    from embedeval.runner import Filters, run_benchmark
    from embedeval.scorer import score as score_results

    filters = Filters()
    if category:
        filters.categories = [CaseCategory(category)]
    if difficulty:
        filters.difficulties = [DifficultyTier(difficulty)]
    if tier:
        filters.tiers = [CaseTier(t.strip()) for t in tier.split(",")]
    if visibility:
        filters.visibility = Visibility(visibility)
    if after_date:
        filters.after_date = after_date

    # Build case_dir_map covering all discoverable cases (public + private).
    # Needed so update_tracker and generate_results_doc can hash private
    # cases correctly — without it they'd resolve to non-existent paths
    # under cases_dir and record the empty-content hash.
    from embedeval.runner import discover_cases as _discover

    case_dir_map: dict[str, Path] = {
        meta.id: cd for cd, meta in _discover(cases_dir)
    }
    if private_cases:
        for cd, meta in _discover(private_cases):
            case_dir_map[meta.id] = cd

    # Retest-only filtering
    if retest_only:
        from embedeval.runner import filter_cases as _filter
        from embedeval.test_tracker import (
            find_cases_needing_retest,
            load_tracker,
        )

        tracker = load_tracker(output_dir)
        all_cases = _discover(cases_dir)
        if private_cases:
            all_cases.extend(_discover(private_cases))
        # Apply same visibility filter that run_benchmark will use,
        # so we don't count private cases that will be excluded later
        retest_filters = Filters(
            categories=filters.categories,
            difficulties=filters.difficulties,
            tiers=filters.tiers,
            tags=filters.tags,
            visibility=filters.visibility
            if filters.visibility is not None
            else (None if include_private else Visibility.PUBLIC),
            after_date=filters.after_date,
        )
        selected = _filter(all_cases, retest_filters)
        all_case_ids = [meta.id for _, meta in selected]
        needs_retest = find_cases_needing_retest(
            tracker,
            model,
            cases_dir,
            all_case_ids,
            case_dir_map=case_dir_map,
        )
        if not needs_retest:
            typer.echo("All cases up to date — nothing to retest.")
            raise typer.Exit(code=0)
        typer.echo(
            f"Retest: {len(needs_retest)}/{len(all_case_ids)} cases need retesting"
        )
        # Override filters to only include cases needing retest
        filters.case_ids = needs_retest

    typer.echo(
        f"Running benchmark: model={model}, cases={cases_dir}, scenario={scenario}"
    )

    # Build a checkpoint path so a crashed run can resume instead of
    # starting from scratch. Deleted on successful completion below.
    model_slug = model.replace("/", "_").replace(":", "_")
    ckpt_suffix = f"_{run_id}" if run_id else ""
    checkpoint_path = (
        output_dir / "runs" / f".checkpoint_{model_slug}{ckpt_suffix}.jsonl"
    )
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    if scenario == "bugfix":
        from embedeval.bugfix import run_bugfix_benchmark

        results = run_bugfix_benchmark(
            cases_dir=cases_dir,
            model=model,
            filters=filters,
            include_private=include_private,
        )
    else:
        extra_dirs = [private_cases] if private_cases else None
        results = run_benchmark(
            cases_dir=cases_dir,
            model=model,
            filters=filters,
            attempts=attempts,
            feedback_rounds=feedback_rounds,
            include_private=include_private,
            extra_cases_dirs=extra_dirs,
            checkpoint_path=checkpoint_path,
        )

    if not results:
        typer.echo("No results generated.")
        raise typer.Exit(code=1)

    # Merge with tracker history so the leaderboard/safe-guide reflect the
    # comprehensive per-model state, not just this run's (possibly partial)
    # slice. --retest-only runs would otherwise clobber LEADERBOARD.md
    # with the 3-case view.
    from embedeval.test_tracker import (
        generate_results_doc,
        load_tracker,
        save_tracker,
        update_tracker,
    )

    prior_tracker = load_tracker(output_dir)
    all_cases_meta = {meta.id: meta for _, meta in _discover(cases_dir)}
    if private_cases:
        for _, meta in _discover(private_cases):
            all_cases_meta[meta.id] = meta

    comprehensive_results = _build_comprehensive_results(
        results, prior_tracker, model, all_cases_meta
    )

    report = score_results(comprehensive_results)
    report.scenario = scenario
    report.temperature = temperature
    report.n_samples_per_case = attempts

    from embedeval.reporter import (
        generate_failure_report,
        generate_json,
        generate_leaderboard,
        generate_run_archive,
        generate_safe_guide,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{model}-results.json"
    generate_json(report, json_path)

    # Leaderboard needs every known model, not just the one that just ran,
    # otherwise a Sonnet-only invocation wipes Haiku off the page.
    leaderboard_reports = [report]
    for other_model in sorted(prior_tracker.results.keys()):
        if other_model == model or other_model == "mock":
            continue
        other_merged = _build_comprehensive_results(
            [], prior_tracker, other_model, all_cases_meta
        )
        if not other_merged:
            continue
        other_report = score_results(other_merged)
        other_report.scenario = scenario
        leaderboard_reports.append(other_report)

    leaderboard_path = output_dir / "LEADERBOARD.md"
    generate_leaderboard(leaderboard_reports, leaderboard_path)

    run_dir = generate_run_archive(
        comprehensive_results, report, output_dir, model, run_id=run_id
    )
    # Failure report still lists just this run's failures — the archive
    # has the full picture, but the one-page report is most useful as
    # "what broke in *this* invocation".
    generate_failure_report(results, run_dir / "report.md", model)

    # Update tracker after building comprehensive_results so the "prior"
    # snapshot used for merging reflects the state *before* this run.
    tracker = update_tracker(
        prior_tracker, results, cases_dir, model, case_dir_map=case_dir_map
    )
    save_tracker(tracker, output_dir)
    generate_results_doc(
        tracker,
        output_dir / "TEST_RESULTS.md",
        cases_dir,
        case_dir_map=case_dir_map,
    )

    # Generate safe guide from all available runs
    guide_path = generate_safe_guide(output_dir)

    # Clean checkpoint — run succeeded, all data is persisted.
    if checkpoint_path.is_file():
        checkpoint_path.unlink()
        logger.info("Checkpoint removed: %s", checkpoint_path)

    typer.echo(f"Results: {json_path}")
    typer.echo(f"Leaderboard: {leaderboard_path}")
    typer.echo(f"Detailed: {run_dir}/")
    typer.echo(f"Tracker: {output_dir / 'test_tracker.json'}")
    if guide_path:
        typer.echo(f"Safe guide: {guide_path}")


@app.command()
def validate(
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", help="Path to cases directory"),
    ] = Path("cases"),
    category: Annotated[
        Optional[str],
        typer.Option("--category", "-c", help="Filter by category"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Validate reference solutions for cases."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    from embedeval.runner import Filters, discover_cases, filter_cases

    cases = discover_cases(cases_dir)
    if category:
        cases = filter_cases(cases, Filters(categories=[CaseCategory(category)]))

    if not cases:
        typer.echo("No cases found.")
        raise typer.Exit(code=1)

    from embedeval.evaluator import evaluate

    passed_count = 0
    failed_count = 0

    for case_dir, meta in cases:
        ref_file = case_dir / "reference" / "main.c"
        if not ref_file.is_file():
            typer.echo(f"  SKIP {meta.id}: no reference solution")
            continue

        ref_code = ref_file.read_text(encoding="utf-8")
        result = evaluate(case_dir=case_dir, generated_code=ref_code, model="reference")

        if result.passed:
            typer.echo(f"  PASS {meta.id}")
            passed_count += 1
        else:
            typer.echo(f"  FAIL {meta.id} (layer {result.failed_at_layer})")
            failed_count += 1

    typer.echo(f"\nValidation: {passed_count} passed, {failed_count} failed")


@app.command(name="validate-metadata")
def validate_metadata(
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", help="Path to cases directory"),
    ] = Path("cases"),
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Validate metadata consistency across all cases."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    from embedeval.runner import discover_cases

    cases = discover_cases(cases_dir)
    if not cases:
        typer.echo("No cases found.")
        raise typer.Exit(code=1)

    warnings: list[str] = []
    for case_dir, meta in cases:
        board = meta.build_board or "native_sim"
        has_cmake = (case_dir / "CMakeLists.txt").is_file()

        # Warn: compilable board target but no CMakeLists.txt
        # and l1_skip not set — possibly misconfigured
        if not meta.l1_skip and not has_cmake and board == "native_sim":
            warnings.append(
                f"  WARN {meta.id}: no CMakeLists.txt and "
                f"l1_skip not set (non-compilable case?)"
            )

        # Warn: compilable case without l1_skip should have
        # reference solution
        if has_cmake and not meta.l1_skip:
            ref = case_dir / "reference" / "main.c"
            if not ref.is_file():
                warnings.append(
                    f"  WARN {meta.id}: compilable case "
                    f"(CMakeLists.txt) but no reference/main.c"
                )

    # Summary by category
    from collections import defaultdict

    by_cat: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "total": 0,
            "l1_skip": 0,
            "l2_skip": 0,
            "hw_board": 0,
        }
    )
    for _, meta in cases:
        cat = meta.category.value
        by_cat[cat]["total"] += 1
        if meta.l1_skip:
            by_cat[cat]["l1_skip"] += 1
        if meta.l2_skip:
            by_cat[cat]["l2_skip"] += 1
        board = meta.build_board or "native_sim"
        if board != "native_sim":
            by_cat[cat]["hw_board"] += 1

    typer.echo("Category Layer Applicability:\n")
    typer.echo(
        f"  {'Category':<20s} {'Total':>5s}  "
        f"{'L1 Skip':>7s} {'L2 Skip':>7s} {'HW Board':>8s}"
    )
    typer.echo(f"  {'─' * 20} {'─' * 5}  {'─' * 7} {'─' * 7} {'─' * 8}")
    for cat in sorted(by_cat):
        c = by_cat[cat]
        typer.echo(
            f"  {cat:<20s} {c['total']:>5d}  "
            f"{c['l1_skip']:>7d} {c['l2_skip']:>7d} "
            f"{c['hw_board']:>8d}"
        )

    if warnings:
        typer.echo(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            typer.echo(w)
    else:
        typer.echo("\nNo metadata warnings.")

    typer.echo(
        f"\nTotal: {len(cases)} cases, "
        f"{sum(c['l1_skip'] for c in by_cat.values())} l1_skip, "
        f"{sum(c['l2_skip'] for c in by_cat.values())} l2_skip"
    )


@app.command()
def report(
    results_dir: Annotated[
        Path,
        typer.Option("--results", help="Directory containing result JSON files"),
    ] = Path("results"),
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output leaderboard path"),
    ] = Path("LEADERBOARD.md"),
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Generate leaderboard from existing results."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    from embedeval.models import BenchmarkReport
    from embedeval.reporter import generate_leaderboard

    json_files = sorted(results_dir.glob("*.json"))
    if not json_files:
        typer.echo(f"No JSON results found in {results_dir}")
        raise typer.Exit(code=1)

    reports: list[BenchmarkReport] = []
    for jf in json_files:
        data = json.loads(jf.read_text(encoding="utf-8"))
        reports.append(BenchmarkReport(**data))

    generate_leaderboard(reports, output)
    typer.echo(f"Leaderboard written to {output}")


@app.command(name="categories")
def list_categories(
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", help="Path to cases directory"),
    ] = Path("cases"),
) -> None:
    """List available categories with case counts."""
    from collections import Counter

    from embedeval.runner import discover_cases

    cases = discover_cases(cases_dir)
    if not cases:
        typer.echo("No cases found.")
        raise typer.Exit(code=0)

    cat_counts: Counter[str] = Counter()
    diff_counts: dict[str, Counter[str]] = {}
    for _, meta in cases:
        cat = meta.category.value
        cat_counts[cat] += 1
        diff_counts.setdefault(cat, Counter())[meta.difficulty.value] += 1

    typer.echo(f"{len(cat_counts)} categories, {len(cases)} total cases:\n")
    typer.echo(
        f"  {'Category':<20s} {'Cases':>5s}  {'Easy':>4s} {'Med':>4s} {'Hard':>4s}"
    )
    typer.echo(f"  {'─' * 20} {'─' * 5}  {'─' * 4} {'─' * 4} {'─' * 4}")
    for cat in sorted(cat_counts):
        dc = diff_counts[cat]
        typer.echo(
            f"  {cat:<20s} {cat_counts[cat]:>5d}"
            f"  {dc.get('easy', 0):>4d} {dc.get('medium', 0):>4d}"
            f"  {dc.get('hard', 0):>4d}"
        )


@app.command()
def agent(
    model: Annotated[
        str,
        typer.Argument(help="LLM model identifier"),
    ],
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", "-d", help="Path to cases directory"),
    ] = Path("cases"),
    max_turns: Annotated[
        int,
        typer.Option("--max-turns", "-t", help="Maximum agent turns per case"),
    ] = 5,
    category: Annotated[
        Optional[list[str]],
        typer.Option("--category", "-c", help="Filter by category (repeatable)"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Run benchmark in multi-turn agent mode with error feedback."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    from embedeval.agent import evaluate_agent
    from embedeval.runner import Filters, discover_cases, filter_cases

    cases = discover_cases(cases_dir)
    filters = Filters()
    if category:
        filters.categories = [CaseCategory(c) for c in category]
    cases = filter_cases(cases, filters)

    if not cases:
        typer.echo("No cases found.")
        raise typer.Exit(code=1)

    typer.echo(
        f"Agent mode: model={model}, max_turns={max_turns}, cases={len(cases)}\n"
    )

    from embedeval.runner import _load_prompt

    passed = 0
    failed = 0
    for case_dir, meta in cases:
        prompt = _load_prompt(case_dir)
        result = evaluate_agent(
            case_dir=case_dir,
            model=model,
            prompt=prompt,
            max_turns=max_turns,
        )
        status = "PASS" if result.passed else "FAIL"
        turns_info = f"turn {result.turns_used}/{result.max_turns}"
        typer.echo(f"  [{status}] {meta.id:30s} ({turns_info})")
        if result.passed:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    pass_rate = passed / total if total > 0 else 0.0
    typer.echo(f"\nAgent results: {passed}/{total} passed ({pass_rate:.1%})")


@app.command()
def guide(
    results_dir: Annotated[
        Path,
        typer.Option("--results", help="Directory containing result JSON files"),
    ] = Path("results"),
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output Safety Guide path"),
    ] = Path("SAFETY-GUIDE.md"),
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Generate LLM Embedded Code Safety Guide from benchmark results."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    import json

    from embedeval.models import EvalResult
    from embedeval.safety_guide import generate_safety_guide

    # Load results from run archive detail files
    all_results: list[EvalResult] = []
    for run_dir in sorted(results_dir.glob("runs/*")):
        details_dir = run_dir / "details"
        if not details_dir.is_dir():
            continue
        for detail_file in sorted(details_dir.glob("*.json")):
            try:
                data = json.loads(detail_file.read_text(encoding="utf-8"))
                all_results.append(EvalResult(**data))
            except Exception:
                continue

    if not all_results:
        typer.echo("No benchmark results found. Run a benchmark first.")
        raise typer.Exit(code=1)

    generate_safety_guide(all_results, output)
    typer.echo(f"Safety Guide written to {output}")


@app.command()
def sensitivity(
    model: Annotated[
        str,
        typer.Argument(help="LLM model identifier"),
    ],
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", help="Path to cases directory"),
    ] = Path("cases"),
    sample: Annotated[
        int,
        typer.Option("--sample", "-s", help="Number of cases to sample (0=all)"),
    ] = 30,
    variants: Annotated[
        int,
        typer.Option("--variants", "-n", help="Number of prompt variants per case"),
    ] = 3,
    seed: Annotated[
        int,
        typer.Option("--seed", help="Random seed for reproducible sampling"),
    ] = 42,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Run prompt sensitivity analysis to measure benchmark robustness."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    from embedeval.sensitivity import run_sensitivity_analysis

    typer.echo(
        f"Sensitivity analysis: model={model}, sample={sample}, "
        f"variants={variants}, seed={seed}"
    )
    report = run_sensitivity_analysis(
        cases_dir=cases_dir,
        model=model,
        sample_size=sample,
        variants_per_case=variants,
        seed=seed,
    )

    typer.echo(f"\nAvg robustness: {report.avg_robustness:.1%}")
    typer.echo(f"Cases analyzed: {report.total_cases}")

    if report.most_sensitive:
        typer.echo("\nMost sensitive cases:")
        for cid in report.most_sensitive:
            case = next(c for c in report.cases if c.case_id == cid)
            typer.echo(f"  {cid}: robustness={case.robustness:.0%}")

    if report.most_robust:
        typer.echo(f"\nMost robust cases ({len(report.most_robust)}):")
        for cid in report.most_robust[:3]:
            typer.echo(f"  {cid}: robustness=100%")


@app.command(name="refresh-tracker")
def refresh_tracker(
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", help="Path to cases directory"),
    ] = Path("cases"),
    results_dir: Annotated[
        Path,
        typer.Option("--results", help="Results directory with tracker"),
    ] = Path("results"),
) -> None:
    """Refresh test tracker after TC changes (used by /wrapup)."""
    from embedeval.test_tracker import (
        detect_changed_cases_from_git,
        generate_results_doc,
        load_tracker,
        mark_cases_changed,
        save_tracker,
    )

    tracker = load_tracker(results_dir)
    if not tracker.results:
        typer.echo("No test results tracked yet.")
        raise typer.Exit(code=0)

    changed = detect_changed_cases_from_git(cases_dir)
    if not changed:
        typer.echo("No cases changed in last commit.")
    else:
        n = mark_cases_changed(tracker, changed, cases_dir)
        save_tracker(tracker, results_dir)
        typer.echo(f"Marked {n} case/model pairs for retest: {', '.join(changed)}")

    generate_results_doc(tracker, results_dir / "TEST_RESULTS.md", cases_dir)
    typer.echo("TEST_RESULTS.md refreshed.")


@app.command(name="list")
def list_cases(
    cases_dir: Annotated[
        Path,
        typer.Option("--cases", help="Path to cases directory"),
    ] = Path("cases"),
    category: Annotated[
        Optional[str],
        typer.Option("--category", "-c", help="Filter by category"),
    ] = None,
    difficulty: Annotated[
        Optional[str],
        typer.Option("--difficulty", "-d", help="Filter by difficulty"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """List available benchmark cases."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    from embedeval.runner import Filters, discover_cases, filter_cases

    cases = discover_cases(cases_dir)
    filters = Filters()
    if category:
        filters.categories = [CaseCategory(category)]
    if difficulty:
        filters.difficulties = [DifficultyTier(difficulty)]

    cases = filter_cases(cases, filters)

    if not cases:
        typer.echo("No cases found.")
        raise typer.Exit(code=0)

    typer.echo(f"Found {len(cases)} cases:\n")
    for _case_dir, meta in cases:
        typer.echo(
            f"  [{meta.difficulty.value:6s}] {meta.id:20s} "
            f"{meta.category.value:15s} — {meta.title}"
        )
