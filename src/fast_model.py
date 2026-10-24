"""Fast numpy version of the BM model in model.py, used by the main sweep (run.py).

Same rules as BMAgent + CooperationModel (weak PD, average payoff, synchronous
rounds), but all players live in arrays: entry i = the player on node i. One round
is a few array operations instead of a Python loop over every player and neighbour
(~10-20x faster). model.py stays the readable reference; check_fast_model.py
checks that the two agree.

Random numbers are drawn differently from the Mesa version, so the same seed gives
a different run. Averages over seeds must match, single runs will not.
"""
import math

import networkx as nx
import numpy as np


def neighbour_matrix(G):
    """Sparse adjacency matrix A (A[i, j] = 1 if i and j are neighbours) and degrees.
    Nodes must be labelled 0..n-1 (see networks.py), so row i = node i."""
    n = G.number_of_nodes()
    A = nx.to_scipy_sparse_array(G, nodelist=range(n), format="csr", dtype=float)
    degree = np.asarray(A.sum(axis=1)).ravel()
    return A, degree


def weak_pd_payoffs(A, degree, coop, b):
    """Average weak PD payoff of every player. coop: True where the player cooperated.
    Only cooperating neighbours pay anything: 1 to a C player, b to a D player."""
    n_coop_neighbours = A @ coop.astype(float)  # row i = cooperators next to node i
    total = np.where(coop, n_coop_neighbours * 1.0, n_coop_neighbours * b)
    return total / degree


def bm_update(p, coop, payoff, beta, aspiration):
    """Bush-Mosteller update for all players at once (same four cases as BMAgent.update)."""
    stimulus = np.tanh(beta * (payoff - aspiration))
    # cooperated: satisfied -> p moves up towards 1, unsatisfied -> down towards 0
    if_cooperated = np.where(stimulus >= 0, p + (1 - p) * stimulus, p + p * stimulus)
    # defected: satisfied -> p moves down towards 0, unsatisfied -> up towards 1
    if_defected = np.where(stimulus >= 0, p - p * stimulus, p - (1 - p) * stimulus)
    return np.where(coop, if_cooperated, if_defected)


def run_bm(A, degree, b, beta, aspiration, epsilon, steps, record_from=0,
           initial_coop=0.5, shuffle_seats=False, seat_groups=None, update_fraction=1.0,
           record_every=1, seed=None):
    """One BM run. Same arguments as CooperationModel (agent_type="bm").
    seat_groups (with shuffle_seats): list of node lists (networks.same_degree_groups);
    players are then re-seated only within their group. None = any seat.
    update_fraction: each round every player updates p only with this probability
    (1.0 = everyone every round, the synchronous default). < 1 breaks the lockstep in
    which all players switch together (desynchronised check, 2026-10-13).
    record_every: node_cooperation counts only every record_every-th round from
    record_from on (measurement only, no rule change; 1 = every round, as before).
    Used by async_scan.py so that long runs at small update_fraction average the same
    number of actions per player (added 2026-10-23).

    Returns:
        curve: cooperation fraction in every round (length steps)
        p: final cooperation probability of every player
        node_cooperation: per player, fraction of counted rounds spent cooperating
    """
    if not 0 < update_fraction <= 1:
        raise ValueError("update_fraction must be in (0, 1]")
    if record_every < 1:
        raise ValueError("record_every must be at least 1")
    rng = np.random.default_rng(seed)
    n = A.shape[0]
    group_arrays = []
    if seat_groups is not None:
        for group in seat_groups:
            group_arrays.append(np.array(group))
    p = np.full(n, float(initial_coop))
    coop_rounds = np.zeros(n)  # rounds spent cooperating, from record_from on
    rounds_counted = 0
    curve = np.zeros(steps)

    for t in range(steps):
        # with probability epsilon the player slips and plays the opposite of what it
        # intended (Ezaki & Masuda 2017)
        prob_cooperate = (1 - epsilon) * p + epsilon * (1 - p)
        coop = rng.random(n) < prob_cooperate
        payoff = weak_pd_payoffs(A, degree, coop, b)

        curve[t] = coop.mean()
        if t >= record_from and (t - record_from) % record_every == 0:
            rounds_counted += 1
            coop_rounds += coop

        new_p = bm_update(p, coop, payoff, beta, aspiration)
        if update_fraction < 1:
            # only a random part of the population updates this round; the rest keep p.
            # Drawn only here, so update_fraction = 1 gives the same random numbers as
            # before (experiment-1 and extension runs reproduce bit-identically)
            updates_now = rng.random(n) < update_fraction
            p = np.where(updates_now, new_p, p)
        else:
            p = new_p

        if shuffle_seats:
            # players take new random seats: reorder everything that belongs to a player
            if seat_groups is None:
                new_order = rng.permutation(n)
            else:
                # only swap seats inside a degree group: seat i gets a player from its own group
                new_order = np.arange(n)
                for group in group_arrays:
                    new_order[group] = group[rng.permutation(len(group))]
            p = p[new_order]
            coop_rounds = coop_rounds[new_order]

    node_cooperation = coop_rounds / rounds_counted
    return curve, p, node_cooperation


