# Project rules

Experiment 1: Bush–Mosteller (BM) learners, weak PD, real networks vs degree-preserving rewirings vs shuffled seats. Question + claims in `ResearchQ/question.md`. Decisions in `ResearchQ/design.md`. Read both before coding. `README.md` = what the mentor reads (what was run, results).

**Log every new decision, dated, in the Decision log of `ResearchQ/design.md` when it is made** (and update question.md if it changes the question, claims or hypotheses).

Scope: build on the experiment-1 claims (hubs defect, fixed partners, structure beyond degree). No new research directions unless the user asks. Fermi, accumulated payoffs and sweep v2 live in `../Experimentation`, not here.

## Communication

- Sacrifice grammar for concision. Short fragments ok.

## Code

- Undergrad-readable. Plain loops, plain functions, descriptive names.
- No clever one-liners, no nested comprehensions, no metaprogramming, no fancy abstractions.
- Libraries: mesa + networkx for simulation. numpy/pandas/matplotlib/scipy ok for data and plots. Nothing exotic.
- Exception: sweep runs use numpy (`fast_model.py`) for speed. Mesa `model.py` stays the reference; any rule change goes in both, then rerun `check_fast_model.py` and `test_model.py`.
- Short comments saying why, not what.
- Versions pinned in requirements.txt. Venv: Python 3.12+ (`py -3.14 -m venv .venv`). No venv here yet: `../Experimentation/.venv` works.
- Run scripts from project root: `python src/run.py`.

## Layout (keep flat)

```
BM-PD-Exploration/
  CLAUDE.md, README.md, requirements.txt, report_extension.txt + report_desync.txt (reports for the mentor)
  ResearchQ/        question.md (question, claims, hypotheses), design.md (decisions, history)
  data/             real edge lists (10) + synthetic/ (rewirings, ER/BA/WS; generated once, fixed)
  src/              ALL code, flat
    networks.py       load + clean graphs, synthetic equivalents, topology table
    model.py          Mesa reference model (readable rules; also has Fermi, unused here)
    fast_model.py     numpy BM used by run.py
    check_fast_model.py  fast_model vs model: exact + 20-seed comparison
    test_model.py     asserts for model.py
    validate_bm.py    BM vs Ezaki & Masuda 2017 rings
    pilot.py          coarse beta x A x b scan on LastFM (chose the grid)
    run.py            the sweep (--more: 5 added networks, --test: tiny)
    analyze.py        diagnostics, real-shuffled, real-degseq, node level
    band_test.py      C1 mechanism test 1: hub defection vs the band rule -> results/band_test.csv
    async_scan.py     update_fraction 1-0.1 at equal updates per player (mentor) -> results/async_scan_*
    plot_graphs.py    network drawings -> graphs/
  graphs/           one png per original real graph
  results/          sweep_runs.csv (exp 1), sweep_more_runs.csv (added networks + all samedeg/ER/BA/WS), sweep_desync_runs.csv (desync check; same run_ids as sync twins, never merge), tables, figures
```

- Scripts import each other directly (`from networks import ...`). No packages, no `__init__.py`.
- Split a file only when it passes ~300 lines. No utils grab-bag.
- Network names: no `_` (run.py/networks.py split graph names on it).

## Git

- Remote: https://github.com/An1sh-R/BM-PD-Exploration.git (main). The mentor sees this repo.
- Commit at milestones (finished, checked work). Short message, what and why. Push only when the user says.
- Never commit: `.venv/`, `results/*_nodes/` (per-node files, large), logs.
