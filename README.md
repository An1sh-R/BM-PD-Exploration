# Experiment 1: Bush–Mosteller learners on real social networks

Weak Prisoner's Dilemma played by reinforcement learners (Bush–Mosteller, BM) on 5 real
social networks. Question: how much do fixed partners and network structure beyond the
degree sequence change cooperation, and how does that depend on learning sensitivity β?

## What was run

**Game.** Weak PD (Nowak & May 1992): R = 1, T = b, S = P = 0. Each round every player
plays one action against all its neighbours; payoff = **average** over neighbours
(in [0, b]). All players update at the same time (synchronous rounds).

**Learner.** Bush–Mosteller with aspiration (Ezaki et al. 2016; Ezaki & Masuda 2017).
Each player has a cooperation propensity p (start 0.5).

- Action: intends C with probability p; the intended action is flipped with probability ε = 0.05.
- Stimulus: s = tanh(β (payoff − A)). Satisfied if s ≥ 0.
- Update:

| Action | s ≥ 0 (satisfied) | s < 0 (unsatisfied) |
|---|---|---|
| C | p + (1 − p) s | p + p s |
| D | p − p s | p − (1 − p) s |

**Networks** (SNAP; self-loops dropped, largest component):

| Network | N | Edges | ⟨k⟩ | Max degree | Degree CV | Clustering | Assortativity |
|---|---|---|---|---|---|---|---|
| Facebook (ego-Facebook) | 4,039 | 88,234 | 43.7 | 1,045 | 1.20 | 0.61 | +0.06 |
| LastFM Asia | 7,624 | 27,806 | 7.3 | 216 | 1.58 | 0.22 | +0.02 |
| Twitch ENGB | 7,126 | 35,324 | 9.9 | 720 | 2.24 | 0.13 | −0.12 |
| Deezer Europe | 28,281 | 92,752 | 6.6 | 172 | 1.21 | 0.14 | +0.10 |
| GitHub | 37,700 | 289,003 | 15.3 | 9,458 | 5.27 | 0.17 | −0.08 |

**Three versions of each network** (15 graphs):

- `real`: the network as is.
- `degseq`: same degree for every node, links rewired at random (10·E double-edge swaps,
  then any cut-off pieces joined back, so the graph stays connected with the exact
  degree sequence). 5 independent rewirings; rep r runs on rewiring r mod 5.
- `shuffled`: the real network, but players take new random seats after every round
  (they keep their p). Same network, no fixed partners.

**Grid** (`src/run.py`): β ∈ {0.01, 0.1, 0.3, 0.6, 1, 2, 3, 5, 10, 20, 30, 100} ×
aspiration a = A/b ∈ {0, 0.1, …, 0.9} × b ∈ {1.1, 1.3, 1.5, 1.7, 2.0} × 10 reps × 15 graphs
= **90,000 runs**. 1,500 rounds; outcome = mean cooperation over the last 500.
Seed = rep, so real / degseq / shuffled runs with the same rep are paired.

**Regimes** (used to report results, `src/analyze.py`):

- `a=0`: nobody is ever unsatisfied (payoff ≥ 0 = A).
- `A<=1`: a cooperator can be satisfied (main regime).
- `A>1`: a cooperator never reaches A (max cooperator payoff = 1). Only at b ≥ 1.5.
- `dead zone` (a ≥ 0.8): nearly everyone unsatisfied every round, cooperation ≈ 0.5. Not used for claims.

β = 0.01 is not fully settled after 1,500 rounds: flagged, not used for claims.

## Analysis (`src/analyze.py`)

- **Diagnostics**: per cell, drift within the window, spread between reps, period-2
  oscillation (whole population flips C ↔ D every round, high β).
- **Paired contrasts**, per network and regime, never pooled over networks:
  - real − shuffled = effect of fixed partners
  - real − degseq = effect of structure beyond the degree sequence (clustering, communities, degree mixing)
  - 95% CI over reps (n = 10); for degseq over the 5 rewirings (n = 5).
- **Node level**: Spearman correlation of each player's cooperation with its degree and
  local clustering (real graphs, rep 0).

## Results

Numbers below: regime `A<=1` unless stated, mean over the regime's (b, a) cells, per
network. 95% CIs are ≤ 0.002 everywhere (they hold run-to-run noise only).
Tables: `results/sweep_steps.csv`, `results/sweep_node_level.csv`; figures:
`results/sweep_steps.png`, `results/sweep_node_level.png`, `results/sweep_diagnostics.png`.

**Mean cooperation** (all networks): real 0.39 at β = 0.1 → 0.49 at β = 100;
degseq 0.39 → 0.48; shuffled 0.38 → 0.44.

**1. Fixed partners help BM, more so at high β** (real − shuffled):

| Network | β = 0.1 | β = 1 | β = 3 | β = 10 | β = 100 |
|---|---|---|---|---|---|
| Facebook | +0.008 | +0.010 | +0.018 | +0.048 | +0.048 |
| LastFM | +0.010 | +0.015 | +0.033 | +0.054 | +0.058 |
| Twitch | +0.021 | +0.020 | +0.023 | +0.037 | +0.042 |
| Deezer | +0.008 | +0.012 | +0.028 | +0.048 | +0.052 |
| GitHub | +0.029 | +0.026 | +0.022 | +0.033 | +0.037 |

