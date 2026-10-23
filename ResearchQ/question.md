# Research Question

## Question

Weak PD (R = 1, T = b, S = P = 0) played by Bush–Mosteller (BM) aspiration learners with averaged payoffs on real networks. How much do (1) a player's degree, (2) fixed partners and (3) network structure beyond the degree sequence change cooperation, and how does each depend on learning sensitivity β and aspiration A = a·b?

"Weak" is the game's name (S = P = 0, the mildest PD), not weak selection.

## Why

- BM = reinforcement learning: players judge their own payoff against an aspiration; nobody copies anyone. Cooperation on networks is mostly studied with imitation on synthetic graphs.
- Ezaki et al. 2016 (lattice): β changes BM cooperation. Ezaki & Masuda 2017 (rings, one β): fixed partners help BM, effect depends on degree k and b/c.
- Earlier work finds RL cooperation largely insensitive to topology (Cimini & Sánchez 2014; Amaral et al. 2016). Here: real networks, node level, across β and A.

## Claims (experiment 1 + extension: 10 networks, 420,000 runs; numbers in README.md)

Stated with their conditions. First written 2026-10-10 from experiment 1 (5 networks); revised 2026-10-13 after the extension sweep (H1–H7 outcomes below). A ≤ 1 = a cooperator can be satisfied (main regime).

- **C1. Low-degree players cooperate more than hubs.** A ≤ 1: Spearman(node cooperation, degree) < 0 on all 10 networks at every β (−0.11 to −0.77; LastFM: top-1% hubs 0.17 vs degree-1 nodes 0.45). Strongest at β ≈ 1–2, weaker at high β. Exception: Facebook at β ≥ 10 (−0.03 to +0.11). A > 1: reverses (hubs cooperate more) at high β, from β ≈ 2–20 depending on the network (first positive: β 2 emaileu, Facebook; 3 GitHub, Twitch, astroph; 5 Deezer, LastFM, gnutella; 10 asinternet; 20 grqc; up to +0.71). Not steady on several: positive at β 2–3, near 0 around β = 10, rising again. Astroph: +0.14 at β = 3, negative at 10–30, +0.09 at 100. a = 0: weak, only around β ≈ 1 (≥ −0.32).
  - Degrees alone produce it: negative on every degree-preserving rewiring, BA (−0.31 to −0.54), ER (−0.18 to −0.64) and WS (weakest, −0.06 to −0.44) at β = 0.1–3 (β = 0.01 excluded, reporting rules). Fits the mechanism below, which uses only a node's degree.
  - At high β real structure changes its size on some networks (astroph real −0.27 vs degseq −0.01; emaileu −0.11 vs +0.19 at β = 100); on asinternet, gnutella real ≈ degseq. Node level = rep 0 only, no CIs.
  - Proposed mechanism: with averaged payoffs and a share x of cooperating neighbours, a cooperator earns x (satisfied iff x ≥ a·b), a defector b·x (satisfied iff x ≥ a). A hub sees x ≈ its neighbourhood's mean. If a ≤ x < a·b, cooperating disappoints and defecting satisfies → hubs drift to D. A degree-1 player with one cooperating partner gets 1 ≥ A and stays C. Band test (2026-10-13, `src/band_test.py`): partly supported. Hubs defect most when their x is in the band (9 of 10 networks), but also below and above it, so the band alone does not explain C1.
  - Wording: "in the model, on real network structure". Not a claim about real people.
- **C2. Fixed partners help BM, more at high β.** real − shuffled > 0 on all 10 networks (A ≤ 1): +0.006 to +0.040 at β = 0.1 → +0.030 to +0.108 at β = 100. Growth with β not reported before as far as found (Ezaki & Masuda 2017 used one β).
  - Split by the same-degree shuffle: real − shuffled = (real − samedeg: fixed partners) + (samedeg − shuffled: keeping one's degree).
  - The growth with β is the fixed-partner part: real − samedeg goes from +0.002 to +0.009 at β = 0.1 to +0.016 to +0.104 at β = 100, on 9 of 10 networks (emaileu: −0.010 to −0.003 at β ≥ 10).
  - At low β on networks with very uneven degrees, most of real − shuffled is keeping one's degree (β = 0.1: asinternet 0.037 of 0.040, GitHub 0.025 of 0.029, Twitch 0.016 of 0.021). Exceptions to growth: asinternet flat (0.027–0.040); emaileu dips at β 2–3.
  - "More than imitators" is not tested here: do not claim it.
- **C3. Beyond the degree sequence, structure barely matters at β ≤ 1; at high β, clustering adds cooperation.** real − degseq: |diff| ≤ 0.011 at β ≤ 1 on all 10. High β: co-authorship networks +0.040 (astroph) to +0.062 (grqc), Facebook up to +0.024, others −0.011 to +0.016; asinternet −0.027 (real below its rewiring).
  - Clustering: WS − ER ≈ 0 at β ≤ 1 (≥ −0.008), +0.011 to +0.070 at high β, largest on grqc and astroph (clustering 0.56, 0.63), matching their real − degseq. Gnutella ≈ 0 (no clustering).
  - Degree spread helps: degseq − ER +0.016 to +0.066 on all 10 at every β (largest GitHub).
  - Fits Cimini & Sánchez 2014, Amaral et al. 2016 at low β only.
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

### Outcomes (sweep complete 2026-10-13)

- H1: holds (ρ < 0 on all 5 new networks). Wrong on details: grqc is not the weakest (emaileu is, at high β); the A > 1 reversal starts at β 2–20 depending on the network, not at β ≥ 3 everywhere (new 5: emaileu 2, astroph 3 but not steady, gnutella 5, asinternet 10, grqc 20).
- H2: holds; asinternet flat with β, emaileu dips at β 2–3.
- H3: holds at β ≤ 1 (asinternet 0.011, borderline). High β exceeds 0.024 on grqc (+0.062) and astroph (+0.040) as predicted. Not predicted: asinternet −0.027.
- H4: holds on all 10. Largest on GitHub; asinternet not above the rest.
- H5: holds; gnutella ≈ 0 as expected.
- H6: partly. Negative on degseq and BA, but also on ER; only WS clearly weaker. At high β degseq differs from real on astroph and emaileu.
- H7: holds on 9 of 10 (emaileu slightly negative at β ≥ 10). samedeg − shuffled: most of real − shuffled at low β on asinternet, GitHub, Twitch.
- H8 (desync, 2026-10-23; 84,000 runs, A ≤ 1): (a) **fails** for the fixed-partner contrasts: at β = 1, real − shuffled and real − samedeg already drop to 23–82% of their synchronous size (change up to −0.015; runs settled, max |drift| 0.0085). Other contrasts pass at β = 1 (≤ 0.005; real − degseq 0.007). (b) holds, more strongly than predicted: at β ≥ 10 the median kept share is 26–30% for real − shuffled, ~32% real − samedeg, 25–29% WS − ER, 44–46% real − degseq; degree spread (degseq − ER) mostly kept (median 86–87%). (c) holds: β = 100 real − samedeg grqc +0.039, astroph +0.023; WS − ER grqc +0.029, astroph +0.025. C1: A ≤ 1 hubs still defect (ρ 0.0–0.15 weaker); A > 1 reversal survives, earlier and steadier (first positive at β = 3 on 9 of 10 networks, Facebook β = 1); the dip near β = 10 was a lockstep effect. Oscillating cells 11% → 0.4%.

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
