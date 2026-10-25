# Bush–Mosteller learners on real networks

Weak Prisoner's Dilemma played by reinforcement learners (Bush–Mosteller, BM) on real
networks. Question: how much do fixed partners and network structure beyond the
degree sequence change cooperation, and how does that depend on learning sensitivity β?
Experiment 1 (below) used 5 networks; the extension (further down) adds 5 more and
same-degree shuffle, ER, BA and WS versions of all 10. Three later checks (desynchronised
updates, async scan, extra scans incl. one player at a time) show that the high-β
fixed-partner, clustering and structure effects in these sections come from all players
updating at the same moment; without it only degrees matter consistently (hubs defect,
uneven degrees help when a cooperator can be satisfied). Current claims: `ResearchQ/question.md`.

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

Holds in `A<=1` (except Facebook at β ≥ 10). Reverses in `A>1` at high β (hubs cooperate more; first
positive at β = 2 Facebook, 3 GitHub and Twitch, 5 Deezer and LastFM). At a = 0 only a dip
around β = 1 (to −0.30). Likely mechanism: a hub's averaged
payoff is close to the population average; at these aspirations cooperating then pays
a little below A (unsatisfied) and defecting pays b times more (satisfied), so hubs
drift to D. A low-degree player with one cooperating partner gets payoff 1 ≥ A and keeps
cooperating. Local clustering is mostly higher at low-degree nodes, so its correlation
is not read separately.

**Diagnostics:** 8,992 of 9,000 cells settled (8 still moving, all at β = 0.01). 12 % of
cells oscillate with period 2 (whole population flips C ↔ D each round; β ≥ 2, a ≥ 0.3);
their window mean is still reported.

## Extension: 10 networks, 7 graph types (2026-10-13)

Do the three results hold on networks unlike the first 5, and which part of each comes
from degrees alone? Hypotheses (H1–H7) were written before the runs (`ResearchQ/question.md`).

**5 added networks** (SNAP):

| Network | Kind | N | Edges | ⟨k⟩ | Max degree | Degree CV | Clustering | Assortativity |
|---|---|---|---|---|---|---|---|---|
| grqc (ca-GrQc) | co-authorship | 4,158 | 13,422 | 6.5 | 81 | 1.34 | 0.56 | +0.64 |
| astroph (ca-AstroPh) | co-authorship | 17,903 | 196,972 | 22.0 | 504 | 1.41 | 0.63 | +0.20 |
| emaileu (email-Eu-core) | email | 986 | 16,064 | 32.6 | 345 | 1.14 | 0.41 | −0.03 |
| asinternet (as20000102) | Internet routers, **not social** | 6,474 | 12,572 | 3.9 | 1,458 | 6.44 | 0.25 | −0.18 |
| gnutella (p2p-Gnutella08) | file sharing, **not social** | 6,299 | 20,776 | 6.6 | 97 | 1.29 | 0.01 | +0.04 |

**Graph types** (new ones for all 10 networks):

