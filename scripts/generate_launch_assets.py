"""Generate visual assets for the public launch.

Reads the canonical n=3 numbers (currently inlined; refresh from
`results/LEADERBOARD.md` when results change) and produces five PNGs in
`assets/launch/`:

  - heatmap.png             — 23 categories x 2 models heatmap
  - implicit-gap.png        — explicit vs implicit prompt pass-rate gap
  - architecture.png        — 5-layer evaluation pipeline diagram
  - twitter-card.png        — 1200x630 composite for social
  - model-comparison.png    — Sonnet vs Haiku n=3 mean + 95% CI bars

Run:
    uv run python scripts/generate_launch_assets.py

Dependencies: matplotlib (install via `uv pip install --system matplotlib`
or add to dev-dependencies temporarily).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "assets" / "launch"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Data (sync with results/LEADERBOARD.md, n=3 baseline 2026-04-12/13)
# ---------------------------------------------------------------------------

CATEGORIES = [
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

# n=3 pooled
SONNET_MEAN = 68.0
SONNET_CI = (64.4, 71.3)
HAIKU_MEAN = 56.9
HAIKU_CI = (53.2, 60.6)

# Implicit knowledge gap (LLM-EMBEDDED-CONSIDERATIONS)
EXPLICIT_PASS = 95
IMPLICIT_PASS = 60


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------


def heatmap() -> None:
    cats = [row[0] for row in CATEGORIES]
    sonnet = [row[1] for row in CATEGORIES]
    haiku = [row[2] for row in CATEGORIES]
    matrix = np.array([sonnet, haiku])

    fig, ax = plt.subplots(figsize=(16, 3.6))
    im = ax.imshow(
        matrix,
        cmap="RdYlGn",
        vmin=0,
        vmax=100,
        aspect="auto",
    )
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(cats, rotation=45, ha="right")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Sonnet 4.6", "Haiku 4.5"])

    # Annotate each cell
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            value = matrix[y, x]
            color = "black" if 35 < value < 75 else "white"
            ax.text(
                x,
                y,
                f"{int(value)}",
                ha="center",
                va="center",
                color=color,
                fontsize=9,
                fontweight="bold",
            )

    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("pass@1 (%)", rotation=270, labelpad=15)
    ax.set_title(
        "EmbedEval pass@1 by category — n=3 last run (2026-04-12)",
        fontsize=13,
        pad=12,
    )
    ax.grid(False)
    plt.tight_layout()
    plt.savefig(OUT / "heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Implicit gap
# ---------------------------------------------------------------------------


def implicit_gap() -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        ["Explicit prompt\n(includes safety hints)", "Implicit prompt\n(domain knowledge required)"],
        [EXPLICIT_PASS, IMPLICIT_PASS],
        color=["#2ecc71", "#e67e22"],
        width=0.55,
    )
    ax.set_ylim(0, 110)
    ax.set_ylabel("pass@1 (%)", fontsize=12)
    ax.set_title(
        "Implicit knowledge gap — Sonnet 4.6 on safety-critical patterns",
        fontsize=13,
        pad=14,
    )

    for bar, value in zip(bars, [EXPLICIT_PASS, IMPLICIT_PASS]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 2,
            f"{value}%",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=14,
        )

    # Gap arrow
    gap = EXPLICIT_PASS - IMPLICIT_PASS
    ax.annotate(
        "",
        xy=(0.5, EXPLICIT_PASS - 1),
        xytext=(0.5, IMPLICIT_PASS + 1),
        arrowprops=dict(arrowstyle="<->", color="#34495e", lw=2),
    )
    ax.text(
        0.55,
        (EXPLICIT_PASS + IMPLICIT_PASS) / 2,
        f"{gap} percentage\npoint gap",
        ha="left",
        va="center",
        fontsize=12,
        color="#34495e",
        fontweight="bold",
    )

    ax.text(
        0.5,
        -0.18,
        "Most coding benchmarks include safety hints by accident → overestimate LLM capability",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="#7f8c8d",
        style="italic",
    )

    plt.tight_layout()
    plt.savefig(OUT / "implicit-gap.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# 5-layer architecture
# ---------------------------------------------------------------------------


def architecture() -> None:
    layers = [
        ("L0 Static", "Pattern matching", "missing headers, bad ISR sigs", "#3498db"),
        ("L1 Compile", "Docker SDK build", "syntax, undefined symbols", "#9b59b6"),
        ("L2 Runtime", "QEMU / native_sim", "segfaults, deadlocks", "#e67e22"),
        ("L3 Heuristic", "Domain checks", "missing volatile, lock order", "#1abc9c"),
        ("L4 Mutation", "Meta-verification", "validates L0/L3 checks", "#e74c3c"),
    ]

    fig, ax = plt.subplots(figsize=(13, 4.5))

    box_w = 2.2
    box_h = 2.5
    x_pad = 0.4
    for i, (layer, method, catches, color) in enumerate(layers):
        x = i * (box_w + x_pad)
        rect = mpatches.FancyBboxPatch(
            (x, 1),
            box_w,
            box_h,
            boxstyle="round,pad=0.06,rounding_size=0.18",
            linewidth=1.5,
            edgecolor=color,
            facecolor="white",
        )
        ax.add_patch(rect)
        ax.text(
            x + box_w / 2,
            1 + box_h - 0.5,
            layer,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=12,
            color=color,
        )
        ax.text(
            x + box_w / 2,
            1 + box_h - 1.2,
            method,
            ha="center",
            va="center",
            fontsize=10,
            color="#34495e",
        )
        ax.text(
            x + box_w / 2,
            1 + 0.6,
            catches,
            ha="center",
            va="center",
            fontsize=9,
            color="#7f8c8d",
            style="italic",
        )

        # Arrow to next
        if i < len(layers) - 1:
            ax.annotate(
                "",
                xy=(x + box_w + x_pad, 1 + box_h / 2),
                xytext=(x + box_w, 1 + box_h / 2),
                arrowprops=dict(arrowstyle="->", color="#34495e", lw=1.6),
            )

    ax.text(
        (len(layers) * (box_w + x_pad)) / 2 - x_pad / 2,
        4.4,
        "EmbedEval — 5-layer evaluation pipeline",
        ha="center",
        fontsize=14,
        fontweight="bold",
    )
    ax.text(
        (len(layers) * (box_w + x_pad)) / 2 - x_pad / 2,
        0.55,
        "Failure at any layer halts evaluation. Default no-Docker mode = L0 + L3.",
        ha="center",
        fontsize=10,
        color="#7f8c8d",
        style="italic",
    )

    ax.set_xlim(-0.3, len(layers) * (box_w + x_pad))
    ax.set_ylim(0, 5)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(OUT / "architecture.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Model comparison (n=3 mean + CI)
# ---------------------------------------------------------------------------


def model_comparison() -> None:
    models = ["Sonnet 4.6", "Haiku 4.5"]
    means = [SONNET_MEAN, HAIKU_MEAN]
    ci_low = [SONNET_MEAN - SONNET_CI[0], HAIKU_MEAN - HAIKU_CI[0]]
    ci_high = [SONNET_CI[1] - SONNET_MEAN, HAIKU_CI[1] - HAIKU_MEAN]
    colors = ["#2980b9", "#16a085"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(models, means, color=colors, width=0.45)
    ax.errorbar(
        models,
        means,
        yerr=[ci_low, ci_high],
        fmt="none",
        ecolor="#2c3e50",
        elinewidth=2,
        capsize=8,
    )
    ax.set_ylim(0, 100)
    ax.set_ylabel("pass@1 % (n=3 mean)", fontsize=12)
    ax.set_title(
        "EmbedEval n=3 baseline — 95% Wilson CI (pooled 699 trials)",
        fontsize=13,
        pad=12,
    )

    for bar, value, lo, hi in zip(bars, means, [SONNET_CI[0], HAIKU_CI[0]], [SONNET_CI[1], HAIKU_CI[1]]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 4,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=13,
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value - 6,
            f"[{lo}, {hi}]",
            ha="center",
            va="top",
            fontsize=9,
            color="white",
        )

    ax.text(
        0.5,
        -0.15,
        "CIs do not overlap — gap is statistically significant (p<0.05)",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="#7f8c8d",
        style="italic",
    )

    plt.tight_layout()
    plt.savefig(OUT / "model-comparison.png", dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Twitter card (1200x630 composite)
# ---------------------------------------------------------------------------


def twitter_card() -> None:
    fig = plt.figure(figsize=(12, 6.3), facecolor="white")
    fig.suptitle(
        "EmbedEval",
        fontsize=32,
        fontweight="bold",
        y=0.95,
        color="#2c3e50",
    )

    fig.text(
        0.5,
        0.86,
        "LLM benchmark for embedded firmware",
        ha="center",
        fontsize=14,
        color="#7f8c8d",
        style="italic",
    )

    # Left panel: model comparison
    ax1 = fig.add_axes([0.06, 0.15, 0.4, 0.6])
    bars = ax1.bar(
        ["Sonnet 4.6", "Haiku 4.5"],
        [SONNET_MEAN, HAIKU_MEAN],
        color=["#2980b9", "#16a085"],
        width=0.5,
    )
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("pass@1 % (n=3)", fontsize=11)
    ax1.set_title("n=3 baseline + 95% CI", fontsize=12)
    ax1.errorbar(
        ["Sonnet 4.6", "Haiku 4.5"],
        [SONNET_MEAN, HAIKU_MEAN],
        yerr=[
            [SONNET_MEAN - SONNET_CI[0], HAIKU_MEAN - HAIKU_CI[0]],
            [SONNET_CI[1] - SONNET_MEAN, HAIKU_CI[1] - HAIKU_MEAN],
        ],
        fmt="none",
        ecolor="#2c3e50",
        elinewidth=2,
        capsize=8,
    )
    for bar, value in zip(bars, [SONNET_MEAN, HAIKU_MEAN]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            value + 4,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", alpha=0.25)

    # Right panel: implicit gap
    ax2 = fig.add_axes([0.55, 0.15, 0.4, 0.6])
    bars2 = ax2.bar(
        ["Explicit\nprompt", "Implicit\nprompt"],
        [EXPLICIT_PASS, IMPLICIT_PASS],
        color=["#2ecc71", "#e67e22"],
        width=0.5,
    )
    ax2.set_ylim(0, 110)
    ax2.set_ylabel("pass@1 %", fontsize=11)
    ax2.set_title("Implicit knowledge gap (~35pp)", fontsize=12)
    for bar, value in zip(bars2, [EXPLICIT_PASS, IMPLICIT_PASS]):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            value + 3,
            f"{value}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.25)

    fig.text(
        0.5,
        0.05,
        "233 cases · 23 categories · 6 platforms · 5-layer evaluation pipeline",
        ha="center",
        fontsize=11,
        color="#34495e",
    )
    fig.text(
        0.5,
        0.015,
        "github.com/Ecro/embedeval",
        ha="center",
        fontsize=10,
        color="#3498db",
    )

    plt.savefig(OUT / "twitter-card.png", dpi=100, bbox_inches="tight", facecolor="white")
    plt.close()


# ---------------------------------------------------------------------------


def main() -> None:
    _setup_style()
    print(f"Generating launch assets in {OUT}")
    heatmap()
    print("  ✓ heatmap.png")
    implicit_gap()
    print("  ✓ implicit-gap.png")
    architecture()
    print("  ✓ architecture.png")
    model_comparison()
    print("  ✓ model-comparison.png")
    twitter_card()
    print("  ✓ twitter-card.png")
    print("Done.")


if __name__ == "__main__":
    main()
