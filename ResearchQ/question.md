# Research Question

## Question

Weak PD (R = 1, T = b, S = P = 0) played by Bush–Mosteller (BM) aspiration learners with averaged payoffs on real networks. How much do (1) a player's degree, (2) fixed partners and (3) network structure beyond the degree sequence change cooperation, and how does each depend on learning sensitivity β and aspiration A = a·b?

"Weak" is the game's name (S = P = 0, the mildest PD), not weak selection.

## Why

- BM = reinforcement learning: players judge their own payoff against an aspiration; nobody copies anyone. Cooperation on networks is mostly studied with imitation on synthetic graphs.
- Ezaki et al. 2016 (lattice): β changes BM cooperation. Ezaki & Masuda 2017 (rings, one β): fixed partners help BM, effect depends on degree k and b/c.
- Earlier work finds RL cooperation largely insensitive to topology (Cimini & Sánchez 2014; Amaral et al. 2016). Here: real networks, node level, across β and A.

## Claims from experiment 1 (5 networks, 90,000 runs; numbers in README.md)

Stated with their conditions (checked 2026-10-10). A ≤ 1 = a cooperator can be satisfied (main regime).

- **C1. Low-degree players cooperate more than hubs.** A ≤ 1: Spearman(node cooperation, degree) −0.28 to −0.77 on all 5 networks (LastFM: top-1% hubs 0.17 vs degree-1 nodes 0.45). Exceptions: Facebook at β ≥ 10 (~0); reverses at A > 1, β ≥ 3 (+0.05 to +0.38); no pattern at a = 0.
  - Proposed mechanism: with averaged payoffs and a share x of cooperating neighbours, a cooperator earns x (satisfied iff x ≥ a·b), a defector b·x (satisfied iff x ≥ a). A hub sees x ≈ its neighbourhood's mean. If a ≤ x < a·b, cooperating disappoints and defecting satisfies → hubs drift to D. A degree-1 player with one cooperating partner gets 1 ≥ A and stays C. Not yet tested directly.
  - Wording: "in the model, on real network structure". Not a claim about real people.
  - Open: local clustering is higher at low-degree nodes, so degree and clustering are not yet separated.
- **C2. Fixed partners help BM, more at high β.** real − shuffled: +0.008 to +0.029 at β = 0.1 → +0.037 to +0.058 at β = 100, all 5 networks (A ≤ 1). Growth with β not reported before as far as found (Ezaki & Masuda 2017 used one β).
  - Caveat: shuffling seats also removes each player's fixed degree, so part may be a degree effect. Tested in the extension by the same-degree shuffle (H7).
  - "More than imitators" is not tested here: do not claim it.
- **C3. Structure beyond the degree sequence matters little.** real − degseq: |diff| ≤ 0.009 at β ≤ 1, ≤ +0.024 at β ≥ 3. Fits Cimini & Sánchez 2014, Amaral et al. 2016 (confirmation on real networks, not new alone).
  - Not "shuffling doesn't matter": shuffled seats do matter (C2). Rewiring links at fixed degrees barely does.
  - "Degree spread matters" (degseq − ER): not in experiment 1; measured in the extension (H4).

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