Positive everywhere. In `A>1` smaller (≤ +0.034), largest at β = 2. Caveat: re-seating
players also takes away each player's fixed degree, so part of this may be a degree effect.

**2. Structure beyond the degree sequence matters little** (real − degseq):

| Network | β = 0.1 | β = 1 | β = 3 | β = 10 | β = 100 |
|---|---|---|---|---|---|
| Facebook | −0.009 | −0.006 | +0.007 | +0.024 | +0.013 |
| LastFM | −0.002 | +0.002 | +0.012 | +0.016 | +0.015 |
| Twitch | +0.005 | +0.005 | +0.006 | +0.006 | +0.005 |
| Deezer | −0.000 | +0.001 | +0.007 | +0.009 | +0.009 |
| GitHub | +0.005 | +0.005 | +0.006 | +0.003 | +0.000 |

|difference| ≤ 0.009 at β ≤ 1, up to +0.024 at β ≥ 3. In `A>1`: |difference| ≤ 0.008.
This fits earlier reports that reinforcement learning is largely insensitive to network
topology (Cimini & Sánchez 2014; Amaral et al. 2016).

**3. Low-degree players cooperate more than hubs** (Spearman correlation of a player's
cooperation with its degree, real graphs):

| Network | β = 0.1 | β = 1 | β = 3 | β = 10 | β = 100 |
|---|---|---|---|---|---|
| Facebook | −0.57 | −0.63 | −0.60 | −0.03 | +0.11 |
| LastFM | −0.65 | −0.77 | −0.71 | −0.49 | −0.41 |
| Twitch | −0.57 | −0.69 | −0.67 | −0.45 | −0.37 |
| Deezer | −0.68 | −0.76 | −0.71 | −0.51 | −0.43 |
| GitHub | −0.48 | −0.62 | −0.61 | −0.37 | −0.28 |

Holds in `A<=1` (except Facebook at β ≥ 10). Reverses in `A>1` at β ≥ 3 (mean +0.05 to
+0.38: hubs cooperate more). No pattern at a = 0. Likely mechanism: a hub's averaged
payoff is close to the population average; at these aspirations cooperating then pays
a little below A (unsatisfied) and defecting pays b times more (satisfied), so hubs
drift to D. A low-degree player with one cooperating partner gets payoff 1 ≥ A and keeps
cooperating. Local clustering is mostly higher at low-degree nodes, so its correlation
is not read separately.

**Diagnostics:** 8,992 of 9,000 cells settled (8 still moving, all at β = 0.01). 12 % of
cells oscillate with period 2 (whole population flips C ↔ D each round; β ≥ 2, a ≥ 0.3);
their window mean is still reported.

## Checks

- `src/test_model.py`: unit checks of the Mesa reference model (16 checks).
- `src/check_fast_model.py`: the numpy engine used for the sweep (`fast_model.py`) against
  the Mesa reference (`model.py`): exact update rules + 20-seed run comparison
  (`results/fast_model_check.csv`).
- `src/validate_bm.py`: reproduces the qualitative results of Ezaki & Masuda 2017 (rings,
  static vs shuffled partners; `results/validate_bm.png`).
- `src/pilot.py`: coarse β × A × b scan on LastFM used to choose the grid (`results/pilot_*`).

## Changes vs the first run of this experiment

- **degseq rewirings are now connected.** The first run's rewirings left 0.1–0.9 % of
  nodes in small cut-off pieces (mostly isolated pairs, which cooperate a lot at high β).
  They are now joined back without changing any degree, and all degseq runs were redone.
  Real and shuffled runs did not change (bit-identical).
- **Analysis**: contrasts reported per network (not pooled); dead zone starts at a = 0.8
  (was 0.9); CI unit for degseq = rewiring.

## Layout and how to run

```
data/               5 real edge lists; data/synthetic/ = rewirings (generated once, fixed)
src/
  networks.py       load + clean graphs, build rewirings, topology table
  model.py          Mesa reference model (readable version of the rules)
  fast_model.py     numpy version of BM used by run.py (~10-20x faster)
  check_fast_model.py, test_model.py, validate_bm.py, pilot.py   checks (see above)
  run.py            the sweep -> results/sweep_runs.csv
  analyze.py        diagnostics, contrasts, node level -> results/sweep_*
  plot_graphs.py    network drawings -> graphs/
results/            sweep_runs.csv (all 90,000 runs), tables and figures
```

Python 3.12+ (tested on 3.14). From the project root:

```
py -3.14 -m venv .venv
.venv\Scripts\activate          (Windows; source .venv/bin/activate elsewhere)
pip install -r requirements.txt
python src/test_model.py
python src/run.py --test        tiny sweep, checks the code
python src/analyze.py
```

`python src/run.py` reruns the full sweep (~6 h on 12 cores; it skips runs already in
`results/sweep_runs.csv`, so delete or rename that file first). Per-node results
(`results/sweep_nodes/`, ~200 MB) are not in the repo; the node-level table built from
them is (`results/sweep_node_level.csv`).
