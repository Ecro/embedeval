"""EmbedEval CLI."""

import typer

app = typer.Typer(help="EmbedEval: Embedded firmware LLM benchmark")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """EmbedEval benchmark tool."""
    if ctx.invoked_subcommand is None:
        typer.echo("EmbedEval v0.1.0 — use --help for commands")