- `samedeg`: like `shuffled`, but players are re-seated only among seats of about the same
  degree (factor-2 degree bins, ≥ 10 seats per group). Loses partners, keeps degree. Splits
  real − shuffled into real − samedeg (fixed partners) + samedeg − shuffled (keeping one's degree).
- `er`, `ba`, `ws`: Erdős–Rényi, Barabási–Albert, Watts–Strogatz with the same N and ⟨k⟩
  (WS: rewiring probability chosen to match the real clustering). One graph each.

Same grid as experiment 1. New runs: 55 graphs × 6,000 = **330,000 runs**
(`results/sweep_more_runs.csv`); analysed together with experiment 1 (`python src/analyze.py --more`
→ `results/sweep_more_*`). Node files saved for every static graph (rep 0).

**1. Fixed partners (real − shuffled), and the part that is partners only (real − samedeg)**, A ≤ 1:

| Network | real − shuffled β = 0.1 | β = 1 | β = 100 | real − samedeg β = 0.1 | β = 1 | β = 100 |
|---|---|---|---|---|---|---|
| Facebook | +0.008 | +0.010 | +0.048 | +0.007 | +0.010 | +0.048 |
| LastFM | +0.010 | +0.015 | +0.058 | +0.006 | +0.017 | +0.052 |
| Twitch | +0.021 | +0.020 | +0.042 | +0.005 | +0.011 | +0.029 |
| Deezer | +0.008 | +0.012 | +0.052 | +0.006 | +0.015 | +0.049 |
| GitHub | +0.029 | +0.026 | +0.037 | +0.004 | +0.009 | +0.016 |
| grqc | +0.006 | +0.020 | +0.108 | +0.005 | +0.023 | +0.104 |
| astroph | +0.008 | +0.013 | +0.070 | +0.006 | +0.014 | +0.061 |
| emaileu | +0.011 | +0.009 | +0.030 | +0.005 | +0.007 | −0.009 |
| asinternet | +0.040 | +0.030 | +0.033 | +0.002 | +0.009 | +0.018 |
| gnutella | +0.014 | +0.009 | +0.035 | +0.009 | +0.011 | +0.029 |

Fixed partners help on all 10. The growth with β is the partners-only part (9 of 10;
emaileu slightly negative at β ≥ 10). At low β on the networks with the most uneven degrees
(asinternet, GitHub, Twitch), most of real − shuffled comes from keeping one's degree.

**2. Structure beyond degree, clustering, degree spread**, A ≤ 1:

| Network | real − degseq β ≤ 1 (max \|diff\|) | real − degseq β = 100 | WS − ER β = 100 | degseq − ER β = 1 |
|---|---|---|---|---|
| Facebook | 0.009 | +0.013 | +0.037 | +0.038 |
| LastFM | 0.002 | +0.015 | +0.020 | +0.043 |
| Twitch | 0.005 | +0.005 | +0.011 | +0.050 |
| Deezer | 0.001 | +0.009 | +0.015 | +0.033 |
| GitHub | 0.005 | +0.000 | +0.011 | +0.064 |
| grqc | 0.006 | +0.062 | +0.070 | +0.037 |
| astroph | 0.008 | +0.038 | +0.069 | +0.047 |
| emaileu | 0.002 | −0.011 | +0.029 | +0.045 |
| asinternet | 0.011 | −0.027 | +0.024 | +0.051 |
| gnutella | 0.007 | −0.007 | +0.001 | +0.036 |

At β ≤ 1, structure beyond degree barely matters anywhere. At high β, clustering adds
cooperation (WS − ER), most on the co-authorship networks (clustering 0.56–0.63), which
is also where real − degseq is largest. Degree spread helps on all 10 at every β
(degseq − ER +0.016 to +0.066). ER/BA/WS are one graph each: CIs hold run noise only.

**3. Hubs defect** (Spearman(cooperation, degree), real graphs, A ≤ 1):

| Network | β = 0.1 | β = 1 | β = 3 | β = 10 | β = 100 |
|---|---|---|---|---|---|
| grqc | −0.66 | −0.75 | −0.60 | −0.32 | −0.25 |
| astroph | −0.65 | −0.74 | −0.70 | −0.38 | −0.27 |
| emaileu | −0.66 | −0.68 | −0.61 | −0.30 | −0.11 |
| asinternet | −0.37 | −0.52 | −0.46 | −0.36 | −0.31 |
| gnutella | −0.62 | −0.72 | −0.71 | −0.54 | −0.47 |

Negative on all 10 networks. Also negative on every random graph at β = 0.1–3 (BA −0.31 to
−0.54, ER −0.18 to −0.64, WS weakest −0.06 to −0.44): degrees alone are enough, as the
proposed mechanism says. At high β real structure changes its size on some networks
(β = 100: astroph real −0.27 vs degseq −0.01; emaileu −0.11 vs +0.19). In A > 1 it
reverses at high β (hubs cooperate more), from β ≈ 2–20 depending on the network; on
several networks not steadily (positive at β 2–3, near 0 around β = 10, rising again).
Node level: rep 0 only, no CIs.

**Diagnostics:** 41,937 of 42,000 cells ok; 56 still moving and 7 with repeats that differ
(≤ 4 per graph); 11 % oscillate (β ≥ 2, mostly shuffled/samedeg).

## Desynchronised-update check (2026-10-23)

In all sweeps above every player updates at the same moment each round. At high β each
update is large, so the whole population can switch together (this lockstep also causes the
period-2 oscillations). Check (mentor's code): each player updates with probability 0.5 per
round; everyone still plays every round. 10 networks × (real, degseq, shuffled, samedeg, ER,
WS) × β = 1, 3, 10, 100 × a = 0.1–0.7 × 5 b × 10 reps = **84,000 runs**, same seeds as the
synchronous sweeps (`results/sweep_desync_runs.csv`, `python src/analyze.py --desync` →
`results/sweep_desync_vs_sync.csv`, `results/sweep_desync_node_vs_sync.csv`).
Full report: `report_desync.txt`.

Result: most of the high-β contrasts came from synchronous updating; hub defection and the
benefit of uneven degrees are robust.

| Contrast, A ≤ 1 | Median share kept under desync, β = 1 | β = 10 | β = 100 |
|---|---|---|---|
| real − shuffled (fixed partners) | 54% | 26% | 30% |
| real − samedeg (partners only) | 45% | 32% | 33% |
| WS − ER (clustering) | (≈ 0 both) | 25% | 29% |
| real − degseq (structure beyond degree) | (≈ 0 both) | 44% | 46% |
| degseq − ER (degree spread) | 97% | 87% | 86% |

Share kept = desync ÷ synchronous per network, where the synchronous effect is ≥ 0.005.

- **Fixed partners (C2)** still help on all 10 networks: real − samedeg at β = 100 is
  +0.005 to +0.039 (≥ 0.01 on 6 of 10; was +0.016 to +0.104, emaileu −0.009).
- **Clustering (C3)** at β = 100 keeps ≥ 0.01 only on grqc (+0.029), astroph (+0.025) and
  Facebook (+0.013). Structure beyond degree likewise: grqc +0.028, astroph +0.017, Facebook +0.012.
- **Hubs defect (C1)** on all 10 networks (except Facebook at β = 100, +0.05), typically
  0.08 weaker. At A > 1 the reversal is stronger and steady: positive by β = 3 on 9 of 10
  networks, +0.60 to +0.78 at β = 100.
- At A > 1, desync makes fixed partners and uneven degrees lower cooperation at high β
  (−0.003 to −0.020 and −0.017 to −0.036 at β = 100).
- Oscillating cells: 34 of 8,400 (0.4%), against 1,375 of the same cells (16%) synchronously.
- Desync also halves how often each player updates (~750 instead of 1,500 updates). The
  async scan below separates the two: the drop comes from breaking the lockstep.

## Async scan (2026-10-23)

Mentor's script (`src/async_scan.py`). Update fraction f = 1, 0.5, 0.25, 0.1 (0.1 = about
one player in ten updates per round) with 1,500/f rounds and a window of 500/f, so every
player gets ~1,500 updates at every f: a smaller f removes the lockstep, not learning time.
10 networks × (real, degseq, samedeg, shuffled, ER) × β = 1, 10, 100 × a = 0.2, 0.4 ×
b = 1.5, 2.0 × 5 reps = **12,000 runs**, A ≤ 1 only (`results/async_scan_runs.csv`;
`python src/async_scan.py --analyze` → `results/async_scan_contrasts.csv/.png`).
Full report: `report_async.txt`.

Checks: f = 1 equals the synchronous sweeps and f = 0.5 (rounds 1,000–1,500) equals the
desync sweep, bit-identically, in 3,000 of 3,000 runs each. Node cooperation is sampled
every 1/f rounds (~500 actions per player at every f), so ρ is not inflated by less noise
at small f. Runs settled (drift > 0.01 in ≤ 0.3% at f ≤ 0.5; no oscillation at f ≤ 0.25).

| Contrast, A ≤ 1 | β | f = 1 (range) | Median share kept, f = 0.5 | f = 0.25 | f = 0.1 | f = 0.1 (range) |
|---|---|---|---|---|---|---|
| real − samedeg (fixed partners) | 1 | +0.010 to +0.024 | 53% | 33% | 23% | −0.002 to +0.007 |
| | 10 | −0.020 to +0.126 | 28% | 1% | −12% | −0.017 to 0.000 |
| | 100 | −0.029 to +0.131 | 26% | 4% | −14% | −0.019 to +0.004 |
| samedeg − shuffled (keeping one's degree) | 1 | +0.001 to +0.039 | 99% | 100% | 100% | +0.001 to +0.039 |
| | 100 | +0.004 to +0.093 | 15% | 12% | 11% | −0.002 to +0.011 |
| real − degseq (structure beyond degree) | 100 | −0.030 to +0.082 | 44% | 23% | 8% | −0.032 to +0.010 |
| degseq − ER (degree spread) | 1 | +0.043 to +0.080 | 97% | 96% | 95% | +0.041 to +0.076 |
| | 100 | +0.028 to +0.095 | 88% | 84% | 81% | −0.001 to +0.070 |

Share kept = value at f ÷ value at f = 1 per network, where |f = 1 value| ≥ 0.005. f = 1
values are over this scan's 4 (b, a) cells, so they differ from the tables above.

- **Fixed partners (C2)** only help in lockstep. The effect shrinks steadily as f falls and
  at f = 0.1, β ≥ 10 is slightly negative: −0.012 to −0.019 on 6–7 of 10 networks (CIs
  exclude 0). At f = 0.5 it is the same after ~750 and ~1,500 updates per player
  (≤ 0.006 apart), so the desync drop came from breaking the lockstep, not from fewer updates.
- **Keeping one's degree** at β = 1 is untouched (asinternet +0.039, GitHub +0.033,
  Twitch +0.021); at high β its synchronous size was lockstep.
- **Hubs defect (C1)** at f = 0.1 on all 10 networks at β = 1 (−0.52 to −0.83, 80–94% of
  f = 1) and β = 10 (−0.36 to −0.70); at β = 100 on 9 of 10 (−0.30 to −0.64), Facebook ≈ −0.05.
- **Degree spread (C3)** stays (+0.033 to +0.076 at f = 0.1, all 10, β ≤ 10; β = 100 all but
  Facebook). **Structure beyond degree** at high β was mostly lockstep: grqc +0.082 → +0.007;
  negative at f = 0.1 on Facebook (−0.032), astroph (−0.023), emaileu (−0.015).
- Not in the scan: WS (clustering), A > 1, β = 3.

## Extra scans (2026-10-25)

Mentor's script (`src/extra_scans.py`), two runs filling the async scan's gaps.
Full report: `report_extra.txt`.

- `--regimes`: the async-scan design (update fraction f = 1, 0.5, 0.25, 0.1 at equal
  updates per player) for regime **A > 1** (b = 1.7, 2.0 × a = 0.6, 0.7; real, degseq,
  samedeg, shuffled, ER, WS) and for **WS in the A ≤ 1 cells** (clustering = WS − ER).
  10 networks × β = 1, 10, 100 × 5 reps = **16,800 runs** (`results/extra_regimes_runs.csv`).
- `--sequential`: **one player at a time** (fully sequential, `fast_model.run_bm_sequential`;
  the f → 0 limit, checked against f = 0.05: 6/6 cells within 0.0007). 8 networks (no Deezer,
  GitHub: too slow), 6 graph types, β = 1, 100, cells (b, a) = (1.5, 0.4), (2.0, 0.2)
  [A ≤ 1] and (2.0, 0.7) [A > 1], 3 reps = **864 runs** (`results/extra_sequential_runs.csv`).

Checks: all runs present; f = 1 equals the synchronous sweeps in 4,200 of 4,200 runs
(bit-identical); drift > 0.01 in ≤ 0.07% of runs.

| Contrast | Regime | β | f = 1 (sync) | f = 0.1 | One at a time |
|---|---|---|---|---|---|
| real − samedeg (fixed partners) | A ≤ 1 | 1 | +0.008 to +0.023 | −0.002 to +0.007 | −0.003 to +0.006 |
| | | 100 | −0.057 to +0.155 | −0.022 to −0.001 | −0.034 to −0.007 |
| real − shuffled (fixed seats) | A > 1 | 100 | +0.001 to +0.010 | −0.035 to −0.005 | −0.035 to −0.003 |
| degseq − ER (degree spread) | A ≤ 1 | 100 | +0.051 to +0.105 | +0.022 to +0.082 | +0.022 to +0.080 |
| | A > 1 | 100 | −0.004 to +0.005 | −0.041 to −0.020 | −0.041 to −0.018 |
| WS − ER (clustering) | A ≤ 1 | 100 | +0.001 to +0.170 | −0.025 to +0.016 | −0.027 to +0.009 |
| Spearman(cooperation, degree), real | A ≤ 1 | 100 | −0.68 to +0.24 | −0.65 to −0.18 | −0.64 to −0.14 |
| | A > 1 | 1 | −0.63 to −0.23 | −0.31 to +0.10 | +0.01 to +0.27 |
| | A > 1 | 100 | +0.10 to +0.68 | +0.62 to +0.78 | +0.51 to +0.85 |

Ranges over networks. A > 1 rows with f = 1 and f = 0.1 are from `--regimes` (10 networks,
4 cells); all other rows, and the one-at-a-time column, use the `--sequential` cells
(8 networks) so the three columns compare the same settings.

- **Fixed partners (C2)** without lockstep: ≈ 0 at β = 1, negative at β = 100 on all 8
  (one at a time is more negative than f = 0.1 on 4 of 8 networks by > 0.005).
- **A > 1**: fixed seats and uneven degrees *lower* cooperation at high β on every network,
  more so as f falls; synchronously both were ≈ 0. The hub reversal (hubs cooperate more) is
  stronger without lockstep and one at a time already shows at β = 1 (7 of 8 networks).
- **Hubs defect (C1)** at A ≤ 1 on all 8 one at a time, including Facebook at β = 100
  (−0.14; synchronous +0.24 on these cells).
- **Clustering (C3)** at high β was lockstep: at f = 0.1, |WS − ER| < 0.01 on 7 of 10
  (10-network `--regimes` runs). grqc keeps +0.045 but is still falling (+0.009 one at a
  time); Facebook (−0.061) and asinternet (−0.032) come from the a = 0.2 cells, where WS
  and ER settle in different states, not from a general clustering effect.

## Checks

- `src/test_model.py`: unit checks of the Mesa reference model (20 checks).
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
data/               10 real edge lists; data/synthetic/ = rewirings, ER/BA/WS (generated once, fixed)
src/
  networks.py       load + clean graphs, build rewirings, topology table
  model.py          Mesa reference model (readable version of the rules)
  fast_model.py     numpy version of BM used by run.py (~10-20x faster)
  check_fast_model.py, test_model.py, validate_bm.py, pilot.py   checks (see above)
  run.py            the sweep -> results/sweep_runs.csv (--more: extension -> sweep_more_runs.csv;
                    --desync: high-beta check, half the players update per round -> sweep_desync_runs.csv)
  analyze.py        diagnostics, contrasts, node level -> results/sweep_*
  band_test.py      hub defection vs the band rule -> results/band_test.csv
  async_scan.py     update fraction 1-0.1 at equal updates per player -> results/async_scan_*
  extra_scans.py    --regimes (A > 1, WS) and --sequential (one player at a time) -> results/extra_*
  plot_graphs.py    network drawings -> graphs/
results/            sweep_runs.csv (90,000 runs), sweep_more_runs.csv (330,000 runs),
                    sweep_desync_runs.csv (84,000), async_scan_runs.csv (12,000),
                    extra_regimes_runs.csv (16,800), extra_sequential_runs.csv (864), tables and figures
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

**Desynchronised check** (results above): `python src/run.py --desync` reruns β = 1, 3, 10,
100 with each player updating with probability 0.5 per round (84,000 runs, same seeds);
`python src/analyze.py --desync` puts every contrast and the node-level degree correlation
next to its synchronous value. Test first: `python src/run.py --test --desync` (needs
`--test` without `--desync` first), then `python src/analyze.py --test --desync`.

**Async scan**: `python src/async_scan.py --processes 12` (~2.5 h on 12 cores; restartable,
skips finished runs), then `python src/async_scan.py --analyze`. Test: `--test`, then
`--test --analyze`.

**Extra scans** (`--regimes` first: the sequential analysis needs its runs):

```
python src/extra_scans.py --regimes --processes 12      (~4 h on 12 cores)
python src/extra_scans.py --sequential --processes 12   (~3.5 h)
python src/extra_scans.py --regimes --analyze
python src/extra_scans.py --sequential --analyze
```

Test: add `--test` (with `--processes 4`), then `--test --analyze`. Restartable.

`python src/run.py` reruns the full sweep (~6 h on 12 cores; it skips runs already in
`results/sweep_runs.csv`, so delete or rename that file first). Per-node results
(`results/sweep_nodes/`, ~200 MB) are not in the repo; the node-level table built from
them is (`results/sweep_node_level.csv`).
