"""EmbedEval interactive leaderboard.

Static Gradio Space backed by the canonical n=3 results from
the upstream EmbedEval repository. To refresh, sync `LEADERBOARD_DATA`
and `CATEGORY_DATA` from `results/LEADERBOARD.md`.
"""

from __future__ import annotations

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Data (synced from results/LEADERBOARD.md, n=3 baseline 2026-04-12/13)
# ---------------------------------------------------------------------------

LEADERBOARD_DATA = [
    {
        "Model": "claude-code://sonnet (Sonnet 4.6)",
        "pass@1 (n=3 mean)": "68.0%",
        "95% CI": "[64.4%, 71.3%]",
        "Stability": "87.1%",
        "Always Pass": 143,
        "Flaky (1-2/3)": 30,
        "Always Fail": 60,
        "Total Cases": 233,
    },
    {
        "Model": "claude-code://haiku (Haiku 4.5)",
        "pass@1 (n=3 mean)": "56.9%",
        "95% CI": "[53.2%, 60.6%]",
        "Stability": "73.0%",
        "Always Pass": 99,
        "Flaky (1-2/3)": 63,
        "Always Fail": 71,
        "Total Cases": 233,
    },
]

# Category, Sonnet pass@1, Haiku pass@1 (n=3 last run)
CATEGORY_DATA = [
    ("adc", 100, 50),
    ("ble", 82, 45),
    ("boot", 90, 100),
    ("device-tree", 100, 100),
    ("dma", 31, 8),
    ("gpio-basic", 67, 83),
    ("isr-concurrency", 23, 38),
    ("kconfig", 90, 60),
    ("linux-driver", 70, 70),
    ("memory-opt", 67, 33),
    ("networking", 75, 75),
    ("ota", 67, 58),
    ("power-mgmt", 75, 67),
    ("pwm", 100, 100),
    ("security", 50, 70),
    ("sensor-driver", 75, 67),
    ("spi-i2c", 79, 64),
    ("storage", 54, 31),
    ("threading", 33, 33),
    ("timer", 83, 50),
    ("uart", 33, 67),
    ("watchdog", 90, 60),
    ("yocto", 80, 70),
]


def leaderboard_df() -> pd.DataFrame:
    return pd.DataFrame(LEADERBOARD_DATA)


def category_df() -> pd.DataFrame:
    return pd.DataFrame(
        CATEGORY_DATA,
        columns=["Category", "Sonnet 4.6", "Haiku 4.5"],
    )


def heatmap_figure() -> go.Figure:
    df = category_df().set_index("Category")
    fig = px.imshow(
        df.T,
        color_continuous_scale="RdYlGn",
        zmin=0,
        zmax=100,
        aspect="auto",
        labels={"x": "Category", "y": "Model", "color": "pass@1 %"},
        text_auto=True,
    )
    fig.update_layout(
        title="pass@1 by category (n=3 last run, 2026-04-12)",
        height=320,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig.update_xaxes(tickangle=-45)
    return fig


def category_bar_figure(model: str) -> go.Figure:
    df = category_df().sort_values(model, ascending=True)
    fig = px.bar(
        df,
        y="Category",
        x=model,
        orientation="h",
        color=model,
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        text=model,
        labels={model: "pass@1 %"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        title=f"{model} — pass@1 by category (sorted)",
        height=720,
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
    )
    return fig


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

INTRO_MD = """
# EmbedEval Leaderboard

EmbedEval measures whether LLMs possess the implicit domain knowledge required
to write safe embedded firmware: interrupt safety, cache coherency, DMA
alignment, power management, real-time constraints. Prompts withhold the
safety patterns the model should derive.

- 233 cases (185 public + 48 private held-out)
- 23 categories across 6 platforms (Zephyr, ESP-IDF, STM32 HAL, FreeRTOS, Linux drivers, Yocto)
- 5-layer evaluation pipeline: Static, Compile, Runtime, Heuristic, Mutation
- Statistical baseline: n=3 with Wilson 95% confidence intervals

[GitHub](https://github.com/Ecro/embedeval) ·
[Methodology](https://github.com/Ecro/embedeval/blob/main/docs/METHODOLOGY.md) ·
[n=3 Reports](https://github.com/Ecro/embedeval/blob/main/docs/BENCHMARK-COMPARISON-2026-04-05.md)
"""

KEY_INSIGHT_MD = """
### Implicit knowledge gap

When prompts include explicit safety hints ("use volatile", "flush the cache
before DMA"), pass@1 sits near 95%. When the same functional requirement is
asked without those hints, pass@1 drops to about 60%.

The ~35 percentage point gap is what we call the implicit knowledge gap.
Most coding benchmarks include the safety hints by accident and so
overestimate LLM capability for embedded work.

Weakest categories on both models: DMA cache coherency, ISR / concurrency,
threading, memory optimization.
"""


def build_ui() -> gr.Blocks:
    with gr.Blocks(
        title="EmbedEval Leaderboard",
        theme=gr.themes.Default(
            primary_hue="indigo",
            neutral_hue="slate",
        ),
    ) as demo:
        gr.Markdown(INTRO_MD)

        with gr.Tab("Leaderboard"):
            gr.Dataframe(
                value=leaderboard_df(),
                interactive=False,
                wrap=True,
            )
            gr.Markdown(KEY_INSIGHT_MD)

        with gr.Tab("Heatmap"):
            gr.Plot(value=heatmap_figure())
            gr.Markdown(
                "Heatmap of pass@1 across all 23 categories for both models. "
                "Red cells = LLM blind spots."
            )

        with gr.Tab("Per-model breakdown"):
            model_choice = gr.Radio(
                choices=["Sonnet 4.6", "Haiku 4.5"],
                value="Sonnet 4.6",
                label="Model",
            )
            bar_plot = gr.Plot(value=category_bar_figure("Sonnet 4.6"))
            model_choice.change(
                fn=category_bar_figure,
                inputs=model_choice,
                outputs=bar_plot,
            )

        with gr.Tab("How it works"):
            gr.Markdown(
                """
                ### 5-Layer Evaluation Pipeline

                | Layer | Method | Catches |
                |-------|--------|---------|
                | **L0** Static | Pattern matching | Missing headers, wrong CONFIG, bad ISR signatures |
                | **L1** Compile | SDK compilation (Docker) | Syntax, undefined symbols, type mismatches |
                | **L2** Runtime | QEMU / native_sim | Segfaults, deadlocks, wrong output |
                | **L3** Heuristic | Domain checks | Missing volatile, wrong lock order, no error cleanup |
                | **L4** Mutation | Meta-verification | Validates that L0/L3 checks themselves are sound |

                Failure at any layer halts evaluation. The default no-Docker
                mode (L0+L3) provides strong discriminative power on its own.

                **Contamination prevention.** 48 private cases live in a
                separate repository never exposed to LLM training data.
                Each case has a `created_date` for temporal cutoff analysis.

                Read the full methodology:
                [docs/METHODOLOGY.md](https://github.com/Ecro/embedeval/blob/main/docs/METHODOLOGY.md)
                """
            )

        gr.Markdown(
            "---\n"
            "EmbedEval is Apache-2.0 licensed. "
            "PRs welcome at [github.com/Ecro/embedeval](https://github.com/Ecro/embedeval)."
        )

    return demo


if __name__ == "__main__":
    build_ui().launch()
