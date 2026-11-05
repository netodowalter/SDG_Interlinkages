"""Network roles at the interface between improving and deteriorating targets.

After performance-based classification, synergies link nodes moving in the same
direction and trade-offs link nodes moving in opposite directions. The roles
below separate what arrives at each node across that interface from what it
passes on. They are exploratory hypotheses, not estimates of causal effects.

Both procedures share these definitions and supply their own ranking rule
(``top``). Context (semantic ambitiousness in IGES/JRC; conditional years to
target or to zero in SDGIndex) does not filter roles: it is exported alongside
every selected node to characterise and prioritise within each role.
"""
from collections import defaultdict

FORWARD, BACKWARD = 'forward', 'backward'
# An improving node is isolated when it passes forward less synergy weight than the
# trade-off weight it receives from deteriorating sources (phi < 1). A relative
# cut-off (outside the top senders) is unsuitable in dense networks, where almost
# every receiver also sends substantial synergy.
ISOLATION_RATIO = 1.0

# Edge-derived measures. Weights are absolute coefficients.
MEASURES = (
    'tradeoff_received_from_backward',  # R: improving node, gains associated with losses upstream
    'tradeoff_sent_to_backward',        # improving node, gains associated with losses downstream
    'forward_synergy_sent',             # improving node, synergies passed to improving nodes
    'tradeoff_received_from_forward',   # T+: deteriorating node, cost of gains upstream
    'synergy_received_from_backward',   # S-: deteriorating node, deterioration received
    'synergy_sent_to_backward',         # deteriorating node, deterioration passed on
    'backward_synergy_sent',            # B: deteriorating source, synergy to any destination
    'bridge_flow',                      # T+ x synergy_sent_to_backward
    'relay_flow',                       # S- x synergy_sent_to_backward
    'forward_ratio',                    # phi = forward_synergy_sent / R (None when R = 0)
)

# (id, title, score field, score label, performance direction)
ROLES = (
    ('contributors', 'I-1 · Contributors', 'colab', 'Colab', FORWARD),
    ('dependent_contributors', 'I-2 · Dependent contributors', 'tradeoff_received_from_backward',
     'Trade-off received from deterioration', FORWARD),
    ('isolated_beneficiaries', 'I-3 · Isolated beneficiaries', 'tradeoff_received_from_backward',
     'Trade-off received from deterioration', FORWARD),
    ('exposed', 'D-1 · Exposed targets', 'neglect', 'Neglect', BACKWARD),
    ('transmission_bridges', 'D-2 · Transmission bridges', 'bridge_flow', 'Bridge flow', BACKWARD),
    ('deterioration_relays', 'D-3 · Deterioration relays', 'relay_flow', 'Relay flow', BACKWARD),
)

RULES = {
    'contributors': 'Top Colab among improving nodes, excluding top receivers of trade-offs from '
                    'deterioration and top senders of trade-offs to deterioration.',
    'dependent_contributors': 'Top receivers of trade-offs from deteriorating sources that pass at least as '
                              'much synergy weight forward to improving nodes (phi >= 1).',
    'isolated_beneficiaries': 'Top receivers of trade-offs from deteriorating sources that pass less synergy '
                              'weight forward to improving nodes than they receive (phi < 1).',
    'exposed': 'Top Neglect among deteriorating nodes, excluding top senders of synergies from '
               'deterioration, transmission bridges and relays.',
    'transmission_bridges': 'Top bridge flow: trade-off received from improving sources multiplied by '
                            'synergy sent to deteriorating nodes (all two-step paths improving → k → deteriorating).',
    'deterioration_relays': 'Top relay flow: synergy received from deteriorating sources multiplied by synergy '
                            'sent to deteriorating nodes, excluding transmission bridges.',
}


