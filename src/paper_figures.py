"""Figures 1-5 of the paper draft, redrawn from the repo's result files (added 2026-10-26).

    Fig. 1  (a) cooperation by degree class, one at a time (run src/fig1_nodes.py first)
            (b) Spearman(cooperation, degree) per network, sync / f = 0.1 / one at a time
    Fig. 2  payoff of a cooperator / defector against the share of cooperating neighbours
    Fig. 3  degree heterogeneity (rewired - ER), beta = 10, sync vs f = 0.1, A <= 1 and A > 1
    Fig. 4  A > 1: Spearman(cooperation, degree) against the update fraction
    Fig. 5  A <= 1, beta = 100: fixed partners, clustering, structure beyond degree against
            the update fraction, down to one player at a time

Run from project root: python src/paper_figures.py   -> researchP/figures/fig1.pdf ... fig5.pdf
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from networks import RESULTS_DIR

OUT_DIR = os.path.join(os.path.dirname(RESULTS_DIR), "researchP", "figures")
GREY = "#9a9a9a"
BLUE = "#1f5fbf"
RED = "#c0392b"

# display names, in the order the draft used
NAMES = {"deezer": "Deezer", "github": "GitHub", "gnutella": "Gnutella", "lastfm": "LastFM",
         "twitch": "Twitch", "asinternet": "as20000102", "astroph": "ca-AstroPh",
         "grqc": "ca-GrQc", "facebook": "ego-Facebook", "emaileu": "email-Eu"}
ORDER = ["deezer", "github", "gnutella", "lastfm", "twitch", "asinternet", "astroph", "grqc",
         "facebook", "emaileu"]

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(OUT_DIR, name), bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def figure_1():
    """(a) cooperation by degree class, one at a time (data: fig1_nodes.py);
    (b) Spearman(cooperation, degree) per network: sync, f = 0.1, one at a time,
    same cells and reps (extra_sequential_contrasts.csv), with 95% CIs over runs."""
    classes = pd.read_csv(os.path.join(RESULTS_DIR, "fig1_degree_classes.csv"))
    contrasts = pd.read_csv(os.path.join(RESULTS_DIR, "extra_sequential_contrasts.csv"))
    fig, (left, right) = plt.subplots(1, 2, figsize=(7.5, 2.9))

    styles = {("lastfm", 1.0): (BLUE, "-"), ("lastfm", 100.0): (BLUE, ":"),
              ("grqc", 1.0): ("#333333", "-"), ("grqc", 100.0): ("#333333", ":")}
    labels = {"lastfm": "LastFM", "grqc": "ca-GrQc"}
    for (network, beta), (color, line) in styles.items():
        part = classes[(classes["network"] == network) & (classes["beta"] == beta)]
        part = part[part["players"] >= 5]  # top classes with a handful of hubs are noise
        left.plot(part["class_lower_degree"], part["cooperation"], color=color, linestyle=line,
                  marker="o", markersize=3, label=f"{labels[network]}, β = {beta:g}")
    left.set_xscale("log", base=2)
    left.set_xlabel("degree (lower edge of factor-2 class)")
    left.set_ylabel("cooperation")
    left.set_title("(a) cooperation by degree, one at a time")
    left.legend(frameon=False, fontsize=7)

    rho = contrasts[(contrasts["quantity"] == "hubs defect (rho)") & (contrasts["regime"] == "A<=1")]
    networks = ["emaileu", "facebook", "grqc", "astroph", "asinternet", "twitch", "lastfm", "gnutella"]
    schemes = [(1.0, "sync", "#a6a6a6"), (0.1, "f = 0.1", "#8fb3e8"), (0.0, "one at a time", BLUE)]
    for j, (fraction, label, color) in enumerate(schemes):
        for beta, marker in [(1.0, "o"), (100.0, "s")]:
            part = rho[(rho["update_fraction"] == fraction) & (rho["beta"] == beta)]
            values = []
            errors = []
            for network in networks:
                row = part[part["network"] == network]
                values.append(row["value"].iloc[0])
                errors.append(row["ci"].iloc[0])
            positions = np.arange(len(networks)) + (j - 1) * 0.22
            legend_label = label if beta == 1.0 else None
            right.errorbar(values, positions, xerr=errors, fmt=marker, color=color, markersize=4,
                           elinewidth=0.8, capsize=0, label=legend_label)
    right.axvline(0, color="black", linewidth=0.8)
    right.set_yticks(np.arange(len(networks)))
    right.set_yticklabels([NAMES[n] for n in networks])
    right.set_xlabel("Spearman ρ (cooperation, degree)")
    right.set_title("(b) ρ per network: ● β = 1, ■ β = 100")
    right.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    fig.tight_layout()
    save(fig, "fig1.pdf")


def figure_2():
    """The band: a <= x < a*b is where cooperating is unsatisfying and defecting satisfying.
    At A > 1 it becomes x >= a (a cooperator is never satisfied)."""
    x = np.linspace(0, 1, 200)
    b = 2.0
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.8), sharey=True)
    for ax, a in zip(axes, [0.4, 0.7]):
        aspiration = a * b
        band_end = min(a * b, 1.0)
        ax.axvspan(a, band_end, color="#e6e6e6")
        ax.plot(x, x, color=BLUE, label="cooperate: r = x")
        ax.plot(x, b * x, color="black", linestyle="--", label="defect: r = bx")
        ax.axhline(aspiration, color="black", linewidth=0.8, label="aspiration A")
        label_x = (a + band_end) / 2
        ax.text(label_x, 0.25, "band:\nC unsatisfied,\nD satisfied", ha="center", fontsize=7)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 2.05)
        ax.set_xlabel("share of cooperating neighbours, x")
        relation = "≤" if aspiration <= 1 else ">"
        ax.set_title(f"b = 2, a = {a}: A = {aspiration:.1f} {relation} 1")
    axes[0].set_ylabel("average payoff r")
    axes[1].legend(loc="upper left", frameon=False, fontsize=7)
    save(fig, "fig2.pdf")


def figure_3():
    """rewired - ER at beta = 10: A <= 1 from the async scan, A > 1 from --regimes."""
    async_table = pd.read_csv(os.path.join(RESULTS_DIR, "async_scan_contrasts.csv"))
    regimes = pd.read_csv(os.path.join(RESULTS_DIR, "extra_regimes_contrasts.csv"))
    series = [("A ≤ 1, sync", async_table, None, 1.0, "#a6a6a6"),
              ("A ≤ 1, f = 0.1", async_table, None, 0.1, BLUE),
              ("A > 1, sync", regimes, "A>1", 1.0, "#e8a49c"),
              ("A > 1, f = 0.1", regimes, "A>1", 0.1, RED)]
    fig, ax = plt.subplots(figsize=(7, 2.8))
    width = 0.2
    for i, (label, table, regime, fraction, color) in enumerate(series):
        part = table[(table["quantity"] == "uneven degrees") & (table["beta"] == 10.0)
                     & (table["update_fraction"] == fraction)]
        if regime is not None:
            part = part[part["regime"] == regime]
        values = []
        errors = []
        for network in ORDER:
            row = part[part["network"] == network]
            values.append(row["value"].iloc[0])
            errors.append(row["ci"].iloc[0])
        positions = np.arange(len(ORDER)) + (i - 1.5) * width
        ax.bar(positions, values, width, yerr=errors, color=color, label=label,
               error_kw={"elinewidth": 0.6, "capsize": 0})
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(np.arange(len(ORDER)))
    ax.set_xticklabels([NAMES[n] for n in ORDER], rotation=30, ha="right")
    ax.set_ylabel("rewired − ER cooperation")
    ax.legend(ncol=4, frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.32))
    save(fig, "fig3.pdf")


def figure_4():
    """A > 1, Spearman(cooperation, degree) against f; grey = networks, blue = median."""
    regimes = pd.read_csv(os.path.join(RESULTS_DIR, "extra_regimes_contrasts.csv"))
    rho = regimes[(regimes["quantity"] == "hubs defect (rho)") & (regimes["regime"] == "A>1")]
    fractions = [1.0, 0.5, 0.25, 0.1]
    fig, axes = plt.subplots(1, 3, figsize=(7, 2.4), sharey=True)
    for ax, beta in zip(axes, [1.0, 10.0, 100.0]):
        part = rho[rho["beta"] == beta]
        table = part.pivot_table(index="network", columns="update_fraction", values="value")
        for network in table.index:
            ax.plot(range(4), [table.loc[network, f] for f in fractions], color=GREY, linewidth=0.7)
        ax.plot(range(4), [table[f].median() for f in fractions], color=BLUE, marker="o",
                linewidth=1.8, markersize=3)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(range(4))
        ax.set_xticklabels(["1\n(sync)", "0.5", "0.25", "0.1"])
        ax.set_xlabel("update fraction f")
        ax.set_title(f"β = {beta:g}")
    axes[0].set_ylabel("Spearman ρ (cooperation, degree)")
    save(fig, "fig4.pdf")


def pair_differences(runs, first, second):
    """first - second per network and update fraction, paired by (b, a, beta, rep),
    then averaged over cells and reps."""
    keys = ["network", "update_fraction", "beta", "b", "a_fraction", "rep"]
    wide = runs.pivot_table(index=keys, columns="graph_type", values="cooperation").reset_index()
    wide["difference"] = wide[first] - wide[second]
    wide = wide.dropna(subset=["difference"])
    return wide.groupby(["network", "update_fraction"])["difference"].mean()


def figure_5():
    """A <= 1, beta = 100, cells (1.5, 0.4) and (2.0, 0.2): sync -> f -> one at a time."""
    cells = [(1.5, 0.4), (2.0, 0.2)]
    async_runs = pd.read_csv(os.path.join(RESULTS_DIR, "async_scan_runs.csv"))
    regimes = pd.read_csv(os.path.join(RESULTS_DIR, "extra_regimes_runs.csv"))
    sequential = pd.read_csv(os.path.join(RESULTS_DIR, "extra_sequential_runs.csv"))
    frames = []
    for runs in [async_runs, regimes[regimes["graph_type"] == "ws"], sequential]:
        keep = runs["beta"] == 100.0
        in_cells = np.zeros(len(runs), dtype=bool)
        for b, a in cells:
            in_cells = in_cells | ((runs["b"] == b) & (runs["a_fraction"] == a)).values
        frames.append(runs[keep.values & in_cells][["network", "graph_type", "update_fraction",
                                                     "beta", "b", "a_fraction", "rep", "cooperation"]])
    runs = pd.concat(frames, ignore_index=True)
    panels = [("(a) fixed partners\nreal − same-degree", "real", "samedeg"),
              ("(b) clustering\nWS − ER", "ws", "er"),
              ("(c) structure beyond degree\nreal − rewired", "real", "degseq")]
    fractions = [1.0, 0.5, 0.25, 0.1, 0.0]  # 0 = one at a time
    fig, axes = plt.subplots(1, 3, figsize=(7, 2.6), sharey=True)
    for ax, (title, first, second) in zip(axes, panels):
        differences = pair_differences(runs, first, second)
        medians = []
        for f in fractions:
            medians.append(differences.xs(f, level="update_fraction").median())
        for network in ORDER:
            xs = []
            ys = []
            for i, f in enumerate(fractions):
                if (network, f) in differences.index:
                    xs.append(i)
                    ys.append(differences[(network, f)])
            ax.plot(xs, ys, color=GREY, linewidth=0.7)
        ax.plot(range(len(fractions)), medians, color=BLUE, marker="o", linewidth=1.8,
                markersize=3, label="median over networks")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(range(len(fractions)))
        ax.set_xticklabels(["1\n(sync)", "0.5", "0.25", "0.1", "one at\na time"])
        ax.set_xlabel("update fraction f")
        ax.set_title(title)
    axes[0].set_ylabel("difference in cooperation")
    axes[0].legend(frameon=False, fontsize=7)
    save(fig, "fig5.pdf")


if __name__ == "__main__":
    figure_1()
    figure_2()
    figure_3()
    figure_4()
    figure_5()
