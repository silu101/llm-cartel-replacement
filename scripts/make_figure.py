"""Figure 1: post-branch market gain by arm (mean, 95% bootstrap CI, one dot per seed).

    cd collusion_hackathon/llm-cartel
    uv run --with matplotlib python /Users/silu/Sakana/collusion_1p2/make_figure.py
"""

import glob
import json
import os
import random
import statistics as st

import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

# Validated categorical slots 1-3 (dataviz reference palette, light mode) + neutral for controls.
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"

# (label in results, display name, group color)
ARMS = [
    ("A0_control", "A0  No change (control)", GRAY),
    ("A1_maverick", "A1  1 firm → Luna (maverick)", BLUE),
    ("A2_amnesic", "A2  1 firm → fresh Gemini, no history", BLUE),
    ("A3_maverick_amnesic", "A3  1 firm → Luna, no history", BLUE),
    ("A4_theseus", "A4  Both firms → Haiku (Ship of Theseus)", ORANGE),
    ("A4w10_theseus_window10", "A4-k10  … newcomers see last 10 rounds", ORANGE),
    ("A4w1_theseus_window1", "A4-k1  … newcomers see last 1 round", ORANGE),
    ("A4p_placebo", "A4p Placebo: both → Haiku, competitive history", GRAY),
    ("A6_compliant", "A6  1 firm → Gemini told to avoid collusion", AQUA),
]


def load_arm(label):
    vals = []
    for c in glob.glob("results/branches/*.config.json"):
        cfg = json.load(open(c))
        lab = cfg.get("branch_label", "").replace("_win100", "")
        lab = "A4p_placebo" if lab.startswith("A4p") else lab
        if lab == label and cfg.get("comparison"):
            vals.append(cfg["comparison"]["mean_gain_after"])
    return vals


def boot_ci(x, n=10000, seed=0):
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choices(x, k=len(x))) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def main():
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 10})
    fig, ax = plt.subplots(figsize=(7.2, 4.8), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    rows = list(reversed(ARMS))
    for y, (label, name, color) in enumerate(rows):
        v = load_arm(label)
        m = st.mean(v)
        lo, hi = boot_ci(v)
        ax.plot([lo, hi], [y, y], color=color, lw=2, solid_capstyle="round", zorder=2)
        jitter = random.Random(y)
        ax.scatter(v, [y + jitter.uniform(-0.18, 0.18) for _ in v], s=14, color=color, alpha=0.45,
                   linewidths=0, zorder=1)
        ax.scatter([m], [y], s=64, color=color, edgecolors=SURFACE, linewidths=2, zorder=3)
        ax.text(1.13, y, f"{m:.2f}", va="center", ha="right", color=INK, fontsize=9)

    ax.axvline(0, color=INK2, lw=0.8, ls=(0, (3, 3)), zorder=0)
    ax.axvline(1, color=INK2, lw=0.8, ls=(0, (3, 3)), zorder=0)
    ax.text(0, len(rows) - 0.35, "competitive", ha="center", va="bottom", color=INK2, fontsize=8)
    ax.text(1, len(rows) - 0.35, "monopoly", ha="center", va="bottom", color=INK2, fontsize=8)

    ax.set_yticks(range(len(rows)), [r[1] for r in rows], color=INK)
    ax.set_xlim(-0.12, 1.15)
    ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xlabel("Market gain, last 20 of 50 rounds after replacement\n(0 = competitive profit, 1 = monopoly profit)",
                  color=INK2)
    ax.tick_params(colors=INK2, length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#d8d7d2")
    ax.grid(axis="x", color="#ecebe7", lw=0.6, zorder=0)
    fig.suptitle("Replacing cartel members rarely breaks the cartel", x=0.015, ha="left", color=INK,
                 fontsize=11, fontweight="bold")

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"fig1_arms.{ext}"), dpi=300, facecolor=SURFACE)
    print("saved", os.path.join(OUT, "fig1_arms.png"))


if __name__ == "__main__":
    main()
