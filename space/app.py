"""EmbedEval interactive leaderboard.

Static Gradio Space backed by the canonical results from the upstream
EmbedEval repository (n=3 where available; Opus 5 is n=1 so far). To refresh,
sync `LEADERBOARD_ROWS` and `CATEGORY_DATA` from `results/LEADERBOARD.md` and
`docs/BENCHMARK-n3-*.md`.

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
# Data (synced from results/LEADERBOARD.md and docs/BENCHMARK-n3-*.md)
# ---------------------------------------------------------------------------

# name, slug, pass@1, samples, 95% CI, stability, always-pass, flaky, always-fail
# Stability / flaky need n >= 2; an n=1 model reports "—" for both.
LEADERBOARD_ROWS = [
    ("Sonnet 4.6", "claude-code://sonnet", 68.0, "n=3", "[64.4%, 71.3%]", "87.1%", 143, 30, 60),  # noqa: E501
    ("Sonnet 5", "claude-code://claude-sonnet-5", 67.0, "n=3", "[63.7%, 70.2%]", "82.1%", 152, 47, 64),  # noqa: E501
    ("Opus 5", "claude-code://claude-opus-5", 61.8, "n=1", "[55.8%, 67.4%]", "—", 165, "—", 102),  # noqa: E501
    ("Haiku 4.5", "claude-code://haiku", 56.9, "n=3", "[53.2%, 60.6%]", "73.0%", 99, 63, 71),  # noqa: E501
]

MODEL_NAMES = [row[0] for row in LEADERBOARD_ROWS]

# category -> {model name: pass@1 %}. None marks a category the model's run
# predates (linux-userspace was added after the 2026-04-12 n=3 baseline), so
# the heatmap leaves a gap instead of implying a zero.
CATEGORY_DATA: dict[str, dict[str, float | None]] = {
    "adc": {"Sonnet 4.6": 100, "Sonnet 5": 100.0, "Opus 5": 50.0, "Haiku 4.5": 50},
    "ble": {"Sonnet 4.6": 82, "Sonnet 5": 72.7, "Opus 5": 63.6, "Haiku 4.5": 45},
    "boot": {"Sonnet 4.6": 90, "Sonnet 5": 100.0, "Opus 5": 100.0, "Haiku 4.5": 100},
    "device-tree": {"Sonnet 4.6": 100, "Sonnet 5": 96.7, "Opus 5": 100.0, "Haiku 4.5": 100},  # noqa: E501
    "dma": {"Sonnet 4.6": 31, "Sonnet 5": 30.8, "Opus 5": 38.5, "Haiku 4.5": 8},
    "gpio-basic": {"Sonnet 4.6": 67, "Sonnet 5": 83.3, "Opus 5": 83.3, "Haiku 4.5": 83},
    "isr-concurrency": {"Sonnet 4.6": 23, "Sonnet 5": 41.0, "Opus 5": 30.8, "Haiku 4.5": 38},  # noqa: E501
    "kconfig": {"Sonnet 4.6": 90, "Sonnet 5": 70.0, "Opus 5": 80.0, "Haiku 4.5": 60},
    "linux-driver": {"Sonnet 4.6": 70, "Sonnet 5": 68.8, "Opus 5": 72.2, "Haiku 4.5": 70},  # noqa: E501
    "linux-userspace": {"Sonnet 4.6": None, "Sonnet 5": 75.0, "Opus 5": 50.0, "Haiku 4.5": None},  # noqa: E501
    "memory-opt": {"Sonnet 4.6": 67, "Sonnet 5": 55.6, "Opus 5": 58.3, "Haiku 4.5": 33},
    "networking": {"Sonnet 4.6": 75, "Sonnet 5": 58.8, "Opus 5": 52.9, "Haiku 4.5": 75},
    "ota": {"Sonnet 4.6": 67, "Sonnet 5": 66.7, "Opus 5": 44.4, "Haiku 4.5": 58},
    "power-mgmt": {"Sonnet 4.6": 75, "Sonnet 5": 83.3, "Opus 5": 66.7, "Haiku 4.5": 67},
    "pwm": {"Sonnet 4.6": 100, "Sonnet 5": 100.0, "Opus 5": 100.0, "Haiku 4.5": 100},
    "security": {"Sonnet 4.6": 50, "Sonnet 5": 53.3, "Opus 5": 40.0, "Haiku 4.5": 70},
    "sensor-driver": {"Sonnet 4.6": 75, "Sonnet 5": 66.7, "Opus 5": 75.0, "Haiku 4.5": 67},  # noqa: E501
    "spi-i2c": {"Sonnet 4.6": 79, "Sonnet 5": 83.3, "Opus 5": 71.4, "Haiku 4.5": 64},
    "storage": {"Sonnet 4.6": 54, "Sonnet 5": 51.3, "Opus 5": 46.2, "Haiku 4.5": 31},
    "threading": {"Sonnet 4.6": 33, "Sonnet 5": 48.9, "Opus 5": 40.0, "Haiku 4.5": 33},
    "timer": {"Sonnet 4.6": 83, "Sonnet 5": 77.8, "Opus 5": 66.7, "Haiku 4.5": 50},
    "uart": {"Sonnet 4.6": 33, "Sonnet 5": 66.7, "Opus 5": 33.3, "Haiku 4.5": 67},
    "watchdog": {"Sonnet 4.6": 90, "Sonnet 5": 76.7, "Opus 5": 70.0, "Haiku 4.5": 60},
    "yocto": {"Sonnet 4.6": 80, "Sonnet 5": 63.9, "Opus 5": 78.6, "Haiku 4.5": 70},
}


def category_df() -> pd.DataFrame:
    records = [
        {"Category": cat, **{m: per_model.get(m) for m in MODEL_NAMES}}
        for cat, per_model in CATEGORY_DATA.items()
    ]
    return pd.DataFrame(records, columns=["Category", *MODEL_NAMES])


# ---------------------------------------------------------------------------
# Leaderboard rendered as plain HTML — bypasses gr.Dataframe styling entirely
# ---------------------------------------------------------------------------


def leaderboard_html() -> str:
    rows_html = "".join(
        f"<tr>"
        f"<td><strong>{name}</strong><br>"
        f"<code style='font-size:0.85em;color:#6b7280'>{slug}</code></td>"
        f"<td style='text-align:right;font-size:1.2em'><strong>{mean:.1f}%</strong></td>"
        f"<td style='text-align:right'>{samples}</td>"
        f"<td style='text-align:right'>{ci}</td>"
        f"<td style='text-align:right'>{stab}</td>"
        f"<td style='text-align:right'>{ap}</td>"
        f"<td style='text-align:right'>{flaky}</td>"
        f"<td style='text-align:right'>{af}</td>"
        f"</tr>"
        for name, slug, mean, samples, ci, stab, ap, flaky, af in LEADERBOARD_ROWS
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
      <th style="text-align:right">pass@1</th>
      <th style="text-align:right">Samples</th>
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
    z = [df[model].tolist() for model in MODEL_NAMES]

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=cats,
            y=MODEL_NAMES,
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
        title="pass@1 by category (blank = category postdates that model's run)",
        height=110 + 55 * len(MODEL_NAMES),
        margin=dict(l=10, r=10, t=60, b=80),
    )
    fig.update_xaxes(tickangle=-45)
    return fig


def category_bar_figure(model: str) -> go.Figure:
    """Horizontal bar chart with explicit per-bar colors mapped onto the
    RdYlGn scale. px.bar's color_continuous_scale also fights coloraxis
    visibility settings on plotly 6.x, so we color bars manually."""
    # dropna: a category that postdates this model's run has no bar to draw,
    # and a NaN would blow up color_for()'s int() conversion.
    df = category_df().dropna(subset=[model]).sort_values(model, ascending=True)
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

- 267 cases (219 public + 48 private held-out)
- 24 categories across 6 platforms (Zephyr, ESP-IDF, STM32 HAL, FreeRTOS,
  Linux drivers, Yocto)
- 5-layer evaluation pipeline: Static, Compile, Runtime, Heuristic, Mutation
- Statistical baseline: n=3 with Wilson 95% confidence intervals
  (Opus 5 is n=1 so far — its confidence interval is correspondingly wider)

[GitHub](https://github.com/Ecro/embedeval) · [Methodology](https://github.com/Ecro/embedeval/blob/main/docs/METHODOLOGY.md) · [Reports](https://github.com/Ecro/embedeval/blob/main/docs/BENCHMARK-COMPARISON-2026-04-05.md)
"""

KEY_INSIGHT_MD = """
### Implicit knowledge gap

When prompts include explicit safety hints ("use volatile", "flush the cache
before DMA"), pass@1 sits near 95%. When the same functional requirement is
asked without those hints, pass@1 drops to about 60%.

The roughly 35 percentage point gap is what we call the implicit knowledge
gap. Most coding benchmarks include the safety hints by accident and so
overestimate LLM capability for embedded work.

Weakest categories on every model measured so far: DMA cache coherency,
ISR / concurrency, threading, memory optimization.
"""

HEATMAP_NOTE_MD = """
Heatmap of pass@1 across all 24 categories for every measured model. Red
cells mark LLM blind spots — DMA, ISR, threading, memory optimization. Green cells
mark areas where LLMs are reliable — device tree, Kconfig, boot sequences.
"""

BREAKDOWN_NOTE_MD = """
Pick a model. The horizontal bar chart shows that model's pass@1 across all
24 categories, sorted from weakest (top) to strongest (bottom). Switch models
to see where each one is structurally weak.
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
                choices=MODEL_NAMES,
                value=MODEL_NAMES[0],
                label="Model",
            )
            bar_plot = gr.Plot(value=category_bar_figure(MODEL_NAMES[0]))
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
