"""Validity checks for SDGIndex roles: degree-preserving null model and phase-shuffled surrogates.

Both answer the objection that, after performance-based classification, synergy is close to
"same direction" and trade-off to "opposite directions", so that roles could reflect only
trend strength and number of links rather than who is linked to whom.

* ``null_model`` keeps the observed network's nodes, performance directions, each node's
  numbers of sent and received arcs and the multiset of arc weights, and rewires partners at
  random (directed double-edge swaps, no self-loops, no duplicate arcs, no pairs within the
  same SDG). The interaction of a rewired arc between two improving or deteriorating nodes
  follows the classification rule (same direction = synergy, opposite = trade-off); arcs
  touching stable or undetermined nodes keep their original interaction. Roles are then
  recomputed with the same rules. A role that the null reproduces as often as observed says
  little beyond degree and direction.
* ``surrogate_density`` replaces every series by an independent Fourier phase-randomised
  surrogate (same power spectrum and autocorrelation, no synchrony) and counts how many
  cross-SDG pairs pass the selection threshold. With independent series the expected share
  is the nominal level (10%); the excess measures how much association comes from shared
  persistence and trends rather than from co-movement.

Exploratory diagnostics, not significance tests of individual links.
"""
import math
import numpy as np
from scipy import stats

from networks import node_metrics
from performance_ranking import highlight_groups

SCORES = dict(contributors='colab', dependent_contributors='tradeoff_received_from_backward',
              isolated_beneficiaries='tradeoff_received_from_backward', exposed='neglect',
              transmission_bridges='bridge_flow', deterioration_relays='relay_flow')
INTERFACE = ('forward', 'backward')


def goal(node_id):
    return node_id.split('.', 1)[0]


def role_sets(highlights):
    return {g['id']: {row[1] for row in g['rows']} for g in highlights}


def _interaction(direction, source, target, original):
    da, db = direction[source], direction[target]
    if da in INTERFACE and db in INTERFACE:
        return 'synergy' if da == db else 'trade-off'
    return original


def rewire(edges, direction, rng, swaps=10):
    """Directed double-edge swaps preserving out- and in-degree. Returns new edge dicts."""
    arcs = [[e['source'], e['target'], e['weight'], e['interaction']] for e in edges]
    present = {(a[0], a[1]) for a in arcs}
    m = len(arcs)
    for _ in range(swaps * m):
        i, j = rng.integers(m, size=2)
        if i == j:
            continue
        (a, b, *_), (c, d, *_) = arcs[i], arcs[j]
        if a == d or c == b or (a, d) in present or (c, b) in present:
            continue
        if goal(a) == goal(d) or goal(c) == goal(b):
            continue
        present -= {(a, b), (c, d)}
        present |= {(a, d), (c, b)}
        arcs[i][1], arcs[j][1] = d, b
    return [dict(source=s, target=t, weight=w, interaction=_interaction(direction, s, t, k))
            for s, t, w, k in arcs]


def _roles(nodes, edges, **options):
    """Recompute Colab, Neglect and interface measures on ``edges``, then select roles."""
    copies = [dict(n) for n in nodes]
    metrics = node_metrics([n['id'] for n in copies],
                           [dict(TargetA=e['source'], TargetB=e['target'], interaction=e['interaction'],
                                 weight=e['weight']) for e in edges],
                           {n['id']: n['direction'] for n in copies})
    for n in copies:
        n.update(colab=metrics[n['id']]['collaboration'], neglect=metrics[n['id']]['neglect'])
    groups = highlight_groups(copies, edges, **options)
    return role_sets(groups), {n['id']: n for n in copies}


