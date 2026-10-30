"""Ezaki & Masuda (2017) rings without lockstep updating (added 2026-10-26).

validate_bm.py reproduces their result: on a ring, a static network beats a shuffled one
(network reciprocity) at k = 2, b/c = 6, but not at b/c = 2, and the gap shrinks as k grows.
They update every player every round. Here the same setup is rerun with only a fraction f
of the players updating per round. To keep learning time equal, a run lasts 50/f rounds and
cooperation is averaged over the first 25/f rounds (their rounds 1-25), so every player gets
about the same number of updates as in their 50-round runs.

Same model and seeds as validate_bm.py (Mesa reference model), so f = 1 must reproduce
results/validate_bm.csv exactly. f = 0.05 stands in for one player at a time.

Run from project root: python src/ring_async.py [--processes 12]
Writes results/ring_async.csv and results/ring_async.png
"""
import os
import sys
from multiprocessing import Pool

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from model import CooperationModel
from networks import RESULTS_DIR

N = 100
BASE_ROUNDS = 50
BASE_AVERAGE_OVER = 25  # first 25 rounds, as in the paper
RUNS = 1000
BM_PARAMS = {"beta": 0.2, "aspiration": 1.0, "epsilon": 0.05, "initial_coop": 0.8}
KS = [2, 4, 6, 8]
BENEFITS = [2.0, 6.0]
FRACTIONS = [1.0, 0.5, 0.25, 0.1, 0.05]


def ring(k):
    # each node linked to k/2 nodes on each side (Watts-Strogatz with no rewiring)
    return nx.watts_strogatz_graph(N, k, 0.0)


def run_setting(job):
    """All RUNS runs of one (k, b, shuffled, f). Returns mean cooperation over the first
    25/f rounds and over rounds 25/f to 50/f."""
    k, b, shuffled, fraction = job
    G = ring(k)
    rounds = int(round(BASE_ROUNDS / fraction))
    first_part = int(round(BASE_AVERAGE_OVER / fraction))
    early_total = 0.0
    late_total = 0.0
    for seed in range(RUNS):
        model = CooperationModel(G, "bm", game="donation", b=b, c=1.0, shuffle_seats=shuffled,
                                 update_fraction=fraction, seed=seed, **BM_PARAMS)
        model.run(rounds)
        curve = model.datacollector.model_vars["cooperation"]
        early_total += sum(curve[:first_part]) / first_part
        late_total += sum(curve[first_part:]) / (rounds - first_part)
    treatment = "shuffled" if shuffled else "static"
    return {"k": k, "b_over_c": b, "treatment": treatment, "update_fraction": fraction,
            "rounds": rounds, "cooperation": early_total / RUNS,
            "cooperation_late": late_total / RUNS}


def processes_from_command_line():
    if "--processes" not in sys.argv:
        return 12
    position = sys.argv.index("--processes")
    return max(1, int(sys.argv[position + 1]))


def main():
    jobs = []
    for fraction in FRACTIONS:
        for k in KS:
            for b in BENEFITS:
                for shuffled in [False, True]:
                    jobs.append((k, b, shuffled, fraction))
    # longest runs first, so the pool finishes evenly
    jobs.sort(key=lambda job: job[3])
    with Pool(processes_from_command_line()) as pool:
        rows = pool.map(run_setting, jobs)
    table = pd.DataFrame(rows).sort_values(["update_fraction", "k", "b_over_c", "treatment"],
                                           ascending=[False, True, True, True])
    os.makedirs(RESULTS_DIR, exist_ok=True)
    table.to_csv(os.path.join(RESULTS_DIR, "ring_async.csv"), index=False)

    # gap = static - shuffled (network reciprocity), per k, b/c and f
    gaps = []
    for (k, b, fraction), part in table.groupby(["k", "b_over_c", "update_fraction"]):
        static = part[part["treatment"] == "static"]
        shuffled = part[part["treatment"] == "shuffled"]
        gaps.append({"k": k, "b_over_c": b, "update_fraction": fraction,
                     "gap": static["cooperation"].iloc[0] - shuffled["cooperation"].iloc[0],
                     "gap_late": static["cooperation_late"].iloc[0] - shuffled["cooperation_late"].iloc[0]})
    gaps = pd.DataFrame(gaps)
    print("static minus shuffled, first 25/f rounds (rows k, b/c; columns f):")
    print(gaps.pivot_table(index=["k", "b_over_c"], columns="update_fraction", values="gap")
          .round(3).to_string())
    print("\nsame, rounds 25/f to 50/f:")
    print(gaps.pivot_table(index=["k", "b_over_c"], columns="update_fraction", values="gap_late")
          .round(3).to_string())

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, b in zip(axes, BENEFITS):
        for k in KS:
            part = gaps[(gaps["k"] == k) & (gaps["b_over_c"] == b)].sort_values("update_fraction",
                                                                                   ascending=False)
            ax.plot(range(len(part)), part["gap"], marker="o", label=f"k = {k}")
        ax.set_xticks(range(len(FRACTIONS)))
        ax.set_xticklabels(["1 (sync)", "0.5", "0.25", "0.1", "0.05"])
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"b/c = {b:.0f}")
        ax.set_xlabel("update fraction f (equal updates per player)")
    axes[0].set_ylabel("static - shuffled cooperation")
    axes[0].legend()
    fig.suptitle(f"Ezaki & Masuda rings without lockstep ({RUNS} runs per point)")
    fig.savefig(os.path.join(RESULTS_DIR, "ring_async.png"), dpi=150, bbox_inches="tight")
    print("saved results/ring_async.csv, results/ring_async.png")


if __name__ == "__main__":
    main()
