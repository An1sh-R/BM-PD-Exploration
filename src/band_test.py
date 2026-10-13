"""C1 mechanism, test 1 (band test). No new runs: uses rep-0 node files of the real graphs.

Band rule (averaged payoffs, x = share of a player's neighbours who cooperate):
a cooperator earns x and is satisfied iff x >= a*b; a defector earns b*x and is
satisfied iff x >= a. If a <= x < a*b, cooperating disappoints and defecting satisfies.
A hub's x stays near its neighbourhood mean, so a hub can sit in that band for good;
a low-degree player's x jumps around and often lands above a*b.

Per cell: x_hub = mean over the top-1% degree nodes of their neighbours' cooperation.
Band position: "below" (x_hub < a), "band" (a <= x_hub < a*b), "above" (x_hub >= a*b).
Prediction (written in design.md before running): Spearman(cooperation, degree) clearly
negative in band cells, near 0 in above and below cells.

Run from project root:  python src/band_test.py
Writes results/band_test.csv (one row per cell)
"""
import os

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

from analyze import DEAD_ZONE_A, OSCILLATION_LIMIT, SLOW_BETA, node_file_name, regime
from networks import REAL_FILES, RESULTS_DIR, load_graph

HUB_SHARE = 0.01  # top 1% by degree
MIN_HUBS = 10  # emaileu has 986 nodes: 1% would be ~10 anyway
STRONG = -0.1  # rho below this counts as "hubs clearly defect"
NODE_DIRS = [os.path.join(RESULTS_DIR, "sweep_nodes"), os.path.join(RESULTS_DIR, "sweep_more_nodes")]


def load_rep0_real_runs():
    """Rep-0 runs of the 10 real graphs from both sweep CSVs."""
    parts = []
    for name in ["sweep_runs.csv", "sweep_more_runs.csv"]:
        runs = pd.read_csv(os.path.join(RESULTS_DIR, name), dtype={"beta": str, "a_fraction": str})
        keep = runs["graph"].isin(list(REAL_FILES)) & (runs["rep"] == 0) & (runs["agent"] == "bm")
        parts.append(runs[keep])
    runs = pd.concat(parts, ignore_index=True)
    runs["beta"] = runs["beta"].astype(float)
    runs["a_fraction"] = runs["a_fraction"].astype(float)
    return runs


def find_node_file(run_id):
    for nodes_dir in NODE_DIRS:
        path = os.path.join(nodes_dir, node_file_name(run_id))
        if os.path.exists(path):
            return path
    return None


def band_position(x, a, b):
    if x < a:
        return "below"
    if x < a * b:
        return "band"
    return "above"


def cell_rows(family, runs):
    G = load_graph(family)
    n = G.number_of_nodes()
    # same node order as fast_model (nodes 0..n-1)
    A = nx.to_scipy_sparse_array(G, nodelist=range(n), format="csr", dtype=float)
    degree = np.asarray(A.sum(axis=1)).ravel()
    n_hubs = max(MIN_HUBS, round(HUB_SHARE * n))
    hubs = np.argsort(degree)[::-1][:n_hubs]

    rows = []
    for _, run in runs.iterrows():
        path = find_node_file(run["run_id"])
        if path is None:
            continue
        coop = np.load(path).astype(float)
        # x each node sees = mean cooperation of its neighbours (time-averaged)
        neighbour_coop = (A @ coop) / degree
        x_hub = neighbour_coop[hubs].mean()
        a = run["a_fraction"]
        b = run["b"]
        rows.append({
            "family": family, "b": b, "beta": run["beta"], "a_fraction": a,
            "regime": regime(a, b),
            "x_hub": x_hub,
            "position": band_position(x_hub, a, b),
            "cooperation": run["cooperation"],
            "hub_cooperation": coop[hubs].mean(),
            "corr_degree": stats.spearmanr(coop, degree).statistic,
            "oscillating": abs(run["even_odd_gap"]) > OSCILLATION_LIMIT,
        })
    return rows


def summary(table, title):
    print()
    print(title)
    groups = table.groupby(["family", "position"])
    out = pd.DataFrame({
        "cells": groups.size(),
        "median_rho": groups["corr_degree"].median(),
        "share_rho_below_-0.1": groups["corr_degree"].apply(lambda r: (r < STRONG).mean()),
    })
    print(out.round(2).unstack("position").to_string())


def main():
    runs = load_rep0_real_runs()
    rows = []
    for family in REAL_FILES:
        rows = rows + cell_rows(family, runs[runs["graph"] == family])
        print(f"done {family}")
    table = pd.DataFrame(rows)
    table.to_csv(os.path.join(RESULTS_DIR, "band_test.csv"), index=False)

    # main view: claim-usable cells (reporting rules), not oscillating
    usable = table[(table["a_fraction"] < DEAD_ZONE_A) & (table["beta"] != SLOW_BETA)]
    print(f"\n{len(table)} cells; {len(usable)} usable (no dead zone, no beta={SLOW_BETA:g}); "
          f"{usable['oscillating'].sum()} of those oscillate")
    summary(usable[~usable["oscillating"]], "NOT OSCILLATING: Spearman(cooperation, degree) by band position")
    summary(usable[usable["oscillating"]], "OSCILLATING (time-averaged x hides round-to-round x)")

    for reg in ["A<=1", "A>1"]:
        part = usable[(usable["regime"] == reg) & ~usable["oscillating"]]
        pivot = part.pivot_table(index="position", columns="beta", values="corr_degree", aggfunc="median")
        counts = part.pivot_table(index="position", columns="beta", values="corr_degree", aggfunc="size")
        print(f"\n{reg}, not oscillating, all networks: median rho (cells) by beta")
        print(pivot.round(2).to_string())
        print(counts.to_string())


if __name__ == "__main__":
    main()
