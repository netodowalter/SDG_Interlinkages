"""Undirected reading of the interface: which improving and deteriorating targets concentrate trade-offs.

Correlation has no direction, so each significant pair is one tie. For ties between an improving and a
deteriorating node classified as trade-offs, each node's trade-off degree is the sum of |r| over those
ties. Degrees are min-max normalised to 0-1 within each side separately. A linked pair's score is
normalised degree of the improving node + normalised degree of the deteriorating node + |r| of the tie
(maximum 3). Unlinked pairs do not enter. The highest score marks the connection most worth studying.
"""
from collections import defaultdict

INTERFACE = ('forward', 'backward')


def tradeoff_pairs(direction, ties):
    """``direction``: node -> progress direction. ``ties``: iterable of (a, b, interaction, weight).

    Returns (sides, pairs): sides maps 'forward'/'backward' to rows ordered by degree; pairs is the list
    of scored linked pairs, highest first."""
    weight = {}
    for a, b, interaction, w in ties:
        if interaction != 'trade-off' or {direction.get(a), direction.get(b)} != set(INTERFACE):
            continue
        good, bad = (a, b) if direction[a] == 'forward' else (b, a)
        weight[good, bad] = max(weight.get((good, bad), 0.0), abs(float(w)))
    degree = defaultdict(float)
    for (good, bad), w in weight.items():
        degree[good] += w
        degree[bad] += w
    sides, scaled = {}, {}
    for side in INTERFACE:
        ids = sorted((i for i in degree if direction[i] == side), key=lambda i: (-degree[i], i))
        lo, hi = (min(degree[i] for i in ids), max(degree[i] for i in ids)) if ids else (0, 0)
        for i in ids:
            scaled[i] = (degree[i] - lo) / (hi - lo) if hi > lo else 1.0
        sides[side] = [dict(rank=k, node=i, tradeoff_degree=degree[i], normalised=scaled[i])
                       for k, i in enumerate(ids, 1)]
    rank = {row['node']: row['rank'] for rows in sides.values() for row in rows}
    pairs = [dict(improving=g, deteriorating=b, improving_rank=rank[g], deteriorating_rank=rank[b],
                  improving_normalised=scaled[g], deteriorating_normalised=scaled[b], tie=w,
                  score=scaled[g] + scaled[b] + w) for (g, b), w in weight.items()]
    pairs.sort(key=lambda p: (-p['score'], p['improving'], p['deteriorating']))
    return sides, pairs
