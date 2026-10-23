"""Async scan: do the network effects survive when players stop learning in lockstep?

The desync sweep (update_fraction = 0.5) halved most
high-beta effects. A spot check then showed the fixed-partner effect keeps shrinking
towards 0 as update_fraction falls (0.1 = nearly one player at a time), while hub
defection and the degree effects stay. This script tests that on all 10 networks.

Each run uses update_fraction f with 1500 / f rounds (window 500 / f), so every
player gets the same number of updates (~1500) whatever f is: a smaller f only
removes the lockstep, not learning time.

Grid: 10 networks x 5 graph types (real, degseq, samedeg, shuffled, er)
      x update_fraction {1, 0.5, 0.25, 0.1} x beta {1, 10, 100} x a {0.2, 0.4}
      x b {1.5, 2.0} x 5 reps = 12,000 runs (all in regime A <= 1; was written as 24,000).
Small f means long runs (f = 0.1 -> 15,000 rounds). Each round costs the same whatever f
is, so per setting the four fractions cost 1 + 2 + 4 + 10 = 17 normal runs: 3,000 settings x 17
= about 51,000 normal 1,500-round runs in total (~2.5-3.5 h on 12 processes).


Safe to stop and restart: finished runs are skipped.

Mentor's script (received 2026-10-23); changed here before any run, same grid and runs:
node cooperation sampled every 1/f rounds (fast_model record_every), extra columns
drift, mean_p, cooperation_1000_1500, run count corrected to 12,000. See ResearchQ/design.md.
"""
import csv
import os
import sys
import time
from multiprocessing import Pool

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from fast_model import neighbour_matrix, run_bm
from networks import RESULTS_DIR, load_graph, rewired_names, same_degree_groups

TEST = "--test" in sys.argv

GRAPH_TYPES = ["real", "degseq", "samedeg", "shuffled", "er"]
if TEST:
    NETWORKS = ["emaileu"]
    FRACTIONS = [1.0, 0.25]
    BETAS = [1.0, 100.0]
    A_FRACTIONS = [0.4]
    TEMPTATIONS = [1.5]
    REPS = 2
    BASE_STEPS = 300
    BASE_WINDOW = 100
    OUT_NAME = "async_scan_test"
else:
    # small and cheap networks first
    NETWORKS = ["emaileu", "grqc", "facebook", "gnutella", "asinternet",
                "lastfm", "twitch", "astroph", "deezer", "github"]
    FRACTIONS = [1.0, 0.5, 0.25, 0.1]
    BETAS = [1.0, 10.0, 100.0]
    A_FRACTIONS = [0.2, 0.4]  # A = a * b <= 1 for both b: main regime only
    TEMPTATIONS = [1.5, 2.0]
    REPS = 5  # rep r runs on rewiring r for degseq: 5 reps = 5 rewirings
    BASE_STEPS = 1500
    BASE_WINDOW = 500
    OUT_NAME = "async_scan"

EPSILON = 0.05
INITIAL_COOP = 0.5
RUNS_PATH = os.path.join(RESULTS_DIR, OUT_NAME + "_runs.csv")
# drift, mean_p, cooperation_1000_1500 added 2026-10-23 (before any run): drift and mean_p
# check that long runs settled; cooperation_1000_1500 = mean cooperation in rounds
# 1000-1499, which at f = 0.5 must equal the desync sweep's value exactly (same seed, so
# the desync run is the first 1,500 rounds of this run)
COLUMNS = ["run_id", "network", "graph_type", "update_fraction", "b", "beta", "a_fraction",
           "aspiration", "rep", "steps", "window", "cooperation", "even_odd_gap",
           "drift", "mean_p", "cooperation_1000_1500", "rho_degree", "seconds"]


def processes_from_command_line():
    if "--processes" not in sys.argv:
        return 12
    position = sys.argv.index("--processes")
    if position + 1 >= len(sys.argv) or not sys.argv[position + 1].isdigit():
        sys.exit("--processes needs a whole number, e.g. --processes 4")
    return max(1, int(sys.argv[position + 1]))


def make_run_id(job):
    return (f"{job['network']}|{job['graph_type']}|f={job['update_fraction']}|b={job['b']}"
            f"|beta={job['beta']}|a={job['a_fraction']}|rep={job['rep']}")


def make_jobs():
    jobs = []
    for network in NETWORKS:
        for graph_type in GRAPH_TYPES:
            for fraction in FRACTIONS:
                for b in TEMPTATIONS:
                    for beta in BETAS:
                        for a_fraction in A_FRACTIONS:
                            for rep in range(REPS):
                                job = {"network": network, "graph_type": graph_type,
                                       "update_fraction": fraction, "b": b, "beta": beta,
                                       "a_fraction": a_fraction, "rep": rep}
                                job["run_id"] = make_run_id(job)
                                jobs.append(job)
    return jobs


