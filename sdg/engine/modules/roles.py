"""Network roles at the interface and within improving and deteriorating subsystems.

After performance-based classification, synergies link nodes moving in the same
direction and trade-offs link nodes moving in opposite directions. The six roles
below measure the trade-offs sent and received across the interface between the
improving (I) and deteriorating (D) subsystems and the synergy degree within each
subsystem. They are exploratory hypotheses, not estimates of causal effects.

Both procedures share these definitions and supply their own ranking rule
(``top``). Each role lists its three highest positive values, with no exclusions
and no backfilling. Context (semantic ambitiousness in IGES/JRC; conditional
years to target or to zero in SDGIndex) does not filter roles: it is exported
alongside every selected node to characterise and prioritise within each role.
"""

FORWARD, BACKWARD = 'forward', 'backward'

# Each role lists only its three highest-ranked nodes, selected independently
# without exclusions or backfilling: a node may hold more than one role.
ROLE_TOP = 3

# Edge-derived measures. Weights are absolute coefficients.
MEASURES = (
    'tradeoff_sent_to_backward',        # Improvement sender: trade-off sent from i in I to D
    'tradeoff_received_from_backward',  # Improvement receiver: trade-off received by i in I from D
    'forward_synergy_received',         # synergy received by i in I from I
    'forward_synergy_sent',             # synergy sent by i in I to I
    'forward_synergy_degree',           # Improvement relay: synergy degree of i within I (in + out)
    'tradeoff_sent_to_forward',         # Deterioration sender: trade-off sent from k in D to I
    'tradeoff_received_from_forward',   # Deterioration receiver: trade-off received by k in D from I
    'synergy_received_from_backward',   # synergy received by k in D from D
    'synergy_sent_to_backward',         # synergy sent by k in D to D
    'backward_synergy_degree',          # Deterioration relay: synergy degree of k within D (in + out)
)

# (id, title, score field, score label, performance direction)
ROLES = (
    ('improvement_sender', 'Improvement sender', 'tradeoff_sent_to_backward',
     'Trade-off sent to deterioration', FORWARD),
    ('improvement_receiver', 'Improvement receiver', 'tradeoff_received_from_backward',
     'Trade-off received from deterioration', FORWARD),
    ('improvement_relay', 'Improvement relay', 'forward_synergy_degree',
     'Synergy degree within improvement', FORWARD),
    ('deterioration_sender', 'Deterioration sender', 'tradeoff_sent_to_forward',
     'Trade-off sent to improvement', BACKWARD),
    ('deterioration_receiver', 'Deterioration receiver', 'tradeoff_received_from_forward',
     'Trade-off received from improvement', BACKWARD),
    ('deterioration_relay', 'Deterioration relay', 'backward_synergy_degree',
     'Synergy degree within deterioration', BACKWARD),
)

RULES = {
    'improvement_sender': 'Three highest senders of trade-off weight from improving nodes (i in I) to deteriorating nodes (D).',
    'improvement_receiver': 'Three highest receivers of trade-off weight at improving nodes (i in I) from deteriorating nodes (D).',
    'improvement_relay': 'Three highest synergy degrees (incoming plus outgoing synergy weight) of improving nodes (i in I) within I.',
    'deterioration_sender': 'Three highest senders of trade-off weight from deteriorating nodes (k in D) to improving nodes (I).',
    'deterioration_receiver': 'Three highest receivers of trade-off weight at deteriorating nodes (k in D) from improving nodes (I).',
    'deterioration_relay': 'Three highest synergy degrees (incoming plus outgoing synergy weight) of deteriorating nodes (k in D) within D.',
}


