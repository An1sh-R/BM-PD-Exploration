# Research Question

## Question

Weak PD (R = 1, T = b, S = P = 0) played by Bush–Mosteller (BM) aspiration learners with averaged payoffs on real networks. How much do (1) a player's degree, (2) fixed partners and (3) network structure beyond the degree sequence change cooperation, and how does each depend on learning sensitivity β and aspiration A = a·b?

"Weak" is the game's name (S = P = 0, the mildest PD), not weak selection.

## Why

- BM = reinforcement learning: players judge their own payoff against an aspiration; nobody copies anyone. Cooperation on networks is mostly studied with imitation on synthetic graphs.
- Ezaki et al. 2016 (lattice): β changes BM cooperation. Ezaki & Masuda 2017 (rings, one β): fixed partners help BM, effect depends on degree k and b/c.
- Earlier work finds RL cooperation largely insensitive to topology (Cimini & Sánchez 2014; Amaral et al. 2016). Here: real networks, node level, across β and A.

## Claims (experiment 1 + extension + desync check: 10 networks, 504,000 runs; numbers in README.md)

Stated with their conditions. First written 2026-10-10 from experiment 1 (5 networks); revised 2026-10-13 after the extension sweep (H1–H7); revised 2026-10-23 after the desynchronised-update check (H8; `report_desync.txt`). A ≤ 1 = a cooperator can be satisfied (main regime). "Sync" = all players update every round (the main sweeps); "desync" = each player updates with probability 0.5 per round (84,000 runs, β = 1, 3, 10, 100, a = 0.1–0.7). Effects that shrink under desync come partly from everyone updating at the same moment.

- **C1. Low-degree players cooperate more than hubs. Robust to desync.** A ≤ 1, sync: Spearman(node cooperation, degree) < 0 on all 10 networks at every β (−0.11 to −0.77; LastFM: top-1% hubs 0.17 vs degree-1 nodes 0.45). Strongest at β ≈ 1–2, weaker at high β. Exception: Facebook at β ≥ 10 (−0.03 to +0.11). Desync: still negative on all 10 (−0.13 to −0.67) except Facebook at β = 100 (+0.05); typically 0.08 weaker.
  - A > 1: reverses (hubs cooperate more) at high β. Sync: first positive at β ≈ 2–20 depending on the network (β 2 emaileu, Facebook; 3 GitHub, Twitch, astroph; 5 Deezer, LastFM, gnutella; 10 asinternet; 20 grqc; up to +0.71), not steady (positive at β 2–3, near 0 around β = 10, rising again). Desync: stronger and steady, positive by β = 3 on 9 of 10 networks (asinternet from β = 10), +0.60 to +0.78 at β = 100. The dip near β = 10 was a lockstep effect.
  - a = 0: weak, only around β ≈ 1 (≥ −0.32; sync only).
  - Degrees alone produce it: negative on every degree-preserving rewiring, BA (−0.31 to −0.54), ER (−0.18 to −0.64) and WS (weakest, −0.06 to −0.44) at β = 0.1–3, sync (β = 0.01 excluded, reporting rules). Desync at β = 1: degseq −0.51 to −0.69, ER −0.17 to −0.51, WS −0.04 to −0.31. Fits the mechanism below, which uses only a node's degree.
  - At high β (sync) real structure changes its size on some networks (astroph real −0.27 vs degseq −0.01; emaileu −0.11 vs +0.19 at β = 100); on asinternet, gnutella real ≈ degseq. Node level = rep 0 only, no CIs.
  - Proposed mechanism: with averaged payoffs and a share x of cooperating neighbours, a cooperator earns x (satisfied iff x ≥ a·b), a defector b·x (satisfied iff x ≥ a). A hub sees x ≈ its neighbourhood's mean. If a ≤ x < a·b, cooperating disappoints and defecting satisfies → hubs drift to D. A degree-1 player with one cooperating partner gets 1 ≥ A and stays C. Band test (2026-10-13, `src/band_test.py`, sync): partly supported. Hubs defect most when their x is in the band (9 of 10 networks), but also below and above it, so the band alone does not explain C1.
  - Wording: "in the model, on real network structure". Not a claim about real people.
