"""Two extra checks before the paper .

1. --regimes: the async scan (async_scan.py) covered only A <= 1 and had no WS graphs.
   Same design (update_fraction 1, 0.5, 0.25, 0.1 at equal updates per player) for
     - regime A > 1 (a cooperator can never be satisfied): b {1.7, 2.0} x a {0.6, 0.7},
       graph types real, degseq, samedeg, shuffled, er, ws;
     - WS in the async scan's A <= 1 cells (b {1.5, 2.0} x a {0.2, 0.4}): WS - ER
       (clustering) pairs with the async scan's ER runs (same seeds).
   beta {1, 10, 100}, 5 reps, 10 networks: 14,400 + 2,400 = 16,800 runs (~3.5 h on 12).
2. --sequential: fully asynchronous updating, one player at a time
   (fast_model.run_bm_sequential), i.e. the update_fraction -> 0 limit. 1,500 sweeps
   (~1,500 updates per player), last 500 recorded, one sampled action per player per sweep.
   8 networks (Deezer and GitHub left out: too slow one player at a time), 6 graph types,
   beta {1, 100}, cells (b, a) = (1.5, 0.4), (2.0, 0.2) [A <= 1] and (2.0, 0.7) [A > 1],
   3 reps: 864 runs (~3.7 h on 12). The analysis puts every contrast next to its
   update_fraction = 1 and 0.1 values on the same cells and reps (from async_scan_runs.csv
   and extra_regimes_runs.csv, so run --regimes first).

Run from project root:
    python src/extra_scans.py --regimes --test            tiny version (~1 min)
    python src/extra_scans.py --sequential --test         tiny version (~1 min)
    python src/extra_scans.py --regimes --processes 12    -> results/extra_regimes_runs.csv
    python src/extra_scans.py --sequential --processes 12 -> results/extra_sequential_runs.csv
    python src/extra_scans.py --regimes --analyze         (add --test for the test runs)
    python src/extra_scans.py --sequential --analyze
Safe to stop and restart: finished runs are skipped.
"""
import csv
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy import stats

from fast_model import neighbour_matrix, run_bm, run_bm_sequential
from networks import RESULTS_DIR, load_graph, rewired_names, same_degree_groups

TEST = "--test" in sys.argv
SEQUENTIAL = "--sequential" in sys.argv
if not SEQUENTIAL and "--regimes" not in sys.argv:
    sys.exit("choose --regimes or --sequential (see the top of this file)")
EPSILON = 0.05
INITIAL_COOP = 0.5
BASE_STEPS = 1500
BASE_WINDOW = 500
ALL_TYPES = ["real", "degseq", "samedeg", "shuffled", "er", "ws"]

# (b, a) cells. A = a * b: A <= 1 cells are the async scan's; A > 1 cells are new
if SEQUENTIAL:
    NETWORKS = ["emaileu", "grqc", "facebook", "gnutella", "asinternet", "lastfm", "twitch", "astroph"]
    BETAS = [1.0, 100.0]
    CELLS_BY_TYPE = {}
    for graph_type in ALL_TYPES:
        CELLS_BY_TYPE[graph_type] = [(1.5, 0.4), (2.0, 0.2), (2.0, 0.7)]
    FRACTIONS = [0.0]  # 0 = one player at a time
    REPS = 3
    OUT_NAME = "extra_sequential"
else:
    NETWORKS = ["emaileu", "grqc", "facebook", "gnutella", "asinternet",
                "lastfm", "twitch", "astroph", "deezer", "github"]
    BETAS = [1.0, 10.0, 100.0]
    above_one = [(1.7, 0.6), (1.7, 0.7), (2.0, 0.6), (2.0, 0.7)]
    CELLS_BY_TYPE = {}
    for graph_type in ALL_TYPES:
        CELLS_BY_TYPE[graph_type] = list(above_one)
    CELLS_BY_TYPE["ws"] = CELLS_BY_TYPE["ws"] + [(1.5, 0.2), (1.5, 0.4), (2.0, 0.2), (2.0, 0.4)]
    FRACTIONS = [1.0, 0.5, 0.25, 0.1]
    REPS = 5
    OUT_NAME = "extra_regimes"
if TEST:
    NETWORKS = ["emaileu"]
    BETAS = [100.0]
    REPS = 2
    BASE_STEPS = 200
    BASE_WINDOW = 60
    if not SEQUENTIAL:
        FRACTIONS = [1.0, 0.25]
    OUT_NAME = OUT_NAME + "_test"

RUNS_PATH = os.path.join(RESULTS_DIR, OUT_NAME + "_runs.csv")
COLUMNS = ["run_id", "network", "graph_type", "update_fraction", "b", "beta", "a_fraction",
           "aspiration", "rep", "steps", "window", "cooperation", "drift", "mean_p",
           "rho_degree", "seconds"]


