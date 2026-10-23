# Design decisions

Companion to `question.md`. Trimmed 2026-10-12 from `../Experimentation/ResearchQ/design.md` to what experiment 1 and its extension use (Fermi, accumulated payoffs, sweep v2 left there). Dates = when decided.

## Scope

- Static networks. Synthetic graphs generated once, then fixed.
- Game: weak PD. R = 1, T = b, S = P = 0. b = temptation.
- Agents: BM only, averaged payoff. Synchronous rounds.

## Data

`data/`, edge lists flat. Cleaning on load (`networks.clean`): undirected, self-loops dropped, parallel edges merged, largest component, nodes relabelled 0..n−1.

| Name | File | Source | N | E | ⟨k⟩ | Max k | Deg CV | Clust | Assort |
|---|---|---|---|---|---|---|---|---|---|
| facebook | facebook_combined.txt | SNAP ego-Facebook | 4,039 | 88,234 | 43.7 | 1,045 | 1.20 | 0.61 | +0.06 |
| lastfm | lastfm_edges.csv | LastFM Asia | 7,624 | 27,806 | 7.3 | 216 | 1.58 | 0.22 | +0.02 |
| twitch | twitch_ENGB_edges.csv | Twitch ENGB | 7,126 | 35,324 | 9.9 | 720 | 2.24 | 0.13 | −0.12 |
| deezer | deezer_edges.csv | Deezer Europe | 28,281 | 92,752 | 6.6 | 172 | 1.21 | 0.14 | +0.10 |
| github | github_edges.csv | GitHub (musae) | 37,700 | 289,003 | 15.3 | 9,458 | 5.27 | 0.17 | −0.08 |
| grqc | ca-GrQc.txt.gz | SNAP | 4,158 | 13,422 | 6.5 | 81 | 1.34 | 0.56 | +0.64 |
| astroph | ca-AstroPh.txt.gz | SNAP | 17,903 | 196,972 | 22.0 | 504 | 1.41 | 0.63 | +0.20 |
| emaileu | email-Eu-core.txt.gz | SNAP (directed → undirected) | 986 | 16,064 | 32.6 | 345 | 1.14 | 0.41 | −0.03 |
| asinternet | as20000102.txt.gz | SNAP, Internet AS graph, not social | 6,474 | 12,572 | 3.9 | 1,458 | 6.44 | 0.25 | −0.18 |
| gnutella | p2p-Gnutella08.txt.gz | SNAP (directed → undirected), P2P, not social | 6,299 | 20,776 | 6.6 | 97 | 1.29 | 0.01 | +0.04 |

- Facebook: SNAP `facebook_combined.txt`, not the ego tarball (rebuilding from it gave 3,963 nodes ≠ 4,039).
- Formats: CSVs one header row, comma. Facebook space, no header. SNAP `.txt.gz` read directly, `#` comment lines skipped. ca-* files list each edge in both directions: merged.
- Largest component drops: grqc 5,242 → 4,158 (21%), astroph 18,772 → 17,903, emaileu 1,005 → 986, gnutella 6,301 → 6,299, asinternet none.
- Raw downloads (incl. spare Twitch regions DE, ES, FR, PTBR, RU) in `../snaps/`.
- Full metrics (incl. Louvain modularity) for all 100 graphs: `results/topology_table.csv`.

## Synthetic equivalents (`networks.py`, seed 42)

| Type | Match | Isolates |
|---|---|---|
| degseq | copy of real, `nx.double_edge_swap` 10×E swaps, cut-off pieces joined back | degree sequence alone |
| ER | p = ⟨k⟩/(N−1), largest component | random baseline |
| BA | m = round(⟨k⟩/2) | heavy tail, low clustering |
| WS | even k ≈ ⟨k⟩; rewiring p from a grid, closest clustering to real | clustering + short paths |