def run_bm_sequential(A, degree, b, beta, aspiration, epsilon, sweeps, record_from=0,
                      initial_coop=0.5, seating="fixed", seat_groups=None, seed=None):
    """BM with fully asynchronous updating: one player at a time (added 2026-10-24).

    A sweep = n single updates; each update: pick a random player, it and its partners
    act (partners from their current p), it gets its average payoff and updates its p.
    Nobody else changes p in between, so no two players ever update together. This is
    the limit of run_bm's update_fraction -> 0 (there, everyone acts every round but
    almost nobody updates). Time is counted in sweeps: ~1 update per player per sweep,
    so 1,500 sweeps = the same learning as 1,500 synchronous rounds.

    seating: "fixed" (static network), "full" (re-seated at random before every update:
    a random seat, partners = random players) or "samedeg" (a random seat in the player's
    own degree group; each partner a random player from that seat's group). These are
    the update_fraction -> 0 limits of shuffle_seats without / with seat_groups.

    Recording: at the end of every sweep everyone acts once (one sampled action per player),
    as async_scan.py samples every 1/f rounds.
    Returns curve (cooperation per sweep), p, node_cooperation (per player).
    """
    rng = np.random.default_rng(seed)
    n = A.shape[0]
    starts = A.indptr
    neighbour_seats = A.indices
    # samedeg: group_of[seat] = its degree group; all groups' members in one array,
    # group g = all_members[group_start[g] : group_start[g] + group_size[g]]
    group_of = np.zeros(n, dtype=int)
    group_members = []
    all_members = np.zeros(0, dtype=int)
    group_start = np.zeros(0, dtype=int)
    group_size = np.zeros(0, dtype=int)
    if seating == "samedeg":
        for g, group in enumerate(seat_groups):
            members = np.array(group)
            group_members.append(members)
            group_of[members] = g
        all_members = np.concatenate(group_members)
        group_size = np.array([len(members) for members in group_members])
        group_start = np.concatenate([[0], np.cumsum(group_size)[:-1]])
    p = np.full(n, float(initial_coop))
    coop_rounds = np.zeros(n)
    sweeps_counted = 0
    curve = np.zeros(sweeps)

    for sweep in range(sweeps):
        for player in rng.integers(n, size=n):
            # where the player sits for this update
            if seating == "fixed":
                seat = player
            elif seating == "full":
                seat = rng.integers(n)
            else:
                own_group = group_members[group_of[player]]
                seat = own_group[rng.integers(len(own_group))]
            seats_next_door = neighbour_seats[starts[seat]:starts[seat + 1]]
            # who sits next door
            if seating == "fixed":
                partners = seats_next_door
            elif seating == "full":
                partners = rng.integers(n, size=len(seats_next_door))
            else:
                # each seat next door holds a random player from that seat's degree group
                groups_next_door = group_of[seats_next_door]
                pick = (rng.random(len(seats_next_door)) * group_size[groups_next_door]).astype(int)
                partners = all_members[group_start[groups_next_door] + pick]
            partner_p = p[partners]
            partner_coop = rng.random(len(partners)) < (1 - epsilon) * partner_p + epsilon * (1 - partner_p)
            n_coop = int(partner_coop.sum())
            own_p = p[player]
            cooperated = rng.random() < (1 - epsilon) * own_p + epsilon * (1 - own_p)
            if cooperated:
                payoff = n_coop / len(partners)
            else:
                payoff = n_coop * b / len(partners)
            stimulus = math.tanh(beta * (payoff - aspiration))
            # same four cases as bm_update
            if cooperated:
                if stimulus >= 0:
                    p[player] = own_p + (1 - own_p) * stimulus
                else:
                    p[player] = own_p + own_p * stimulus
            else:
                if stimulus >= 0:
                    p[player] = own_p - own_p * stimulus
                else:
                    p[player] = own_p - (1 - own_p) * stimulus
        # record: everyone acts once
        actions = rng.random(n) < (1 - epsilon) * p + epsilon * (1 - p)
        curve[sweep] = actions.mean()
        if sweep >= record_from:
            sweeps_counted += 1
            coop_rounds += actions

    node_cooperation = coop_rounds / max(sweeps_counted, 1)
    return curve, p, node_cooperation
