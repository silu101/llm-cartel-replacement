"""2x2 decomposition: is persistence carried by the surviving incumbent, the inherited history, or both?

    cd collusion_hackathon/llm-cartel
    python3 -I /Users/silu/Sakana/collusion_1p2/factorial_analysis.py

Newcomers are always Claude Haiku 5.5 with the neutral prompt. "No history" newcomers start from
one Nash warm-up round (branch_game_neutral.py), matching how base runs start.
Outcome: mean market gain over post-branch rounds 11-30, per base seed (0, 2-7).
"""

import glob
import json
import random
import re
import statistics as st

CELLS = {
    ("incumbent", "history"): "F_inc1_hist1",
    ("incumbent", "no history"): "F_inc1_hist0",
    ("no incumbent", "history"): "A4_theseus",
    ("no incumbent", "no history"): "F_inc0_hist0",
}
WINDOW = slice(10, 30)  # post-branch rounds 11-30


def cell(label):
    out = {}
    for c in glob.glob(f"results/branches/*__{label}*.config.json"):
        cfg = json.load(open(c))
        if not cfg.get("comparison"):
            continue
        seed = int(re.search(r"seed(\d)", c).group(1))
        recs = [json.loads(l) for l in open(c.replace(".config.json", ".jsonl"))]
        after = [r for r in recs if r.get("branch_phase") == "after"]
        if len(after) < 30:
            continue
        out[seed] = st.mean(st.mean(r["gains"]) for r in after[WINDOW])
    return out


def boot(seeds, f, n=10000, rng=random.Random(0)):
    vals = sorted(f([rng.choice(seeds) for _ in seeds]) for _ in range(n))
    return vals[int(0.025 * n)], vals[int(0.975 * n)]


def main():
    data = {k: cell(v) for k, v in CELLS.items()}
    seeds = sorted(set.intersection(*(set(d) for d in data.values())))
    print(f"paired seeds: {seeds}\n")
    for k, d in data.items():
        v = [d[s] for s in seeds]
        lo, hi = boot(seeds, lambda ss, d=d: st.mean(d[s] for s in ss))
        print(f"  {k[0]:<13} + {k[1]:<11} gain {st.mean(v):.2f} [{lo:.2f}, {hi:.2f}]  per-seed {[round(x, 2) for x in v]}")

    I_H, I_N, N_H, N_N = (data[k] for k in CELLS)

    def effects(ss):
        hist = st.mean((I_H[s] - I_N[s] + N_H[s] - N_N[s]) / 2 for s in ss)
        inc = st.mean((I_H[s] - N_H[s] + I_N[s] - N_N[s]) / 2 for s in ss)
        inter = st.mean((I_H[s] - I_N[s]) - (N_H[s] - N_N[s]) for s in ss)
        return hist, inc, inter

    est = effects(seeds)
    names = ["history main effect", "incumbent main effect", "interaction (history effect with vs without incumbent)"]
    print()
    for i, name in enumerate(names):
        lo, hi = boot(seeds, lambda ss, i=i: effects(ss)[i])
        print(f"  {name:<58} {est[i]:+.2f} [{lo:+.2f}, {hi:+.2f}]")


if __name__ == "__main__":
    main()