- Experiment 1 used only degseq (+ shuffled seats). The extension runs ER/BA/WS for all 10 networks.
- degseq replaced `nx.configuration_model` (collapses hub multi-edges: GitHub kmax 9,458 → 5,923).
- 5 independent rewirings per network (`<name>_rewired0..4`, seeds 1000 + r); rep r runs on rewiring r % 5.
- **Connected rewirings (2026-10-08).** Swaps cut off tiny pieces (mostly two degree-1 nodes linked together; LastFM 0.9% of nodes). Isolated pairs cooperated ~0.84 at high β and pushed degseq cooperation up. `reconnect_pieces`: piece edge (u,v) + non-bridge main edge (x,y) → (u,x),(v,y); degrees exact, connected (asserted). Experiment-1 degseq runs all redone on these.
- degseq removes clustering fully on most graphs, partly on hub-heavy ones (GitHub 0.17 → 0.09, asinternet 0.25 → 0.13, emaileu 0.41 → 0.16: hubs make triangles by degree alone).
- Limits of ER/BA/WS (matter only if ever run): BA ⟨k⟩ off 7–10% (integer m) for deezer, lastfm, github, grqc, gnutella; BA can't reach asinternet's kmax (229 vs 1,458); ER loses up to 2% nodes (asinternet); gnutella WS = near-random (real clustering ~0 → chose p = 0.8).

## Shuffled seats (mentor's idea, 2026-10-07)

- `<name>_shuffled` = real graph, players re-seated at random every round, keeping their p. Same network, no fixed partners.
- Caveat: also removes each player's fixed degree position. Addressed by `<name>_samedeg` (2026-10-13, Decision log): re-seated only within degree groups.

## BM rules (Ezaki et al. 2016; Ezaki & Masuda 2017)

- State p = cooperation propensity, start 0.5 for everyone.
- Action: intends C with prob p; intended action flipped with prob ε = 0.05 → P(C) = (1−ε)p + ε(1−p).
  - **Fixed 2026-10-07:** code had (1−ε)p + ε/2 (flip rate ε/2). Both pilots and the first `validate_bm` ran with the old rule; the sweep uses the corrected one.
- Payoff r = average over neighbours ∈ [0, b]. Stimulus s = tanh(β(r − A)), A = a·b.
- Update:

| Action | s ≥ 0 | s < 0 |
|---|---|---|
| C | p + (1−p)s | p + p·s |
| D | p − p·s | p − (1−p)s |

- p stays in [0, 1], no clipping.
- Aspiration as a fraction of b: the pilot's interesting band moves with b.

## Implementation

- `model.py` (Mesa 3.5.1): readable reference. Update phase reads frozen actions + payoffs → in-place updates = synchronous. Cooperation = fraction of C actions played. Also contains Fermi (used only by tests).
- `fast_model.py` (numpy): same rules in arrays; payoffs = one sparse product. 10–20× faster.
- `check_fast_model.py` (LastFM): payoffs and BM update exactly equal to Mesa; 7 cells × 20 seeds × 600 steps (incl. shuffled, β up to 100) agree, |diff| ≤ 0.0002 (`results/fast_model_check.csv`). Same seed ≠ same run across the two versions.
- `test_model.py`: 16 checks pass (re-run 2026-10-12).
- `validate_bm.py`: Ezaki & Masuda 2017 rings (N = 100, donation game, β = 0.2, A = 1, ε = 0.05, p0 = 0.8, 1000 runs). Shape matches all 3 paper claims: reciprocity at b/c = 6, k = 2 (+0.084); none at b/c = 2; gap shrinks with k. Paper gives no numbers → qualitative only.

## Pilot (`pilot.py`, LastFM, 9 β × 9 A × 3 b × 3 reps × 1000 steps, ε = 0.05)

- Cooperation 0.06–0.82. β flat for β ≤ 0.3, transition β ≈ 1–10, saturates β ≥ 30.
- β = 0.01 still drifting at step 1000 → flagged in analysis.
- Dead zone A ≳ 0.8b: nearly everyone unhappy, cooperation ≈ 0.5.
- **Period-2 oscillation**, not bistability (corrected 2026-10-07): at high β the whole population flips C ↔ D every round; the pilot sampled even steps only and saw one phase. Means over every step are fine. Likely a synchronous-update effect: mention in the paper.

## Sweep (`run.py`)

- Grid: β ∈ {0.01, 0.1, 0.3, 0.6, 1, 2, 3, 5, 10, 20, 30, 100} × a ∈ {0, 0.1, …, 0.9} × b ∈ {1.1, 1.3, 1.5, 1.7, 2.0} × 10 reps; graphs real, degseq, shuffled. 6,000 runs per graph.
- 1,500 rounds; outcome = mean cooperation over the last 500. Seed = rep → real/degseq/shuffled paired.
- Per run also: drift (2nd − 1st half of window), even_odd_gap (oscillation), mean_p.
- Per-node cooperation saved for real graphs, rep 0 only (`results/<name>_nodes/`, gitignored). Extension: real + degseq (see Decision log).
- Crash-safe: each row written at once; restart skips done runs; `--processes N`.
- **Experiment 1 (2026-10-08):** 5 original networks, 90,000 runs, 339 min on 12 processes → `results/sweep_runs.csv`. Re-checked 2026-10-10: CSV complete; 4 rows reproduced bit-exactly; degseq redone on connected rewirings.
- **Extension (not run yet):** `run.py --more` → `results/sweep_more_runs.csv`: added networks with all 6 graph types, original networks' ER/BA/WS (see Decision log, 2026-10-13). Same grid so tables compare directly. Order small → large.

