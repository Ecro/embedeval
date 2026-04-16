"""EmbedEval interactive leaderboard.

Static Gradio Space backed by the canonical n=3 results from the upstream
EmbedEval repository. To refresh, sync `LEADERBOARD_DATA` and `CATEGORY_DATA`
from `results/LEADERBOARD.md`.

Design choice: this app intentionally avoids custom CSS, custom themes, and
plotly layout overrides. Gradio 5's defaults work reliably out of the box;
fighting them with CSS hacks produced contrast bugs across multiple tabs.
"""

from __future__ import annotations

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Data (synced from results/LEADERBOARD.md, n=3 baseline 2026-04-12/13)
# ---------------------------------------------------------------------------

LEADERBOARD_ROWS = [
    ("Sonnet 4.6", "claude-code://sonnet", 68.0, "[64.4%, 71.3%]", "87.1%", 143, 30, 60),
    ("Haiku 4.5", "claude-code://haiku", 56.9, "[53.2%, 60.6%]", "73.0%", 99, 63, 71),
]

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


def category_df() -> pd.DataFrame:
    return pd.DataFrame(CATEGORY_DATA, columns=["Category", "Sonnet 4.6", "Haiku 4.5"])


# ---------------------------------------------------------------------------
# Leaderboard rendered as plain HTML — bypasses gr.Dataframe styling entirely
# ---------------------------------------------------------------------------


def leaderboard_html() -> str:
    rows_html = "".join(
        f"<tr>"
        f"<td><strong>{name}</strong><br>"
        f"<code style='font-size:0.85em;color:#6b7280'>{slug}</code></td>"
        f"<td style='text-align:right;font-size:1.2em'><strong>{mean:.1f}%</strong></td>"
        f"<td style='text-align:right'>{ci}</td>"
        f"<td style='text-align:right'>{stab}</td>"
        f"<td style='text-align:right'>{ap}</td>"
        f"<td style='text-align:right'>{flaky}</td>"
        f"<td style='text-align:right'>{af}</td>"
        f"</tr>"
        for name, slug, mean, ci, stab, ap, flaky, af in LEADERBOARD_ROWS
    )
    return f"""
<style>
  .embedeval-leaderboard {{
    width: 100%;
    border-collapse: collapse;
    font-family: system-ui, -apple-system, sans-serif;
    margin: 1em 0;
  }}
  .embedeval-leaderboard th {{
    background: #f3f4f6;
    color: #111827;
    text-align: left;
    padding: 10px;
    border-bottom: 2px solid #d1d5db;
    font-weight: 600;
  }}
  .embedeval-leaderboard td {{
    padding: 10px;
    border-bottom: 1px solid #e5e7eb;
    color: #111827;
    background: #ffffff;
  }}
</style>
<table class="embedeval-leaderboard">
  <thead>
    <tr>
      <th>Model</th>
      <th style="text-align:right">pass@1 (n=3 mean)</th>
      <th style="text-align:right">95% CI</th>
      <th style="text-align:right">Stability</th>
      <th style="text-align:right">Always Pass</th>
      <th style="text-align:right">Flaky</th>
      <th style="text-align:right">Always Fail</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
"""


# ---------------------------------------------------------------------------
# Plotly figures — no layout overrides, defaults only
# ---------------------------------------------------------------------------


def heatmap_figure() -> go.Figure:
    """Heatmap built with go.Heatmap directly. px.imshow on plotly 6.x lost
    DataFrame index/columns and rendered an empty axis."""
    df = category_df()
    cats = df["Category"].tolist()
    z = [df["Sonnet 4.6"].tolist(), df["Haiku 4.5"].tolist()]

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=cats,
            y=["Sonnet 4.6", "Haiku 4.5"],
            colorscale="RdYlGn",
            zmin=0,
            zmax=100,
            text=z,
            texttemplate="%{z:.0f}",
            textfont=dict(size=11),
            colorbar=dict(title="pass@1 %"),
        )
    )
    fig.update_layout(
        title="pass@1 by category (n=3 last run, 2026-04-12)",
        height=320,
        margin=dict(l=10, r=10, t=60, b=80),
    )
    fig.update_xaxes(tickangle=-45)
    return fig


