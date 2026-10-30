"""Per-player cooperation by degree, one player at a time, for Fig. 1a of the paper draft
(added 2026-10-30).

The sequential runs of extra_scans.py store only Spearman(cooperation, degree), not each
player's cooperation. This reruns their real-graph runs on LastFM and ca-GrQc
(beta = 1, 100; cells (b, a) = (1.5, 0.4), (2.0, 0.2); reps 0-2; same seeds), checks that
cooperation and rho equal results/extra_sequential_runs.csv exactly, and saves mean
cooperation per factor-2 degree class. Cooperation = sampled actions over the last 500
sweeps (one per player per sweep), as in extra_scans.py, not p.

Run from project root: python src/fig1_nodes.py   (24 runs, a few minutes on 12 processes)
Writes results/fig1_degree_classes.csv and results/fig1_hubs.csv
"""
import os
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy import stats

from fast_model import neighbour_matrix, run_bm_sequential
from networks import RESULTS_DIR, load_graph

NETWORKS = ["lastfm", "grqc"]
BETAS = [1.0, 100.0]
CELLS = [(1.5, 0.4), (2.0, 0.2)]
REPS = 3
EPSILON = 0.05
INITIAL_COOP = 0.5
SWEEPS = 1500
WINDOW = 500
HUB_SHARE = 0.01  # top 1% by degree, as band_test.py


def run_one(job):
    network, beta, b, a_fraction, rep = job
    A, degree = neighbour_matrix(load_graph(network))
    aspiration = round(a_fraction * b, 6)
    curve, p, node_cooperation = run_bm_sequential(
        A, degree, b, beta, aspiration, EPSILON, SWEEPS, record_from=SWEEPS - WINDOW,
        initial_coop=INITIAL_COOP, seating="fixed", seed=rep)
    rho = float(stats.spearmanr(node_cooperation, degree).statistic)
    return {"job": job, "cooperation": float(curve[SWEEPS - WINDOW:].mean()), "rho": rho,
            "degree": degree, "node_cooperation": node_cooperation}


def main():
    jobs = []
    for network in NETWORKS:
        for beta in BETAS:
            for b, a_fraction in CELLS:
                for rep in range(REPS):
                    jobs.append((network, beta, b, a_fraction, rep))
    with Pool(12) as pool:
        results = pool.map(run_one, jobs)

    # same runs as extra_scans.py --sequential: must match exactly
    old = pd.read_csv(os.path.join(RESULTS_DIR, "extra_sequential_runs.csv"),
                      float_precision="round_trip")
    old = old[old["graph_type"] == "real"]
    for result in results:
        network, beta, b, a_fraction, rep = result["job"]
        row = old[(old["network"] == network) & (old["beta"] == beta) & (old["b"] == b)
                  & (old["a_fraction"] == a_fraction) & (old["rep"] == rep)]
        assert len(row) == 1, result["job"]
        assert row["cooperation"].iloc[0] == result["cooperation"], result["job"]
        assert row["rho_degree"].iloc[0] == result["rho"], result["job"]
    print("all", len(results), "runs equal extra_sequential_runs.csv")

    class_rows = []
    hub_rows = []
    for network in NETWORKS:
        for beta in BETAS:
            mine = [r for r in results if r["job"][0] == network and r["job"][1] == beta]
            degree = mine[0]["degree"]
            # mean over the 2 cells x 3 reps, per player
            cooperation = np.mean([r["node_cooperation"] for r in mine], axis=0)
            degree_class = np.floor(np.log2(degree)).astype(int)
            for k in sorted(set(degree_class)):
                members = degree_class == k
                class_rows.append({"network": network, "beta": beta, "class_lower_degree": 2 ** k,
                                   "players": int(members.sum()),
                                   "cooperation": float(cooperation[members].mean())})
            n_hubs = max(10, round(HUB_SHARE * len(degree)))
            hubs = np.argsort(degree)[::-1][:n_hubs]
            hub_rows.append({"network": network, "beta": beta,
                             "top1pct_cooperation": float(cooperation[hubs].mean()),
                             "degree1_cooperation": float(cooperation[degree == 1].mean()),
                             "degree1_players": int((degree == 1).sum())})
    pd.DataFrame(class_rows).to_csv(os.path.join(RESULTS_DIR, "fig1_degree_classes.csv"), index=False)
    hubs_table = pd.DataFrame(hub_rows)
    hubs_table.to_csv(os.path.join(RESULTS_DIR, "fig1_hubs.csv"), index=False)
    print(hubs_table.round(3).to_string())
    print("saved results/fig1_degree_classes.csv, results/fig1_hubs.csv")


if __name__ == "__main__":
    main()