def null_model(nodes, edges, replicates=500, seed=1, **options):
    """Compare observed roles with roles in degree- and direction-preserving rewired networks.

    Returns (summary rows per role, rows per observed role member)."""
    rng = np.random.default_rng(seed)
    direction = {n['id']: n['direction'] for n in nodes}
    observed, obs_nodes = _roles(nodes, edges, **options)
    same = {i: 0 for members in observed.values() for i in members}
    exceed = {(r, i): 0 for r, members in observed.items() for i in members}
    sizes = {r: [] for r in observed}
    overlap = {r: [] for r in observed}
    for _ in range(replicates):
        roles, null_nodes = _roles(nodes, rewire(edges, direction, rng), **options)
        for r, members in observed.items():
            sizes[r].append(len(roles[r]))
            union = members | roles[r]
            overlap[r].append(len(members & roles[r]) / len(union) if union else 1.0)
            field = SCORES[r]
            for i in members:
                same[i] += i in roles[r]
                exceed[r, i] += (null_nodes[i][field] or 0) >= (obs_nodes[i][field] or 0)
    summary = [dict(role=r, observed_members=len(m), null_mean_members=float(np.mean(sizes[r])),
                    mean_jaccard_with_null=float(np.mean(overlap[r])),
                    members_beating_null_p05=sum((exceed[r, i] + 1) / (replicates + 1) < .05 for i in m),
                    replicates=replicates) for r, m in observed.items()]
    members = [dict(role=r, node=i, direction=direction[i], score_field=SCORES[r],
                    observed_score=obs_nodes[i][SCORES[r]],
                    share_null_same_role=same[i] / replicates,
                    p_null_score_ge_observed=(exceed[r, i] + 1) / (replicates + 1))
               for r, m in observed.items() for i in sorted(m)]
    return summary, members


def phase_surrogate(x, rng):
    """Fourier phase randomisation of the finite stretch of ``x`` (NaN elsewhere kept)."""
    out = np.full_like(x, np.nan)
    idx = np.where(np.isfinite(x))[0]
    if len(idx) < 4:
        return out
    v = x[idx[0]:idx[-1] + 1]
    if not np.all(np.isfinite(v)):
        v = np.interp(np.arange(len(v)), np.where(np.isfinite(v))[0], v[np.isfinite(v)])
    f = np.fft.rfft(v - v.mean())
    phases = rng.uniform(0, 2 * np.pi, len(f))
    phases[0] = 0
    if len(v) % 2 == 0:
        phases[-1] = 0
    s = np.fft.irfft(np.abs(f) * np.exp(1j * phases), n=len(v)) + v.mean()
    out[idx[0]:idx[-1] + 1] = s
    out[~np.isfinite(x)] = np.nan
    return out


def _pass_share(matrix, allowed, alpha, method):
    """Share of allowed pairs with p < alpha (pairwise complete, at least 8 points)."""
    x = np.array(matrix)
    passed = total = 0
    for a, b in allowed:
        ok = np.isfinite(x[a]) & np.isfinite(x[b])
        n = int(ok.sum())
        u, v = x[a][ok], x[b][ok]
        if n < 8 or min(np.std(u), np.std(v)) < 1e-12:
            continue
        if method == 'spearman':
            u, v = stats.rankdata(u), stats.rankdata(v)
        r = float(np.clip(np.corrcoef(u, v)[0, 1], -1, 1))
        if r == 0:
            continue
        t = abs(r) * math.sqrt((n - 2) / max(1e-15, 1 - r * r))
        total += 1
        passed += 2 * stats.t.sf(t, n - 2) < alpha
    return passed / total if total else None, total


def surrogate_density(series, goal_of, replicates=200, seed=1, alpha=.1, method='pearson', basis='levels'):
    """Observed vs surrogate share of cross-SDG pairs passing p < alpha."""
    rng = np.random.default_rng(seed)
    codes = sorted(series)
    allowed = [(i, j) for i in range(len(codes)) for j in range(i + 1, len(codes))
               if goal_of[codes[i]] != goal_of[codes[j]]]
    transform = np.diff if basis == 'changes' else (lambda v: v)
    observed, total = _pass_share([transform(series[c]) for c in codes], allowed, alpha, method)
    shares = []
    for _ in range(replicates):
        sur = [transform(phase_surrogate(series[c], rng)) for c in codes]
        shares.append(_pass_share(sur, allowed, alpha, method)[0])
    shares = np.array(shares)
    return dict(basis=basis, method=method, alpha=alpha, pairs_tested=total, observed_share=observed,
                surrogate_mean_share=float(shares.mean()), surrogate_p95_share=float(np.quantile(shares, .95)),
                excess_over_surrogate=observed - float(shares.mean()),
                p_surrogate_ge_observed=float(((shares >= observed).sum() + 1) / (replicates + 1)),
                replicates=replicates)