def processes_from_command_line():
    if "--processes" not in sys.argv:
        return 12
    position = sys.argv.index("--processes")
    if position + 1 >= len(sys.argv) or not sys.argv[position + 1].isdigit():
        sys.exit("--processes needs a whole number, e.g. --processes 4")
    return max(1, int(sys.argv[position + 1]))


def make_jobs():
    jobs = []
    for network in NETWORKS:
        for graph_type in ALL_TYPES:
            for fraction in FRACTIONS:
                for b, a_fraction in CELLS_BY_TYPE[graph_type]:
                    for beta in BETAS:
                        for rep in range(REPS):
                            job = {"network": network, "graph_type": graph_type,
                                   "update_fraction": fraction, "b": b, "beta": beta,
                                   "a_fraction": a_fraction, "rep": rep}
                            # same format as async_scan.py, so runs can be matched
                            job["run_id"] = (f"{network}|{graph_type}|f={fraction}|b={b}"
                                             f"|beta={beta}|a={a_fraction}|rep={rep}")
                            jobs.append(job)
    return jobs


def graph_file(network, graph_type, rep):
    if graph_type == "degseq":
        names = rewired_names(network)
        return names[rep % len(names)]
    if graph_type in ("er", "ws"):
        return network + "_" + graph_type
    return network  # real, samedeg, shuffled


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
    graph_type = job["graph_type"]
    aspiration = round(job["a_fraction"] * job["b"], 6)
    if SEQUENTIAL:
        steps = BASE_STEPS
        window = BASE_WINDOW
        seating = "fixed"
        if graph_type == "shuffled":
            seating = "full"
        if graph_type == "samedeg":
            seating = "samedeg"
        curve, p, node_cooperation = run_bm_sequential(
            A, degree, job["b"], job["beta"], aspiration, EPSILON, steps,
            record_from=steps - window, initial_coop=INITIAL_COOP, seating=seating,
            seat_groups=groups, seed=job["rep"])
    else:
        fraction = job["update_fraction"]
        steps = int(round(BASE_STEPS / fraction))  # equal updates per player (as async_scan)
        window = int(round(BASE_WINDOW / fraction))
        seat_groups = None
        if graph_type == "samedeg":
            seat_groups = groups
        curve, p, node_cooperation = run_bm(
            A, degree, job["b"], job["beta"], aspiration, EPSILON, steps,
            record_from=steps - window, initial_coop=INITIAL_COOP,
            shuffle_seats=graph_type in ("shuffled", "samedeg"), seat_groups=seat_groups,
            update_fraction=fraction, record_every=int(round(1 / fraction)), seed=job["rep"])
    in_window = curve[steps - window:]
    half = window // 2
    rho = ""
    if graph_type not in ("shuffled", "samedeg"):  # a node is one player only on static graphs
        rho = float(stats.spearmanr(node_cooperation, degree).statistic)
    return {"run_id": job["run_id"], "network": job["network"], "graph_type": graph_type,
            "update_fraction": job["update_fraction"], "b": job["b"], "beta": job["beta"],
            "a_fraction": job["a_fraction"], "aspiration": aspiration, "rep": job["rep"],
            "steps": steps, "window": window, "cooperation": float(in_window.mean()),
            "drift": float(in_window[half:].mean() - in_window[:half].mean()),
            "mean_p": float(p.mean()), "rho_degree": rho,
            "seconds": round(time.time() - start, 2)}


def finished_run_ids():
    done = set()
    if not os.path.exists(RUNS_PATH):
        return done
    with open(RUNS_PATH, newline="") as f:
        text = f.read()
    if text and not text.endswith("\n"):  # killed while writing: drop the cut-off line
        with open(RUNS_PATH, "w", newline="") as f:
            f.write(text[:text.rfind("\n") + 1])
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
    todo.sort(key=lambda job: (NETWORKS.index(job["network"]),
                               graph_file(job["network"], job["graph_type"], job["rep"])))
    print(f"{len(all_jobs)} runs, {len(done)} already done, {len(todo)} to go, {n_processes} processes")
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
                    print(f"  {i + 1}/{len(todo)} done, {(time.time() - start) / 60:.1f} min so far")


# ---- analysis ----------------------------------------------------------------

CONTRASTS = [("fixed partners", "real", "samedeg"),
             ("keeping one's degree", "samedeg", "shuffled"),
             ("structure beyond degree", "real", "degseq"),
             ("uneven degrees", "degseq", "er"),
             ("clustering", "ws", "er")]


def regime(row_b, row_a):
    if row_a * row_b <= 1:
        return "A<=1"
    return "A>1"


