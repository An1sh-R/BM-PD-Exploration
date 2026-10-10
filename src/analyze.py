"""Analyse experiment 1 (run src/run.py first): BM with average payoff on real, degseq
and shuffled versions of the 5 networks.

0. Diagnostics   is each cell settled (drift)? Do repeats agree? Does it oscillate
                 (even_odd_gap: population flips C <-> D every round)?
1. Steps         real - shuffled (fixed partners), real - degseq (structure beyond the
                 degree sequence). Per family and per regime, never pooled over
                 families (families with opposite signs cancel out). Paired by seed.
                 95% CI over independent units: reps, except with degseq, where reps r and
                 r+5 ran on the same rewiring -> unit = rewiring (n = 5).
2. Node level    per-node cooperation vs degree and local clustering (real graphs, rep 0)

Regimes (a = A/b): "a=0" nobody is ever unhappy (payoff >= 0 = A); "A<=1" cooperators
can be satisfied; "A>1" a cooperator never reaches A (max cooperator payoff = 1);
"dead zone" a >= 0.8, nearly everyone unhappy every round, cooperation ~0.5.
Only A<=1 and A>1 are shown in the plots. With the cutoff at 0.8, A>1 exists only
for b >= 1.5 (a = 0.7 at b = 1.5; a = 0.6, 0.7 at b = 1.7, 2.0).

Run from project root:  python src/analyze.py   (or --test for the test sweep)
Writes results/<name>_*.csv and results/<name>_*.png
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

from networks import N_REWIRINGS, REAL_FILES, RESULTS_DIR, load_graph

TEST = "--test" in sys.argv
NAME = "sweep_test" if TEST else "sweep"

DRIFT_LIMIT = 0.02  # |drift| above this: run was still moving at the end
SPREAD_LIMIT = 0.05  # std between repeats above this: repeats end at different levels
OSCILLATION_LIMIT = 0.05  # |even - odd round cooperation| above this: period-2 oscillation
SLOW_BETA = 0.01  # pilot: not settled by 1000 steps
# a >= 0.8: nearly everyone unhappy, cooperation ~0.5 (mean |coop - 0.5| 0.010-0.039
# at a = 0.8 vs 0.009-0.033 at a = 0.9). Including a = 0.8 diluted the A>1 averages.
DEAD_ZONE_A = 0.8
SHOWN_REGIMES = ["A<=1", "A>1"]


def out_path(suffix):
    return os.path.join(RESULTS_DIR, NAME + suffix)


def regime(a_fraction, b):
    if a_fraction == 0:
        return "a=0"
    if a_fraction >= DEAD_ZONE_A:
        return "dead zone"
    if a_fraction * b <= 1:
        return "A<=1"
    return "A>1"


def load_bm_runs():
    """All runs, beta and a_fraction as numbers, plus a regime column."""
    runs = pd.read_csv(out_path("_runs.csv"), dtype={"beta": str, "a_fraction": str})
    bm = runs[runs["agent"] == "bm"].copy()
    bm["beta"] = bm["beta"].astype(float)
    bm["a_fraction"] = bm["a_fraction"].astype(float)
    regimes = []
    for _, row in bm.iterrows():
        regimes.append(regime(row["a_fraction"], row["b"]))
    bm["regime"] = regimes
    return bm


def independent_unit(graph_types, rep):
    """Reps r and r+5 of a degseq graph ran on the same rewiring (run.py), so with a
    degseq graph involved the independent unit is the rewiring, not the rep."""
    if "degseq" in graph_types:
        return rep % N_REWIRINGS
    return rep


def t_interval(values):
    """Mean and 95% half-width (t distribution) of a list of numbers."""
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return values.mean(), np.nan
    half = stats.t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values))
    return values.mean(), half


# ---- 0. diagnostics ----------------------------------------------------------

def diagnostics(bm):
    """Per cell (graph, b, beta, a): settled? repeats agree? oscillating?"""
    bm = bm.copy()
    bm["abs_drift"] = bm["drift"].abs()
    keys = ["graph", "graph_type", "b", "beta", "a_fraction"]
    cells = bm.groupby(keys, as_index=False).agg(
        mean_abs_drift=("abs_drift", "mean"), rep_spread=("cooperation", "std"),
        cooperation=("cooperation", "mean"), even_odd_gap=("even_odd_gap", "mean"),
        n_reps=("rep", "count"))
    # separate flag, not a status: an oscillating cell can still be settled (its mean is fine)
    cells["oscillating"] = cells["even_odd_gap"] > OSCILLATION_LIMIT
    statuses = []
    for _, cell in cells.iterrows():
        if cell["mean_abs_drift"] > DRIFT_LIMIT:
            statuses.append("still moving")  # slow convergence: longer runs needed
        elif cell["rep_spread"] > SPREAD_LIMIT:
            statuses.append("settled, repeats differ")  # repeats end at different levels
        else:
            statuses.append("ok")
    cells["status"] = statuses
    cells.to_csv(out_path("_diagnostics.csv"), index=False)

    print()
    print("DIAGNOSTICS (cells)")
    print(cells["status"].value_counts().to_string())
    slow = cells[cells["beta"] <= SLOW_BETA]
    if len(slow) > 0:
        print(f"still moving at beta={SLOW_BETA:g}: {(slow['status'] == 'still moving').mean():.0%} of cells")
    oscillating = cells[cells["oscillating"]]
    print(f"oscillating (even-odd gap > {OSCILLATION_LIMIT}): {len(oscillating)} of {len(cells)} cells"
          f" ({cells['oscillating'].mean():.0%})")
    if len(oscillating) > 0:
        print(f"  at beta {oscillating['beta'].min():g}-{oscillating['beta'].max():g}, "
              f"a {oscillating['a_fraction'].min():g}-{oscillating['a_fraction'].max():g}, "
              f"b {oscillating['b'].min():g}-{oscillating['b'].max():g}")

    rows = [("mean_abs_drift", "mean |drift|", 2 * DRIFT_LIMIT),
            ("rep_spread", "std between repeats", 2 * SPREAD_LIMIT),
            ("even_odd_gap", "even-odd gap", 2 * OSCILLATION_LIMIT)]
    temptations = sorted(cells["b"].unique())
    fig, axes = plt.subplots(len(rows), len(temptations),
                             figsize=(4 * len(temptations), 3.75 * len(rows)), squeeze=False)
    fig.subplots_adjust(hspace=0.5)
    for r, (column, title, vmax) in enumerate(rows):
        image = None
        for c, b in enumerate(temptations):
            ax = axes[r][c]
            part = cells[cells["b"] == b].groupby(["a_fraction", "beta"], as_index=False)[column].mean()
            grid = part.pivot(index="a_fraction", columns="beta", values=column)
            image = ax.imshow(grid.values, origin="lower", aspect="auto", cmap="Reds", vmin=0, vmax=vmax)
            ax.set_xticks(range(len(grid.columns)))
            ax.set_xticklabels([f"{x:g}" for x in grid.columns], rotation=45)
            ax.set_yticks(range(len(grid.index)))
            ax.set_yticklabels([f"{y:g}" for y in grid.index])
            ax.set_xlabel("beta")
            ax.set_ylabel("a = A/b")
            ax.set_title(f"{title}, b = {b:g}", fontsize=9)
        fig.colorbar(image, ax=axes[r].tolist(), shrink=0.8)
    fig.suptitle("Diagnostics, BM average payoff (mean over graphs)")
    fig.savefig(out_path("_diagnostics.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return cells


# ---- 1. steps: real/shuffled, real/degseq ------------------------------------

COMPARISONS = [("partner_effect", "real", "shuffled", "real - shuffled: fixed partners"),
               ("structure_effect", "real", "degseq", "real - degseq: structure beyond degree")]


def steps(bm):
    """Paired differences per family, regime and beta, with a 95% CI over independent
    units (see independent_unit). Per rep: mean over the regime's (b, a) cells of
    graph1 - graph2 (same seed); then averaged within each unit."""
    wide = bm.pivot_table(index=["family", "regime", "b", "beta", "a_fraction", "rep"],
                          columns="graph_type", values="cooperation").reset_index()
    rows = []
    for name, first, second, title in COMPARISONS:
        if first not in wide.columns or second not in wide.columns:
            continue
        wide["difference"] = wide[first] - wide[second]
        per_rep = wide.groupby(["family", "regime", "beta", "rep"], as_index=False)["difference"].mean()
        units = []
        for rep in per_rep["rep"]:
            units.append(independent_unit([first, second], rep))
        per_rep["unit"] = units
        per_unit = per_rep.groupby(["family", "regime", "beta", "unit"], as_index=False)["difference"].mean()
        for (family, shown, beta), group in per_unit.groupby(["family", "regime", "beta"]):
            mean, half = t_interval(group["difference"])
            rows.append({"comparison": name, "family": family, "regime": shown, "beta": beta,
                         "difference": mean, "ci": half, "n_units": len(group)})
    if not rows:
        print("steps: no comparable graph pairs in the sweep, skipped")
        return None
    table = pd.DataFrame(rows)
    table.to_csv(out_path("_steps.csv"), index=False)

    comparisons = []
    for name, first, second, title in COMPARISONS:
        if name in set(table["comparison"]):
            comparisons.append((name, title))
    fig, axes = plt.subplots(len(comparisons), len(SHOWN_REGIMES),
                             figsize=(6 * len(SHOWN_REGIMES), 3.8 * len(comparisons)), squeeze=False)
    fig.subplots_adjust(hspace=0.45)
    for r, (name, title) in enumerate(comparisons):
        for c, shown in enumerate(SHOWN_REGIMES):
            ax = axes[r][c]
            part = table[(table["comparison"] == name) & (table["regime"] == shown)]
            for family in sorted(part["family"].unique()):
                line = part[part["family"] == family].sort_values("beta")
                ax.errorbar(line["beta"], line["difference"], yerr=line["ci"], marker="o",
                            markersize=3, capsize=2, label=family)
            ax.axhline(0, color="black", linewidth=0.5)
            ax.set_xscale("log")
            ax.set_xlabel("beta")
            ax.set_title(f"{title}\nregime {shown}", fontsize=9)
            ax.set_ylabel("cooperation difference")
    axes[0][-1].legend(fontsize=7)
    fig.suptitle("BM (average payoff): mean over b and a within regime. "
                 "95% CI over reps (degseq: over 5 rewirings)")
    fig.savefig(out_path("_steps.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return table


# ---- 2. node level -------------------------------------------------------------

def node_file_name(run_id):
    # must match run.py
    return run_id.replace("|", "__").replace("=", "-") + ".npy"


def node_level(bm):
    """Rep 0 of the real graphs (run.py saves per-node cooperation only for those)."""
    nodes_dir = out_path("_nodes")
    rows = []
    for family in REAL_FILES:
        part = bm[(bm["graph"] == family) & (bm["rep"] == 0)]
        if len(part) == 0:
            continue
        G = load_graph(family)
        degrees = []
        local_clustering = []
        clustering_dict = nx.clustering(G)
        for node in range(G.number_of_nodes()):
            degrees.append(G.degree(node))
            local_clustering.append(clustering_dict[node])
        for _, run in part.iterrows():
            path = os.path.join(nodes_dir, node_file_name(run["run_id"]))
            if not os.path.exists(path):
                continue
            coop = np.load(path)
            # Spearman: rank correlation, robust to heavy-tailed degrees
            rows.append({"family": family, "b": run["b"], "beta": run["beta"],
                         "a_fraction": run["a_fraction"], "regime": run["regime"],
                         "corr_degree": stats.spearmanr(coop, degrees).statistic,
                         "corr_clustering": stats.spearmanr(coop, local_clustering).statistic})
    if not rows:
        print("node level: no node files found, skipped")
        return None
    table = pd.DataFrame(rows)
    table.to_csv(out_path("_node_level.csv"), index=False)

    fig, axes = plt.subplots(2, len(SHOWN_REGIMES), figsize=(6.5 * len(SHOWN_REGIMES), 8), sharey=True)
    for c, shown in enumerate(SHOWN_REGIMES):
        for r, (column, title) in enumerate([("corr_degree", "node cooperation vs degree"),
                                             ("corr_clustering", "node cooperation vs local clustering")]):
            ax = axes[r][c]
            part = table[table["regime"] == shown]
            for family, group in part.groupby("family"):
                line = group.groupby("beta")[column].mean()
                ax.plot(line.index, line.values, marker="o", markersize=3, label=family)
            ax.axhline(0, color="black", linewidth=0.5)
            ax.set_xscale("log")
            ax.set_xlabel("beta")
            ax.set_title(f"{title}, regime {shown}", fontsize=9)
            ax.set_ylabel("Spearman correlation (rep 0, mean over b, a)")
    axes[0][-1].legend(fontsize=7)
    fig.savefig(out_path("_node_level.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return table


def main():
    bm = load_bm_runs()
    print(f"{len(bm)} BM runs, {bm['graph'].nunique()} graphs")
    diagnostics(bm)
    steps(bm)
    node_level(bm)
    print("saved tables and figures in", RESULTS_DIR)


if __name__ == "__main__":
    main()