## Analysis (`analyze.py`; `--more` for the extension)

- Regimes (a = A/b): a = 0 (nobody unhappy), A ≤ 1 (cooperator can be satisfied; main), A > 1 (cooperator never satisfied; only b ≥ 1.5), dead zone a ≥ 0.8.
  - **Dead-zone cutoff 0.9 → 0.8 (2026-10-09):** mean |coop − 0.5| a = 0.8 0.010–0.039 ≈ a = 0.9 0.009–0.033 (a = 0.7 0.014–0.047). Including 0.8 diluted the A > 1 averages.
- Diagnostics per cell: still moving (mean |drift| > 0.02), repeats differ (rep std > 0.05), oscillating (even-odd gap > 0.05; flag only, mean still valid).
- Contrasts, per network and regime, paired by seed: real − shuffled (fixed partners), real − degseq (structure beyond degree). 95% CI over reps, or over rewirings when degseq is involved.
- Node level: Spearman of node cooperation vs degree and local clustering, real graphs, rep 0.
- Reporting rules: in `question.md`.

## Decision log (newest last; add every new decision here when it is made)

- **2026-10-12 — 5 networks added** (grqc, astroph, emaileu, asinternet, gnutella; user's SNAP picks). Registered in `networks.py`; loader reads `.gz`. ER/BA/WS/degseq/5 rewirings built, all pass `check_graph`, degseq degrees exact. Original 5 networks still load identically (N, E checked).
- **2026-10-12 — Docs moved in.** CLAUDE.md, question.md, design.md trimmed from `../Experimentation` to experiment 1 + extension. Git rule changed: push only when the user says (the mentor sees this repo).
- **2026-10-12 — Extension sweep in its own CSV** (`run.py --more` → `results/sweep_more_runs.csv`, `analyze.py --more`). No branch, main only. Same grid and graph types as experiment 1 (real, degseq, shuffled).
- **2026-10-12 — Node files for degseq too** (rep 0 = rewiring 0), for C1: same degrees, clustering destroyed, so equal Spearman(cooperation, degree) on real and degseq means the effect is degree, not clustering. `analyze.py` node level prints real vs degseq; figure stays real-only. ~+50 MB, no extra runs. Experiment-1 sweep unaffected (already run, real only).
- **2026-10-12 — Hypotheses H1–H3 for the extension** written in question.md before the sweep.
- **2026-10-12 — First launch stopped by the user** after 276 emaileu runs (kept: valid, restart skips them).
- **2026-10-13 — Sweep every graph we have** (user). `run.py --more` = 5 added networks × (real, degseq, shuffled, ER, BA, WS) + ER/BA/WS of the original 5 (their real/degseq/shuffled already in `sweep_runs.csv`). One CSV, same grid as experiment 1. Extended by samedeg below.
- **2026-10-13 — Node files for every static graph** (real, degseq, ER, BA, WS; rep 0). Not shuffled: there a node is not one player. Shows whether "hubs defect" needs real structure or only degrees. Disk ~1 GB (93 GB free).
- **2026-10-13 — Analysis for C3.** `analyze.py --more` reads `sweep_runs.csv` + `sweep_more_runs.csv` together (all 10 networks); outputs `sweep_more_*`, experiment-1 outputs unchanged (checked: steps/diagnostics identical, node-level numbers identical + new graph_type column). New contrasts: degseq − ER (degree spread), WS − ER (clustering + locality at near-equal degrees). BA used at node level, not in a contrast (its ⟨k⟩ is off by up to 10%). ER/BA/WS = one graph each: CIs hold run noise only. Contrasts skip families where a pair is missing.
- **2026-10-13 — Test grid** (`--test`) now includes lastfm_er and twitch_ws so the new contrasts are exercised.
- **2026-10-13 — Same-degree shuffle (`<name>_samedeg`), with degree bins** (user). Splits C2: real − shuffled = (real − samedeg: partners only) + (samedeg − shuffled: keeping one's degree). Players re-seated every round only within their degree group (`networks.same_degree_groups`):
  - factor-2 degree bins (1, 2–3, 4–7, …); each group ≥ MIN_GROUP = 10 seats so a hub with a unique degree can still move;
  - a too-small (top) bin borrows only the highest-degree nodes it needs from the next bin down; equal degrees never split. First version merged whole bins: top group spanned 8–11× in degree (Facebook 128–1,045, asinternet 128–1,458). Now: median |log2(k / group mean degree)| 0.14–0.29 (≈ ±20%); widest groups = the top-10 hubs themselves (GitHub 1,568–9,458, asinternet 173–1,458), unavoidable with 10 seats.
  - In `fast_model.run_bm(seat_groups=...)` and Mesa `CooperationModel(seat_groups=...)` (Mesa tracks the current seating in `self.seating`; `self.players` keeps player order). Full shuffle code path unchanged: experiment-1 runs reproduce bit-identically (5 rows: real, degseq, shuffled, checked).
  - Checks: 2 new tests (groups cover every node once, ≥ 10; players keep their degree and do move), 18/18 pass. `check_fast_model.py` with 2 samedeg cells: exact payoff + update checks pass, 9/9 cells agree (samedeg |diff| ≤ 0.0001); the 7 old cells give the same numbers as before (Mesa full shuffle unchanged).
  - Runs on all 10 networks (original 5 too, needed for the contrast). No node files (a node is not one player).
- **2026-10-13 — Final extension sweep:** 55 graphs × 6,000 = 330,000 runs: added 5 × (real, degseq, shuffled, samedeg, ER, BA, WS) + original 5 × (samedeg, ER, BA, WS). Original 5's real/degseq/shuffled not rerun: in `sweep_runs.csv`, reproduced bit-identically by the current code. 12 processes.
- **2026-10-13 — Extension sweep complete.** Paused once by the user at 304,472 runs, resumed (restart skips finished runs; file ended on a full line). Checked: 330,000 unique run_ids, 55 graphs × 6,000, no missing cooperation. `analyze.py --more`: 42,000 cells, 41,937 ok, 56 still moving (scattered, ≤ 4 per graph), 7 repeats differ; 11% of cells oscillate (β ≥ 2, mostly shuffled/samedeg; as in experiment 1). Node level has no degseq column for the original 5 (experiment 1 saved real node files only). Results vs H1–H7 reported to the user; 
- **2026-10-13 — Claims revised** (user approved): question.md C1–C3 rewritten with all 10 networks + H1–H7 outcomes; README gets an extension section. Main changes: C2 split into fixed partners (grows with β) vs keeping one's degree (most of the low-β effect on uneven-degree networks); C3 = structure beyond degree barely matters at β ≤ 1, clustering adds cooperation at high β (co-authorship +0.04–0.06); C1 holds on all 10 and on every random graph at β ≤ 3.
- **2026-10-13 — C1 mechanism test 1: band test** (user; `src/band_test.py`, no new runs; prediction written before running). Per cell, real graphs, rep 0 node files: x_hub = mean over the top-1% degree nodes of their neighbours' cooperation (the x a hub actually sees). Band position: below (x_hub < a), band (a ≤ x_hub < a·b), above (x_hub ≥ a·b; all a = 0 cells). Prediction: band cells have Spearman(cooperation, degree) clearly negative; above and below cells near 0. At A > 1 the band is x_hub ≥ a (a·b > 1 ≥ x), so the rule also predicts ρ < 0 there: the observed high-β reversal would then be outside the mechanism. Reported per network, by β; oscillating runs (even-odd gap > 0.05) split out (time-averaged x hides round-to-round x); dead zone, β = 0.01 flagged. Not tested: steps 2–4 (fixed neighbourhood, per-degree prediction, satisfaction tracking).
- **2026-10-13 — Band test result** (`results/band_test.csv`): prediction **partly failed**. 4,400 usable cells (469 oscillate, split out). Not oscillating, per network: band cells most negative (median ρ −0.51 to −0.82; ρ < −0.1 in 87–100% of cells, Facebook 66%). But below-band cells also negative (−0.32 to −0.62) and above-band cells too (−0.03 to −0.38; −0.68 at β = 0.1, all networks), not ≈ 0 as predicted. Ordering band < below < above holds at every β. A > 1: every cell has x_hub < a ("below"); rule predicts no hub/leaf difference there, so the high-β reversal is outside it. Reading: the band adds to C1 but does not explain it alone; the cooperator threshold a·b looks more important than the defector threshold a, and at low β satisfaction is graded (tanh), not a threshold. Next tests (2, 3) not run.
- **2026-10-13 — Correction (reversal onset).** The H1 outcome said the A > 1 reversal needs β > 3 on most networks; wrong. First positive ρ: β 2–3 on emaileu, Facebook, GitHub, Twitch; 5 on Deezer, LastFM, gnutella; 10 asinternet; 20 grqc; astroph not steady. Fixed in question.md (C1, H1 outcome) and README. Caught by a review of the sweep-2 report.
- **2026-10-13 — Report cross-check for the mentor.** All report numbers recomputed from the CSVs with β = 0.01 excluded (reporting rules). Fixed: real ρ range −0.11 to −0.77 (was −0.78); random-graph ranges at β = 0.1–3 were computed with β = 0.01 included (BA −0.31 not −0.25, ER −0.18 not −0.11, WS −0.06 not −0.03); reversal onset β 2–20 (emaileu, Facebook at β = 2); band test: band is the most negative position on 9 of 10 networks (asinternet band −0.51 vs below −0.52), not all.
- **2026-10-13 — Mentor report** `report_extension.txt` (user): numbers recomputed from the CSVs. Doc mismatches fixed at the same time: question.md C2 (real − samedeg at β = 0.1, not 0.01; asinternet total 0.027–0.040), README experiment-1 C1 (A > 1 onset per network instead of "β ≥ 3"; a = 0 dip to −0.30 instead of "no pattern").

- **2026-10-13 — Desynchronised-update check (`--desync`; mentor review).** Mentor's spot check: at β ≥ 10 about half of every contrast (real − shuffled, real − samedeg, real − degseq, WS − ER) disappears when only a random half of the players update each round; β ≤ 1 unchanged. So all β ≥ 2 claims need a desynchronised rerun before the paper. Implemented:
  - `update_fraction` in `fast_model.run_bm` and Mesa `CooperationModel` (each player updates with this probability per round; default 1.0 = synchronous). Random draw only when < 1, so all existing runs reproduce bit-identically (36 rows re-checked: experiment 1 real/degseq/shuffled + extension samedeg/degseq/ER/WS).
  - `run.py --desync` → `results/sweep_desync_runs.csv` (+ `update_fraction` column): 10 networks × (real, degseq, shuffled, samedeg, ER, WS) × β {1, 3, 10, 100} × a 0.1–0.7 × 5 b × 10 reps = 84,000 runs, same seeds as the synchronous sweeps (each run has a synchronous twin). β = 1 = control.
  - `analyze.py --desync` → `sweep_desync_*` + `sweep_desync_vs_sync.csv/.png`: each contrast next to its synchronous value on the same runs; kept_share = desync / sync.
  - Checks: 2 new tests (20/20 pass); `check_fast_model.py`: update_fraction = 1 bit-identical; 13/13 cells agree incl. the 4 new desync cells (|Mesa − numpy| ≤ 0.0003); `run.py --test --desync` + `analyze.py --test --desync` run end to end.
  - Prediction H8 written in question.md before the runs.
- **2026-10-21 — Mentor's desync code merged** (received 2026-10-21 as a full repo copy in `../mentor-code`; the entry above is the mentor's, dated by him). Only his 9 changed files copied (code + docs; no results or images). Re-checked here: 20/20 tests; `check_fast_model.py` 13/13 cells agree (4 desync cells, |Mesa − numpy| ≤ 0.0003), update_fraction = 1 bit-identical, output identical to the mentor's `fast_model_check.csv`; 30 old runs (experiment 1 + extension, all graph types incl. BA, β 1–100) rerun bit-identically; `--desync` job list = 84,000 unique runs, every one with a synchronous twin. Desync sweep not run yet. Noted for the analysis: update_fraction = 0.5 also halves each player's updates (~750 instead of 1,500), so check drift at β = 1; the desync run_ids equal the synchronous ones (different CSV, never concatenate them).
- **2026-10-21 — Desync analysis covers C1 at node level** (user): `analyze.py --desync` also pairs each real-graph rep-0 run with its synchronous twin's node file and compares Spearman(cooperation, degree), A ≤ 1 and A > 1, plus the first β where the A > 1 mean turns positive (the reversal) → `sweep_desync_node_vs_sync.csv`. Checked: on the test sweep both columns equal the existing node-level tables exactly (8/8 cells, |diff| = 0); all 1,400 real rep-0 cells of the full desync grid have a synchronous node file. Desync test sweep (80 runs, 8 processes, 20 s) + `analyze.py --test --desync` run end to end (test numbers not interpreted: 300 rounds).
- **2026-10-23 — Desync sweep complete** (`results/sweep_desync_runs.csv`, 84,000 runs, 60 graphs × 1,400, all update_fraction 0.5, no missing values). Paused once by the user at 71,163 and resumed (also restarted after VS Code closed; file intact). `analyze.py --desync`: 8,397 of 8,400 cells ok, 34 oscillate; every run paired with its synchronous twin; contrast CIs ≤ 0.0031. Outcome in question.md (H8). Claims C1–C3 not reworded yet (user decides). Open: desync changes both lockstep and update count per player, so the β = 1 drop in the partner effect cannot yet be assigned to either.
- **2026-10-23 — Claims revised after the desync check** (user): question.md C1–C3 now give synchronous and desync results side by side (C1 robust; C2 holds but its size and β-growth depend on synchronous updating; C3: uneven degrees robust, high-β clustering/structure ≥ 0.01 only on grqc, astroph, Facebook). README gets a desync section (table of median shares kept). `report_extension.txt` keeps its 2026-10-13 text with a dated update note at the top. New `report_desync.txt` (text version of the desync report); its 320 table numbers and the doc's 160 table cells re-checked against the CSVs. Fixed while checking: oscillation comparison now on the same 8,400 cells (1,375 = 16% sync, not the 11% of the full grid).
- **2026-10-23 — Async scan (mentor's `async_scan.py`, received 2026-10-23) → `src/async_scan.py`.** Separates the two parts of the desync change: update_fraction f ∈ {1, 0.5, 0.25, 0.1} with 1,500/f rounds (window 500/f), so updates per player stay ~1,500. Grid kept as sent (user: no extra run time; WS, A > 1, β = 3 later): 10 networks × (real, degseq, samedeg, shuffled, ER) × β {1, 10, 100} × a {0.2, 0.4} × b {1.5, 2.0} × 5 reps = 24,000 runs → `results/async_scan_runs.csv`; `--analyze` → `async_scan_contrasts.csv/.png`. Reviewed by reading (subagent + me) before any run. Changes before launch, no extra runs (user chose):
  - Hub-defection bias fixed: node cooperation was averaged over all 500/f window rounds, so 10× less action noise at f = 0.1, which alone makes Spearman(cooperation, degree) look stronger (~0.05–0.1, the size of the effect measured). Now sampled every 1/f rounds (~500 actions per player at every f) via new `fast_model.run_bm(record_every=...)`; default 1 = old behaviour. Measurement only, no rule change, so Mesa `model.py` unchanged.
  - New columns: drift and mean_p (did the long runs settle), cooperation_1000_1500 (at f = 0.5 must equal the desync sweep: same seed, the desync run is the first 1,500 rounds).
  - Docstring cost corrected: 6,000 settings × (1 + 2 + 4 + 10) = ~102,000 normal-run equivalents, not 51,000 (each round costs the same at any f).
  - `results/async_scan_test_*` added to .gitignore.
  - Reviewer notes kept for later: β = 1 may be underpowered (4 cells × 5 reps; more cells, not reps, since degseq has only 5 rewirings); analysis lacks real − shuffled, f = 1 / desync checks, kept shares; WS, A > 1 cells, β = 3 not in the grid.
  - Prediction H9 in question.md.
  - Checks before launch (2026-10-23): 20/20 tests; `check_fast_model.py` 13/13 cells, output file unchanged; 30 old runs + 6 rep-0 node files rerun bit-identically with `record_every`; `async_scan.py --test` + `--analyze` run end to end; 12 full-length runs: f = 1 equals the synchronous sweep and f = 0.5 rounds 1,000–1,500 equal the desync sweep exactly (6 graph types/networks). Note: compare CSV floats with `pd.read_csv(..., float_precision="round_trip")`; the default parser can be 1 ulp off and fakes mismatches.

## Open

- Node-level CIs: rep 0 only; emaileu top 1% = ~10 nodes.