def interface_measures(direction, edges):
    """Return MEASURES per node.

    ``direction`` maps node id to 'forward', 'backward', 'stable' or 'undetermined'.
    ``edges`` yields (source, target, interaction, weight). Links involving stable
    or undetermined nodes, and self-loops, do not enter interface measures.
    """
    values = {i: dict.fromkeys(MEASURES, 0.0) for i in direction}
    for source, target, interaction, weight in edges:
        if source == target or source not in values or target not in values:
            continue
        w = abs(float(weight))
        da, db = direction[source], direction[target]
        if da not in (FORWARD, BACKWARD) or db not in (FORWARD, BACKWARD):
            continue
        if interaction == 'trade-off' and da != db:
            if da == FORWARD:
                values[source]['tradeoff_sent_to_backward'] += w
                values[target]['tradeoff_received_from_forward'] += w
            else:
                values[source]['tradeoff_sent_to_forward'] += w
                values[target]['tradeoff_received_from_backward'] += w
        elif interaction == 'synergy' and da == db:
            if da == FORWARD:
                values[source]['forward_synergy_sent'] += w
                values[target]['forward_synergy_received'] += w
            else:
                values[source]['synergy_sent_to_backward'] += w
                values[target]['synergy_received_from_backward'] += w
    for v in values.values():
        v['forward_synergy_degree'] = v['forward_synergy_received'] + v['forward_synergy_sent']
        v['backward_synergy_degree'] = v['synergy_received_from_backward'] + v['synergy_sent_to_backward']
    return values


def link_shares(ids, edges):
    """NT Dinte 77 link-share factor, P_i = L_i / sum_j L_j, for sent and received arcs.

    Counts every arc of the final network between listed nodes, whatever its type.
    Returns {id: dict(links_out, links_in, share_out, share_in, relative_out, relative_in)}.
    ``relative_*`` = share x number of nodes, so a node with the mean number of links has 1.
    Dividing by the relative share orders nodes exactly as dividing by the share, but keeps
    weighted values on the scale of the unweighted ones.
    """
    ids = set(ids)
    out, inc = dict.fromkeys(ids, 0), dict.fromkeys(ids, 0)
    total = 0
    for source, target, *_ in edges:
        if source in ids and target in ids and source != target:
            out[source] += 1
            inc[target] += 1
            total += 1
    n = len(ids)
    result = {}
    for i in ids:
        share_out = out[i] / total if total else 0.0
        share_in = inc[i] / total if total else 0.0
        result[i] = dict(links_out=out[i], links_in=inc[i], share_out=share_out, share_in=share_in,
                         relative_out=share_out * n, relative_in=share_in * n)
    return result


# Which link-count share divides each measure in the weighted (_pond) version.
SENT = ('colab', 'tradeoff_sent_to_backward', 'tradeoff_sent_to_forward',
        'forward_synergy_sent', 'synergy_sent_to_backward')
RECEIVED = ('neglect', 'tradeoff_received_from_backward', 'tradeoff_received_from_forward',
            'forward_synergy_received', 'synergy_received_from_backward')


def ponderate(node, shares):
    """Divide each measure by the node's relative share of sent or received links (NT Dinte 77, eq. 1).

    The relative share (share x number of nodes) gives the same ordering as the share itself
    and keeps values comparable with the unweighted version. Internal synergy degrees sum the
    weighted received and sent components within the subsystem. A measure whose share is zero is zero.
    """
    def divide(value, share):
        return value / share if share > 0 and value is not None else 0.0
    result = dict(node, **shares)
    for field in SENT:
        if field in node:
            result[field] = divide(node[field], shares['relative_out'])
    for field in RECEIVED:
        if field in node:
            result[field] = divide(node[field], shares['relative_in'])
    if 'forward_synergy_degree' in node:
        result['forward_synergy_degree'] = result.get('forward_synergy_received', 0.0) + result.get('forward_synergy_sent', 0.0)
    if 'backward_synergy_degree' in node:
        result['backward_synergy_degree'] = result.get('synergy_received_from_backward', 0.0) + result.get('synergy_sent_to_backward', 0.0)
    return result


def select_roles(top, n=None):
    """Return {role id: set of node ids}.

    ``top(field, direction, n=None)`` returns the ``n`` highest positive values of
    ``field`` among nodes with that performance direction. Every role lists at most
    ``ROLE_TOP`` nodes (or ``n``), ranked by its own score, with no exclusions and
    no backfilling. Roles are selected independently, so a node can hold more than one.
    """
    k = n or ROLE_TOP
    return {slug: top(field, direction, k) for slug, _, field, _, direction in ROLES}