def graph_file(network, graph_type, rep):
    """degseq: rep r uses rewiring r % 5 (as in run.py). shuffled/samedeg: the real graph."""
    if graph_type == "degseq":
        names = rewired_names(network)
        return names[rep % len(names)]
    if graph_type == "er":
        return network + "_er"
    return network


# each worker keeps the last graph it loaded (jobs are sorted by graph file)
cached_file = None
cached = None


def get_graph(file_name):
    global cached_file, cached
    if file_name != cached_file:
        G = load_graph(file_name)
        A, degree = neighbour_matrix(G)
        cached = (A, degree, same_degree_groups(G))
        cached_file = file_name
    return cached


def run_one(job):
    start = time.time()
    A, degree, groups = get_graph(graph_file(job["network"], job["graph_type"], job["rep"]))
    fraction = job["update_fraction"]
    # same number of updates per player for every fraction (see module docstring)
    steps = int(round(BASE_STEPS / fraction))
    window = int(round(BASE_WINDOW / fraction))
    shuffle = job["graph_type"] in ("shuffled", "samedeg")
    seat_groups = None
    if job["graph_type"] == "samedeg":
        seat_groups = groups
    aspiration = round(job["a_fraction"] * job["b"], 6)
    # node cooperation from every (1/f)-th round only: ~500 actions per player at every f.
    # Averaging all 500/f window rounds would make it less noisy at small f, and less
    # noise alone makes Spearman(cooperation, degree) look stronger (added 2026-10-23)
    record_every = int(round(1 / fraction))
    curve, p, node_cooperation = run_bm(A, degree, job["b"], job["beta"], aspiration, EPSILON,
                                        steps, record_from=steps - window,
                                        initial_coop=INITIAL_COOP, shuffle_seats=shuffle,
                                        seat_groups=seat_groups, update_fraction=fraction,
                                        record_every=record_every, seed=job["rep"])
    in_window = curve[steps - window:]
    half = window // 2
    cooperation_1000_1500 = np.nan  # --test runs are shorter than 1,500 rounds
    if steps >= 1500:
        cooperation_1000_1500 = float(curve[1000:1500].mean())
    # hub defection (C1): only meaningful where a node is one player (static graphs)
    rho = ""
    if not shuffle:
        rho = float(stats.spearmanr(node_cooperation, degree).statistic)
    return {"run_id": job["run_id"], "network": job["network"], "graph_type": job["graph_type"],
            "update_fraction": fraction, "b": job["b"], "beta": job["beta"],
            "a_fraction": job["a_fraction"], "aspiration": aspiration, "rep": job["rep"],
            "steps": steps, "window": window, "cooperation": float(in_window.mean()),
            "even_odd_gap": float(abs(in_window[0::2].mean() - in_window[1::2].mean())),
            "drift": float(in_window[half:].mean() - in_window[:half].mean()),
            "mean_p": float(p.mean()),
            "cooperation_1000_1500": cooperation_1000_1500,
            "rho_degree": rho, "seconds": round(time.time() - start, 2)}


def finished_run_ids():
    done = set()
    if not os.path.exists(RUNS_PATH):
        return done
    with open(RUNS_PATH, newline="") as f:
        text = f.read()
    if text and not text.endswith("\n"):  # killed while writing: drop the cut-off line
        text = text[:text.rfind("\n") + 1]
        with open(RUNS_PATH, "w", newline="") as f:
            f.write(text)
    with open(RUNS_PATH, newline="") as f:
        for row in csv.DictReader(f):
            done.add(row["run_id"])
    return done


def run_scan():
    n_processes = processes_from_command_line()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_jobs = make_jobs()
    done = finished_run_ids()
    todo = []
    for job in all_jobs:
        if job["run_id"] not in done:
            todo.append(job)
    # long runs (small fraction) spread out; same graph file next to each other
    todo.sort(key=lambda job: (NETWORKS.index(job["network"]),
                               graph_file(job["network"], job["graph_type"], job["rep"])))
    print(f"{len(all_jobs)} runs in scan, {len(done)} already done, {len(todo)} to go, "
          f"{n_processes} processes")
    if not todo:
        return
    new_file = not os.path.exists(RUNS_PATH)
    start = time.time()
    with open(RUNS_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        with Pool(n_processes) as pool:
            for i, row in enumerate(pool.imap_unordered(run_one, todo)):
                writer.writerow(row)
                f.flush()
                if (i + 1) % 20 == 0 or i + 1 == len(todo):
                    os.fsync(f.fileno())
                    minutes = (time.time() - start) / 60
                    print(f"  {i + 1}/{len(todo)} done, {minutes:.1f} min so far")


# ---- analysis ----------------------------------------------------------------

CONTRASTS = [("fixed partners", "real", "samedeg"),
             ("keeping one's degree", "samedeg", "shuffled"),
             ("structure beyond degree", "real", "degseq"),
             ("uneven degrees", "degseq", "er")]


def mean_and_ci(values):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return values.mean(), np.nan
    half = stats.t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values))
    return values.mean(), half