def category_bar_figure(model: str) -> go.Figure:
    """Horizontal bar chart with explicit per-bar colors mapped onto the
    RdYlGn scale. px.bar's color_continuous_scale also fights coloraxis
    visibility settings on plotly 6.x, so we color bars manually."""
    df = category_df().sort_values(model, ascending=True)
    values = df[model].tolist()
    cats = df["Category"].tolist()

    # Map 0-100 to RdYlGn manually
    def color_for(v: float) -> str:
        # piecewise: 0 = red, 50 = yellow, 100 = green
        if v < 50:
            t = v / 50.0
            r, g = 255, int(255 * t)
        else:
            t = (v - 50) / 50.0
            r, g = int(255 * (1 - t)), 200 - int(50 * t)
        return f"rgb({r},{g},80)"

    fig = go.Figure(
        data=go.Bar(
            x=values,
            y=cats,
            orientation="h",
            marker=dict(color=[color_for(v) for v in values]),
            text=[f"{v:.0f}%" for v in values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.0f}%%<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"{model} pass@1 by category (sorted ascending — weakest at top)",
        height=720,
        margin=dict(l=10, r=40, t=60, b=10),
        xaxis=dict(title="pass@1 %", range=[0, 110]),
        yaxis=dict(title="Category"),
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# Markdown bodies
# ---------------------------------------------------------------------------

INTRO_MD = """
# EmbedEval Leaderboard

EmbedEval measures whether LLMs possess the implicit domain knowledge
required to write safe embedded firmware: interrupt safety, cache coherency,
DMA alignment, power management, real-time constraints. Prompts withhold
the safety patterns the model should derive.

- 233 cases (185 public + 48 private held-out)
- 23 categories across 6 platforms (Zephyr, ESP-IDF, STM32 HAL, FreeRTOS,
  Linux drivers, Yocto)
- 5-layer evaluation pipeline: Static, Compile, Runtime, Heuristic, Mutation
- Statistical baseline: n=3 with Wilson 95% confidence intervals

[GitHub](https://github.com/Ecro/embedeval) · [Methodology](https://github.com/Ecro/embedeval/blob/main/docs/METHODOLOGY.md) · [n=3 Reports](https://github.com/Ecro/embedeval/blob/main/docs/BENCHMARK-COMPARISON-2026-04-05.md)
"""

KEY_INSIGHT_MD = """
### Implicit knowledge gap

When prompts include explicit safety hints ("use volatile", "flush the cache
before DMA"), pass@1 sits near 95%. When the same functional requirement is
asked without those hints, pass@1 drops to about 60%.

The roughly 35 percentage point gap is what we call the implicit knowledge
gap. Most coding benchmarks include the safety hints by accident and so
overestimate LLM capability for embedded work.

Weakest categories on both models: DMA cache coherency, ISR / concurrency,
threading, memory optimization.
"""

HEATMAP_NOTE_MD = """
Heatmap of pass@1 across all 23 categories for both models. Red cells mark
LLM blind spots — DMA, ISR, threading, memory optimization. Green cells
mark areas where LLMs are reliable — device tree, Kconfig, boot sequences.
"""

BREAKDOWN_NOTE_MD = """
Pick a model. The horizontal bar chart shows that model's pass@1 across all
23 categories, sorted from weakest (top) to strongest (bottom). Compare with
the other model to see where each one is structurally weak.
"""

METHODOLOGY_MD = """
### 5-Layer Evaluation Pipeline

| Layer | Method | What it catches |
|-------|--------|-----------------|
| L0 Static | Pattern matching | Missing headers, wrong CONFIG, bad ISR signatures |
| L1 Compile | SDK compilation (Docker) | Syntax, undefined symbols, type mismatches |
| L2 Runtime | QEMU / native_sim | Segfaults, deadlocks, wrong output |
| L3 Heuristic | Domain checks | Missing volatile, wrong lock order, no error cleanup |
| L4 Mutation | Meta-verification | Validates that L0/L3 checks themselves are sound |

Failure at any layer halts evaluation. The default no-Docker mode (L0 + L3)
provides strong discriminative power on its own.

**Contamination prevention.** 48 private cases live in a separate repository
never exposed to LLM training data. Each case has a `created_date` for
temporal cutoff analysis.

Read the full methodology:
[docs/METHODOLOGY.md](https://github.com/Ecro/embedeval/blob/main/docs/METHODOLOGY.md)
"""

FOOTER_MD = (
    "---\n"
    "EmbedEval is Apache-2.0 licensed. PRs welcome at "
    "[github.com/Ecro/embedeval](https://github.com/Ecro/embedeval)."
)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


FORCE_LIGHT_CSS = """
/* Override dark-mode contrast: always render with light background and
   dark text, regardless of OS color-scheme preference. Targets cover
   gradio's typical class names plus the .dark scope it injects. */
html, body, .gradio-container, .dark, .dark .gradio-container {
    background: #ffffff !important;
}
.prose, .prose *, .dark .prose, .dark .prose * {
    color: #111827 !important;
}
.prose a, .dark .prose a { color: #4338ca !important; text-decoration: underline; }
.dark { color: #111827 !important; }

/* Tab labels */
button[role="tab"] { color: #4b5563 !important; }
button[role="tab"][aria-selected="true"] { color: #4338ca !important; font-weight: 600; }

/* Footer */
footer, footer * { color: #6b7280 !important; }
footer a { color: #4338ca !important; }

/* Inline code (gradio defaults to dark background which clashes) */
code, .prose code, .dark code, .dark .prose code {
    color: #b91c1c !important;
    background: #fef2f2 !important;
    padding: 1px 5px !important;
    border-radius: 3px !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace !important;
}
"""


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="EmbedEval Leaderboard", css=FORCE_LIGHT_CSS) as demo:
        gr.Markdown(INTRO_MD)

        with gr.Tab("Leaderboard"):
            gr.HTML(leaderboard_html())
            gr.Markdown(KEY_INSIGHT_MD)

        with gr.Tab("Heatmap"):
            gr.Plot(value=heatmap_figure())
            gr.Markdown(HEATMAP_NOTE_MD)

        with gr.Tab("Per-model breakdown"):
            gr.Markdown(BREAKDOWN_NOTE_MD)
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
            gr.Markdown(METHODOLOGY_MD)

        gr.Markdown(FOOTER_MD)

    return demo


if __name__ == "__main__":
    build_ui().launch()
