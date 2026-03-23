"""EmbedEval CLI."""

import json
import logging
from pathlib import Path
from typing import Annotated, Optional

import typer

from embedeval.models import CaseCategory, DifficultyTier

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
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging"),
    ] = False,
) -> None:
    """Run benchmark evaluation on cases."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)

    from embedeval.runner import Filters, run_benchmark
    from embedeval.scorer import score as score_results

    filters = Filters()
    if category:
        filters.categories = [CaseCategory(category)]
    if difficulty:
        filters.difficulties = [DifficultyTier(difficulty)]

    typer.echo(f"Running benchmark: model={model}, cases={cases_dir}")
    results = run_benchmark(
        cases_dir=cases_dir,
        model=model,
        filters=filters,
        attempts=attempts,
    )

    if not results:
        typer.echo("No results generated.")
        raise typer.Exit(code=1)

    report = score_results(results)

    from embedeval.reporter import generate_json, generate_leaderboard

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{model}-results.json"
    generate_json(report, json_path)

    leaderboard_path = output_dir / "LEADERBOARD.md"
    generate_leaderboard([report], leaderboard_path)

    typer.echo(f"Results: {json_path}")
    typer.echo(f"Leaderboard: {leaderboard_path}")


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
