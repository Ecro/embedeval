"""EmbedEval CLI."""

import json
import logging
from pathlib import Path
from typing import Annotated, Optional

import typer

from embedeval.models import CaseCategory, DifficultyTier, Visibility

app = typer.Typer(help="EmbedEval: Embedded firmware LLM benchmark")

logger = logging.getLogger(__name__)


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
        typer.Option("--tier", help="Filter by tier: sanity, core, challenge (comma-separated)"),
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

    from embedeval.runner import Filters, run_benchmark
    from embedeval.scorer import score as score_results

    from embedeval.models import CaseTier

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

    typer.echo(
        f"Running benchmark: model={model}, cases={cases_dir}, scenario={scenario}"
    )

    if scenario == "bugfix":
        from embedeval.bugfix import run_bugfix_benchmark

        results = run_bugfix_benchmark(
            cases_dir=cases_dir,
            model=model,
            filters=filters,
            include_private=include_private,
        )
    else:
        results = run_benchmark(
            cases_dir=cases_dir,
            model=model,
            filters=filters,
            attempts=attempts,
            feedback_rounds=feedback_rounds,
            include_private=include_private,
        )

    if not results:
        typer.echo("No results generated.")
        raise typer.Exit(code=1)

    report = score_results(results)
    report.scenario = scenario
    report.temperature = temperature
    report.n_samples_per_case = attempts

    from embedeval.reporter import (
        generate_failure_report,
        generate_json,
        generate_leaderboard,
        generate_run_archive,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{model}-results.json"
    generate_json(report, json_path)

    leaderboard_path = output_dir / "LEADERBOARD.md"
    generate_leaderboard([report], leaderboard_path)

    run_dir = generate_run_archive(results, report, output_dir, model)
    generate_failure_report(results, run_dir / "report.md", model)

    typer.echo(f"Results: {json_path}")
    typer.echo(f"Leaderboard: {leaderboard_path}")
    typer.echo(f"Detailed: {run_dir}/")


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
        typer.echo(f"\nMost sensitive cases:")
        for cid in report.most_sensitive:
            case = next(c for c in report.cases if c.case_id == cid)
            typer.echo(f"  {cid}: robustness={case.robustness:.0%}")

    if report.most_robust:
        typer.echo(f"\nMost robust cases ({len(report.most_robust)}):")
        for cid in report.most_robust[:3]:
            typer.echo(f"  {cid}: robustness=100%")


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
