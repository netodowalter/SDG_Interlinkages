"""Two-step interface: a display-only projection of the complete directed graph."""
from math import ceil, sqrt

NOTE = 'Note: This experimental layout is a more reader-friendly visual representation designed to place the study’s targets of interest more centrally in the network.'


def two_step_scores(nodes, edges):
    by_id = {n['id']: n for n in nodes}
    pressure = dict.fromkeys(by_id, 0.0)
    sending = dict.fromkeys(by_id, 0.0)
    for e in edges:
        a, b = e['source'], e['target']
        da, db = by_id[a].get('direction'), by_id[b].get('direction')
        if da not in ('forward', 'backward') or db not in ('forward', 'backward') or a == b:
            continue
        w = abs(e['weight'])
        if e['interaction'] == 'trade-off' and da != db:
            pressure[b] += w
        elif e['interaction'] == 'synergy' and da == db:
            sending[a] += w
    # A weighted (_pond) graph divides the two-step flow by the node's sent x received link shares.
    scale = {i: n.get('interface_scale', 1) or 0 for i, n in by_id.items()}
    return {i: pressure[i]*sending[i]/scale[i] if scale[i] > 0 else 0.0 for i in by_id}


def interface_positions(nodes, edges, sizes, baseline, bounds):
    import numpy as np
    scores = two_step_scores(nodes, edges)
    if not any(scores.values()):
        return baseline
    x0, y0, x1, y1 = bounds
    step = max(sizes.values(), default=76)+26
    cols, rows = int((x1-x0)//step), int((y1-y0)//step)
    # Enlarge the canvas coordinate space for exceptionally large graphs.
    if cols*rows < len(nodes):
        rows = ceil(len(nodes)/max(1, cols))
        step = min((x1-x0)/max(1,cols), (y1-y0)/rows)
        if step < max(sizes.values())+18:
            raise ValueError('Too many nodes for a readable fixed-size interface PNG.')
    slots = [(x0+(c+.5)*(x1-x0)/cols, y0+(r+.5)*(y1-y0)/rows)
             for r in range(rows) for c in range(cols)]
    desired = {}
    for direction, sign in [('forward', -1), ('backward', 1)]:
        cohort = [n['id'] for n in nodes if n.get('direction') == direction]
        ordered = sorted(cohort, key=lambda i: (baseline[i][1], i))
        for k, i in enumerate(ordered):
            below = sum(scores[j] < scores[i] for j in cohort)
            equal = sum(scores[j] == scores[i] for j in cohort)
            rank = (below+(equal-1)/2)/max(1,len(cohort)-1)
            desired[i] = (.5+sign*(.10+.90*(1-rank))*.46, .08+.84*k/max(1,len(cohort)-1))
    for n in nodes:
        desired.setdefault(n['id'], (.5, .03))
    result = {}
    for i in sorted(desired, key=lambda i: (-scores[i], i)):
        dx, dy = desired[i]
        index = min(range(len(slots)), key=lambda k:
                    4*((slots[k][0]-x0)/(x1-x0)-dx)**2+((slots[k][1]-y0)/(y1-y0)-dy)**2)
        result[i] = np.array(slots.pop(index))
    return result