def analyze():
    runs = pd.read_csv(RUNS_PATH)
    print(f"{len(runs)} runs")
    keys = ["network", "update_fraction", "beta", "b", "a_fraction", "rep"]
    wide = runs.pivot_table(index=keys, columns="graph_type", values="cooperation").reset_index()
    rows = []
    for name, first, second in CONTRASTS:
        if first not in wide.columns or second not in wide.columns:
            continue
        wide["difference"] = wide[first] - wide[second]
        paired = wide.dropna(subset=["difference"])
        # per rep: mean over the (b, a) cells; reps are the independent units
        # (for degseq each rep is its own rewiring)
        per_rep = paired.groupby(["network", "update_fraction", "beta", "rep"],
                                 as_index=False)["difference"].mean()
        for (network, fraction, beta), group in per_rep.groupby(["network", "update_fraction", "beta"]):
            mean, half = mean_and_ci(group["difference"])
            rows.append({"quantity": name, "network": network, "update_fraction": fraction,
                         "beta": beta, "value": mean, "ci": half, "n_reps": len(group)})
    # hub defection: Spearman(node cooperation, degree) on the real graph, mean over cells and reps
    real = runs[runs["graph_type"] == "real"]
    for (network, fraction, beta), group in real.groupby(["network", "update_fraction", "beta"]):
        per_rep = group.groupby("rep")["rho_degree"].mean()
        mean, half = mean_and_ci(per_rep.values)
        rows.append({"quantity": "hubs defect (rho)", "network": network,
                     "update_fraction": fraction, "beta": beta, "value": mean, "ci": half,
                     "n_reps": len(per_rep)})
    table = pd.DataFrame(rows)
    table.to_csv(os.path.join(RESULTS_DIR, OUT_NAME + "_contrasts.csv"), index=False)

    quantities = [name for name, first, second in CONTRASTS] + ["hubs defect (rho)"]
    for quantity in quantities:
        part = table[table["quantity"] == quantity]
        if len(part) == 0:
            continue
        print()
        print(f"{quantity}: rows = network, columns = (beta, update_fraction); "
              f"update_fraction 1 = synchronous, 0.1 = nearly one player at a time")
        shown = part.pivot_table(index="network", columns=["beta", "update_fraction"], values="value")
        print(shown.round(3).to_string())
    max_ci = table[table["quantity"] != "hubs defect (rho)"]["ci"].max()
    print(f"\nlargest 95% CI half-width of a contrast: {max_ci:.4f}")

    betas = sorted(table["beta"].unique())
    fig, axes = plt.subplots(len(quantities), len(betas),
                             figsize=(4.2 * len(betas), 3.2 * len(quantities)), squeeze=False)
    fig.subplots_adjust(hspace=0.55, wspace=0.3)
    for r, quantity in enumerate(quantities):
        for c, beta in enumerate(betas):
            ax = axes[r][c]
            part = table[(table["quantity"] == quantity) & (table["beta"] == beta)]
            for network, line in part.groupby("network"):
                line = line.sort_values("update_fraction")
                ax.errorbar(line["update_fraction"], line["value"], yerr=line["ci"],
                            marker="o", markersize=3, capsize=2, label=network)
            ax.axhline(0, color="black", linewidth=0.5)
            ax.set_xscale("log")
            ax.set_xlabel("update_fraction (1 = synchronous)")
            ax.set_title(f"{quantity}, beta = {beta:g}", fontsize=9)
    axes[0][-1].legend(fontsize=7)
    fig.suptitle("Async scan, regime A <= 1: effects as players stop learning in lockstep "
                 "(same number of updates per player)")
    fig.savefig(os.path.join(RESULTS_DIR, OUT_NAME + "_contrasts.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", os.path.join(RESULTS_DIR, OUT_NAME + "_contrasts.csv"), "and .png")


if __name__ == "__main__":
    if "--analyze" in sys.argv:
        analyze()
    else:
        run_scan()