- **C2. Fixed partners help BM on all 10 networks, but how much depends on synchronous updating.** Sync, A ≤ 1: real − shuffled +0.006 to +0.040 at β = 0.1 → +0.030 to +0.108 at β = 100. Desync: about half of the effect at β = 1 and about a third at β ≥ 10 (median share kept 26–33%); real − shuffled +0.007 to +0.037 at β = 100.
  - Split by the same-degree shuffle: real − shuffled = (real − samedeg: fixed partners) + (samedeg − shuffled: keeping one's degree).
  - Partners only (real − samedeg). Sync: +0.002 to +0.009 at β = 0.1 → +0.016 to +0.104 at β = 100 on 9 of 10 (emaileu −0.010 to −0.003 at β ≥ 10). Desync: positive on all 10 at every β tested; +0.003 to +0.008 at β = 1 → +0.005 to +0.039 at β = 100, ≥ 0.01 on 6 of 10. Growth with β is clear only on grqc, astroph, Facebook, Deezer, LastFM. Growth with β not reported before as far as found (Ezaki & Masuda 2017 used one β), but here it is largely a synchronous-updating effect.
  - Keeping one's degree (samedeg − shuffled): at low β on very uneven-degree networks most of real − shuffled (β = 0.1 sync: asinternet 0.037 of 0.040, GitHub 0.025 of 0.029, Twitch 0.016 of 0.021); unchanged by desync at β = 1. At β = 100 it vanishes under desync (−0.003 to +0.006; sync up to +0.040).
  - A > 1 (desync only): fixed partners lower cooperation at high β (real − shuffled −0.003 to −0.020 at β = 100; sync small and positive).
  - Open: desync also halves each player's updates; the β = 1 drop is not yet assigned to lockstep vs update rate.
  - "More than imitators" is not tested here: do not claim it.
- **C3. Uneven degrees help, robustly. Beyond the degree sequence, structure barely matters at β ≤ 1; at high β clustering adds cooperation only on the most clustered networks.** Degree spread (degseq − ER): +0.016 to +0.066 on all 10 at every β (sync, largest GitHub); desync unchanged at β = 1 (≤ 0.002) and positive on all 10 at every β (+0.002 Facebook to +0.033 at β = 100). At A > 1 under desync it turns negative at high β (−0.017 to −0.036 at β = 100).
  - real − degseq: |diff| ≤ 0.011 at β ≤ 1 on all 10 (sync; desync at β = 1 ≤ 0.008). High β, sync: co-authorship networks +0.040 (astroph) to +0.062 (grqc), Facebook up to +0.024, others −0.011 to +0.016, asinternet −0.027. Desync at β = 100: ≥ 0.01 only on grqc +0.028, astroph +0.017, Facebook +0.012; asinternet −0.010.
  - Clustering (WS − ER): ≈ 0 at β ≤ 1 (≥ −0.008). High β, sync: +0.011 to +0.070 (gnutella ≈ 0), largest on grqc and astroph. Desync at β = 100: ≥ 0.01 only on grqc +0.029, astroph +0.025, Facebook +0.013 (the three most clustered networks); others +0.009 or less.
  - Fits Cimini & Sánchez 2014, Amaral et al. 2016 at low β; at high β the extra structure effect is small once updating is desynchronised.
  - Not "shuffling doesn't matter": shuffled seats do matter (C2). Rewiring links at fixed degrees barely does at low β.
  - ER/BA/WS = one graph each: CIs hold run noise only.

## Extension: 5 more networks (added 2026-10-12)

Do C1–C3 hold on structures unlike the first 5 (all online friendship/follow graphs, assortativity −0.12 to +0.10)?

| Network | Kind | What it stresses |
|---|---|---|
| grqc (ca-GrQc) | co-authorship, social | hubs linked to hubs (assortativity +0.64), modularity 0.85 |
| astroph (ca-AstroPh) | co-authorship, social | high clustering 0.63, dense (⟨k⟩ 22) |
| emaileu (email-Eu-core) | email, social | small (986) and dense (⟨k⟩ 33) |
| asinternet (as20000102) | Internet routers, **not social** | extreme degree spread (CV 6.4, 37% degree-1) |
| gnutella (p2p-Gnutella08) | file-sharing peers, **not social** | no clustering (0.01) |

Non-social networks = contrasts (does it need social structure, or only degrees?). Never counted under "real social networks".

### Hypotheses (written 2026-10-12, before the sweep)

One dry-run cell was seen before writing: grqc, β = 10, a = 0.4, b = 1.5, one rep: real 0.54, degseq 0.45, shuffled 0.40.

- **H1 (C1).** A ≤ 1: Spearman(cooperation, degree) < 0 on all 5. Weakest where a hub's neighbourhood is least like the population: grqc (hubs next to hubs). Reverses at A > 1, β ≥ 3 as before.
- **H2 (C2).** real − shuffled > 0 in A ≤ 1 on all 5 and grows with β.
- **H3 (C3).** |real − degseq| ≤ 0.01 at β ≤ 1 on all 5. At high β it may exceed experiment 1's 0.024 on grqc and astroph, where rewiring removes the most structure (clustering → ~0.01, grqc modularity 0.85 → 0.37).

Added 2026-10-13 (ER/BA/WS for all 10 networks), before those runs:

- **H4 (C3, degree spread).** A ≤ 1: degseq − ER > 0 on all 10 networks, largest where degrees are most uneven (asinternet, GitHub). Basis: partial sweep v2 data (`../Experimentation`, 4 networks, A ≤ 1) gave +0.02 to +0.05; already seen, so a replication, not a blind prediction.
- **H5 (C3, clustering).** WS − ER ≈ 0 at low β, positive at high β (v2 partial: +0.01–0.04). Uninformative for gnutella (its WS is near-random).
- **H7 (C2, partners vs degree position; samedeg added 2026-10-13, before its runs).** real − samedeg > 0 in A ≤ 1 on all 10 networks and grows with β (fixed partners matter even when each player keeps its degree). No prediction for samedeg − shuffled's size; its share of real − shuffled is the answer to the C2 caveat.
- **H6 (C1, needs only degrees).** A ≤ 1: Spearman(cooperation, degree) < 0 on degseq and BA as on real (the mechanism uses only a node's degree), weaker on ER and WS (narrow degree range).
- **H8 (all β ≥ 2 claims; desynchronised rerun, written 2026-10-13 before its runs, mentor review).** With each player updating with probability 0.5 per round (`run.py --desync`), regime A ≤ 1: (a) at β = 1 every contrast changes by ≤ 0.005 vs the synchronous run; (b) at β ≥ 3 real − shuffled, real − samedeg, real − degseq and WS − ER all shrink, by roughly half; (c) on grqc and astroph real − samedeg and WS − ER stay > 0.01 at β = 100. Basis: mentor's spot check (grqc, astroph, LastFM, Facebook; b = 1.5, a = 0.2–0.4, 3 seeds): β = 0.3 unchanged, β = 100 effects 40–65% smaller. If (c) fails, claims stay at β ≤ 1.
- **H9 (async scan, written 2026-10-23 before its runs; mentor's expectation from a spot check).** `src/async_scan.py`: update_fraction f = 1, 0.5, 0.25, 0.1 with 1,500/f rounds, so every player gets ~1,500 updates at every f; A ≤ 1 only (a = 0.2, 0.4; b = 1.5, 2.0), β = 1, 10, 100, 5 reps. (a) Checks: f = 1 reproduces the synchronous runs bit-identically; at f = 0.5 cooperation over rounds 1,000–1,500 equals the desync sweep exactly. (b) real − samedeg (fixed partners) shrinks towards 0 as f falls, at β = 10 and 100. (c) Hub defection (Spearman ρ < 0 on real graphs) and the degree effects (degseq − ER, samedeg − shuffled) show no trend towards 0. (d) If (b) holds at equal updates, the desync drop of the partner effect comes from breaking the lockstep, not from fewer updates. Not tested here: WS (clustering), A > 1, β = 3.

### Outcomes (sweep complete 2026-10-13)

- H1: holds (ρ < 0 on all 5 new networks). Wrong on details: grqc is not the weakest (emaileu is, at high β); the A > 1 reversal starts at β 2–20 depending on the network, not at β ≥ 3 everywhere (new 5: emaileu 2, astroph 3 but not steady, gnutella 5, asinternet 10, grqc 20).
- H2: holds; asinternet flat with β, emaileu dips at β 2–3.
- H3: holds at β ≤ 1 (asinternet 0.011, borderline). High β exceeds 0.024 on grqc (+0.062) and astroph (+0.040) as predicted. Not predicted: asinternet −0.027.
- H4: holds on all 10. Largest on GitHub; asinternet not above the rest.
- H5: holds; gnutella ≈ 0 as expected.
- H6: partly. Negative on degseq and BA, but also on ER; only WS clearly weaker. At high β degseq differs from real on astroph and emaileu.
- H7: holds on 9 of 10 (emaileu slightly negative at β ≥ 10). samedeg − shuffled: most of real − shuffled at low β on asinternet, GitHub, Twitch.
- H8 (desync, 2026-10-23; 84,000 runs, A ≤ 1): (a) **fails** for the fixed-partner contrasts: at β = 1, real − shuffled and real − samedeg already drop to 23–82% of their synchronous size (change up to −0.015; runs settled, max |drift| 0.0085). Other contrasts pass at β = 1 (≤ 0.005; real − degseq 0.007). (b) holds, more strongly than predicted: at β ≥ 10 the median kept share is 26–30% for real − shuffled, ~32% real − samedeg, 25–29% WS − ER, 44–46% real − degseq; degree spread (degseq − ER) mostly kept (median 86–87%). (c) holds: β = 100 real − samedeg grqc +0.039, astroph +0.023; WS − ER grqc +0.029, astroph +0.025. C1: A ≤ 1 hubs still defect on all 10 (ρ −0.13 to −0.67 except Facebook β = 100, +0.05; typically 0.08 weaker, range 0.14 stronger to 0.16 weaker); A > 1 reversal survives, earlier and steadier (positive by β = 3 on 9 of 10 networks: first positive Facebook β = 1, asinternet β = 10, rest β = 3); the dip near β = 10 was a lockstep effect. Oscillating cells 11% → 0.4%.

## Reporting rules

- Per network and regime, never pooled over networks (opposite signs cancel).
- Smallest effect worth reporting: |difference| ≥ 0.01 cooperation. Many CIs (networks × regimes × β × contrasts): read patterns across β, not single CIs.
- Dead zone (a ≥ 0.8) and β = 0.01 (not settled) flagged, not used for claims.
- 95% CI unit: rep (n = 10); with degseq involved, the rewiring (n = 5).

## Key refs

- Nowak & May 1992, Nature. Weak PD on lattices.
- Ezaki, Horita, Takezawa & Masuda 2016, PLOS Comput Biol. BM model; varied β (cooperation more frequent at large β, lattice only).
- Ezaki & Masuda 2017, PLOS ONE. BM on rings, static vs shuffled partners (β = 0.2; their payoff range ~7 vs ours ~1.5 → ≈ our β ≈ 1).
- Cimini & Sánchez 2014, J R Soc Interface. RL cooperation same on lattice, BA, well-mixed.
- Amaral, Wardil, Perc & da Silva 2016, Phys Rev E. Aspiration learning largely independent of topology.
- Santos & Pacheco 2005, PRL. Hubs and heterogeneity under imitation (contrast: there hubs cooperate).
- Data: SNAP (Leskovec & Krevl 2014). Each dataset's SNAP page lists its own paper to cite: get those before writing.
