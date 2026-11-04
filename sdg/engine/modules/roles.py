"""Network roles at the interface between improving and deteriorating targets.

After performance-based classification, synergies link nodes moving in the same
direction and trade-offs link nodes moving in opposite directions. The roles
below separate what arrives at each node across that interface from what it
passes on. They are exploratory hypotheses, not estimates of causal effects.

Both procedures share these definitions. Each supplies its own ranking rule
(``top``) and its own context criterion (``context``).
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
    'contributors': 'Top Colab among improving nodes meeting the context criterion, excluding top receivers '
                    'of trade-offs from deterioration and top senders of trade-offs to deterioration.',
    'dependent_contributors': 'Top receivers of trade-offs from deteriorating sources that pass at least as '
                              'much synergy weight forward to improving nodes (phi >= 1).',
    'isolated_beneficiaries': 'Top receivers of trade-offs from deteriorating sources that pass less synergy '
                              'weight forward to improving nodes than they receive (phi < 1).',
    'exposed': 'Top Neglect among deteriorating nodes meeting the context criterion, excluding top senders '
               'of synergies from deterioration, transmission bridges and relays.',
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


def select_roles(top, context, ratio):
    """Return {role id: set of node ids}.

    ``top(field, direction)`` returns the selected top set of positive values of
    ``field`` among nodes with that performance direction. ``context(role)``
    returns the set of nodes meeting the procedure's context criterion for
    'contributors' or 'exposed'. ``ratio`` maps node id to forward_ratio (phi).
    Intersections are not refilled.
    """
    colab, receivers = top('colab', FORWARD), top('tradeoff_received_from_backward', FORWARD)
    cost = top('tradeoff_sent_to_backward', FORWARD)
    isolated = {i for i in receivers if ratio[i] is not None and ratio[i] < ISOLATION_RATIO}
    neglect, senders = top('neglect', BACKWARD), top('backward_synergy_sent', BACKWARD)
    bridges = top('bridge_flow', BACKWARD)
    relays = top('relay_flow', BACKWARD) - bridges
    return dict(
        contributors=(colab & context('contributors')) - receivers - cost,
        dependent_contributors=receivers - isolated,
        isolated_beneficiaries=isolated,
        exposed=(neglect & context('exposed')) - senders - bridges - relays,
        transmission_bridges=bridges,
        deterioration_relays=relays,
    )