def mean_and_ci(values):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return values.mean(), np.nan
    half = stats.t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values))
    return values.mean(), half


def contrasts(runs):
    """Per network, regime, update_fraction (0 = one at a time) and beta: each contrast,
    paired by seed, mean over the regime's (b, a) cells, 95% CI over reps."""
    runs = runs.copy()
    regimes = []
    for _, row in runs.iterrows():
        regimes.append(regime(row["b"], row["a_fraction"]))
    runs["regime"] = regimes
    keys = ["network", "regime", "update_fraction", "beta", "b", "a_fraction", "rep"]
    wide = runs.pivot_table(index=keys, columns="graph_type", values="cooperation").reset_index()
    rows = []
    for name, first, second in CONTRASTS:
        if first not in wide.columns or second not in wide.columns:
            continue
        wide["difference"] = wide[first] - wide[second]
        paired = wide.dropna(subset=["difference"])
        per_rep = paired.groupby(["network", "regime", "update_fraction", "beta", "rep"],
                                 as_index=False)["difference"].mean()
        for group_keys, group in per_rep.groupby(["network", "regime", "update_fraction", "beta"]):
            mean, half = mean_and_ci(group["difference"])
            rows.append({"quantity": name, "network": group_keys[0], "regime": group_keys[1],
                         "update_fraction": group_keys[2], "beta": group_keys[3],
                         "value": mean, "ci": half, "n_reps": len(group)})
    real = runs[runs["graph_type"] == "real"]
    for group_keys, group in real.groupby(["network", "regime", "update_fraction", "beta"]):
        per_rep = group.groupby("rep")["rho_degree"].mean()
        mean, half = mean_and_ci(per_rep.values)
        rows.append({"quantity": "hubs defect (rho)", "network": group_keys[0],
                     "regime": group_keys[1], "update_fraction": group_keys[2],
                     "beta": group_keys[3], "value": mean, "ci": half, "n_reps": len(per_rep)})
    return pd.DataFrame(rows)


def read_runs(file_name):
    path = os.path.join(RESULTS_DIR, file_name)
    if not os.path.exists(path):
        print("not found (skipped):", path)
        return None
    return pd.read_csv(path)


def analyze():
    runs = read_runs(OUT_NAME + "_runs.csv")
    if runs is None:
        return
    print(f"{len(runs)} runs; |drift| > 0.01 in {(runs['drift'].abs() > 0.01).mean():.1%}")
    if SEQUENTIAL:
        # same cells and reps from the update_fraction runs, so all three columns compare
        # the same settings: 1 = lockstep, 0.1 = one in ten per round, 0 = one at a time
        test_part = "_test" if TEST else ""
        frames = [runs]
        for file_name in ["async_scan" + test_part + "_runs.csv", "extra_regimes" + test_part + "_runs.csv"]:
            other = read_runs(file_name)
            if other is not None:
                frames.append(other[other["update_fraction"].isin([1.0, 0.1])])
        combined = pd.concat(frames, ignore_index=True)
        cells = runs[["network", "graph_type", "b", "a_fraction", "beta", "rep"]].drop_duplicates()
        combined = combined.merge(cells, on=["network", "graph_type", "b", "a_fraction", "beta", "rep"])
        table = contrasts(combined)
    else:
        # WS - ER at A <= 1 needs the async scan's ER runs (same cells, seeds, fractions)
        frames = [runs]
        test_part = "_test" if TEST else ""
        async_runs = read_runs("async_scan" + test_part + "_runs.csv")
        if async_runs is not None:
            frames.append(async_runs[async_runs["graph_type"] == "er"])
        table = contrasts(pd.concat(frames, ignore_index=True))
        # keep A <= 1 only for clustering (the other A <= 1 contrasts are in async_scan)
        keep = (table["regime"] == "A>1") | (table["quantity"] == "clustering")
        table = table[keep]
    out = os.path.join(RESULTS_DIR, OUT_NAME + "_contrasts.csv")
    table.to_csv(out, index=False)
    for (quantity, shown_regime), part in table.groupby(["quantity", "regime"]):
        print()
        print(f"{quantity}, regime {shown_regime}: rows = network, columns = (beta, update_fraction);"
              f" 1 = lockstep, 0.1 = one in ten per round, 0 = one at a time")
        print(part.pivot_table(index="network", columns=["beta", "update_fraction"],
                               values="value").round(3).to_string())
    print(f"\nlargest 95% CI half-width of a contrast: {table[table['quantity'] != 'hubs defect (rho)']['ci'].max():.4f}")
    print("saved", out)


if __name__ == "__main__":
    if "--analyze" in sys.argv:
        analyze()
    else:
        run_scan()