def interface_measures(direction, edges):
    """Return MEASURES per node.

    ``direction`` maps node id to 'forward', 'backward', 'stable' or 'undetermined'.
    ``edges`` yields (source, target, interaction, weight). Links involving stable
    or undetermined nodes, and self-loops, do not enter interface measures, except
    ``backward_synergy_sent``, which keeps its established definition (synergies
    sent by a deteriorating source to any destination).
    """
    values = {i: dict.fromkeys(MEASURES, 0.0) for i in direction}
    for source, target, interaction, weight in edges:
        if source == target or source not in values or target not in values:
            continue
        w = abs(float(weight))
        da, db = direction[source], direction[target]
        if interaction == 'synergy' and da == BACKWARD:
            values[source]['backward_synergy_sent'] += w
        if da not in (FORWARD, BACKWARD) or db not in (FORWARD, BACKWARD):
            continue
        if interaction == 'trade-off' and da != db:
            if da == BACKWARD:
                values[target]['tradeoff_received_from_backward'] += w
            else:
                values[source]['tradeoff_sent_to_backward'] += w
                values[target]['tradeoff_received_from_forward'] += w
        elif interaction == 'synergy' and da == db:
            if da == FORWARD:
                values[source]['forward_synergy_sent'] += w
            else:
                values[source]['synergy_sent_to_backward'] += w
                values[target]['synergy_received_from_backward'] += w
    for i, v in values.items():
        v['bridge_flow'] = v['tradeoff_received_from_forward'] * v['synergy_sent_to_backward']
        v['relay_flow'] = v['synergy_received_from_backward'] * v['synergy_sent_to_backward']
        received = v['tradeoff_received_from_backward']
        v['forward_ratio'] = v['forward_synergy_sent'] / received if received > 0 else None
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
SENT = ('colab', 'tradeoff_sent_to_backward', 'forward_synergy_sent', 'synergy_sent_to_backward',
        'backward_synergy_sent')
RECEIVED = ('neglect', 'tradeoff_received_from_backward', 'tradeoff_received_from_forward',
            'synergy_received_from_backward')
TWO_STEP = ('bridge_flow', 'relay_flow')


def ponderate(node, shares):
    """Divide each measure by the node's relative share of sent or received links (NT Dinte 77, eq. 1).

    The relative share (share x number of nodes) gives the same ordering as the share itself
    and keeps values comparable with the unweighted version. Two-step flows combine a received and a sent component and are divided by both
    shares. The forward ratio phi is a ratio of flows at the same node and is left
    unchanged. A measure whose share is zero is zero.
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
    for field in TWO_STEP:
        if field in node:
            result[field] = divide(node[field], shares['relative_out'] * shares['relative_in'])
    return result


def select_roles(top, ratio, isolation='ratio'):
    """Return {role id: set of node ids}.

    ``top(field, direction)`` returns the selected top set of positive values of
    ``field`` among nodes with that performance direction. ``ratio`` maps node
    id to forward_ratio (phi).
    Intersections are not refilled. ``isolation='zero'`` counts as isolated only receivers that
    pass no synergy forward (phi == 0), a stricter alternative to phi < 1.
    """
    colab, receivers = top('colab', FORWARD), top('tradeoff_received_from_backward', FORWARD)
    cost = top('tradeoff_sent_to_backward', FORWARD)
    cut = (lambda r: r == 0) if isolation == 'zero' else (lambda r: r < ISOLATION_RATIO)
    isolated = {i for i in receivers if ratio[i] is not None and cut(ratio[i])}
    neglect, senders = top('neglect', BACKWARD), top('backward_synergy_sent', BACKWARD)
    bridges = top('bridge_flow', BACKWARD)
    relays = top('relay_flow', BACKWARD) - bridges
    return dict(
        contributors=colab - receivers - cost,
        dependent_contributors=receivers - isolated,
        isolated_beneficiaries=isolated,
        exposed=neglect - senders - bridges - relays,
        transmission_bridges=bridges,
        deterioration_relays=relays,
    )
