"""Interface roles: the worked example of the methodological article, in both procedures."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sdg/engine/modules'))
from roles import interface_measures, link_shares, ponderate
from performance_ranking import highlight_groups as sdg_highlights
from progress import highlight_groups as iges_highlights

# Eight hypothetical targets: A-D deteriorating, E-H improving (article, Section 6).
DIRECTION = dict(A='backward', B='backward', C='backward', D='backward',
                 E='forward', F='forward', G='forward', H='forward')
EDGES = [('A', 'B', 'synergy', .8), ('A', 'C', 'synergy', .5), ('B', 'C', 'synergy', .7),
         ('C', 'D', 'synergy', .6), ('B', 'D', 'synergy', .4),
         ('E', 'F', 'synergy', .8), ('F', 'E', 'synergy', .5), ('E', 'H', 'synergy', .6),
         ('E', 'B', 'trade-off', .6), ('F', 'A', 'trade-off', .4), ('H', 'D', 'trade-off', .3),
         ('D', 'G', 'trade-off', .7), ('C', 'G', 'trade-off', .6), ('D', 'E', 'trade-off', .5)]
EXPECTED = dict(contributors=set(), dependent_contributors={'E'}, isolated_beneficiaries={'G'},
                exposed={'D'}, transmission_bridges={'A', 'B'}, deterioration_relays={'B', 'C'})


def colab_neglect():
    colab = dict.fromkeys(DIRECTION, 0.0)
    neglect = dict.fromkeys(DIRECTION, 0.0)
    for a, b, kind, w in EDGES:
        colab[a] += w if kind == 'synergy' else -w
        if kind == 'trade-off' or DIRECTION[a] == 'backward':
            neglect[b] += w
    return colab, neglect


class InterfaceRoles(unittest.TestCase):
    def test_measures(self):
        m = interface_measures(DIRECTION, EDGES)
        self.assertAlmostEqual(m['A']['bridge_flow'], .4 * 1.3)
        self.assertAlmostEqual(m['B']['bridge_flow'], .6 * 1.1)
        self.assertAlmostEqual(m['C']['bridge_flow'], 0)
        self.assertAlmostEqual(m['B']['relay_flow'], .8 * 1.1)
        self.assertAlmostEqual(m['C']['relay_flow'], 1.2 * .6)
        self.assertAlmostEqual(m['G']['tradeoff_received_from_backward'], 1.3)
        self.assertEqual(m['G']['forward_ratio'], 0)
        self.assertIsNone(m['F']['forward_ratio'])
        self.assertAlmostEqual(m['F']['tradeoff_sent_to_backward'], .4)

    def test_sdgindex_roles(self):
        colab, neglect = colab_neglect()
        nodes = [dict(id=i, indicator=i, description='Test', direction=d, colab=colab[i], neglect=neglect[i],
                      years_to_target=1.0 if d == 'forward' else None,
                      years_to_zero=1.0 if d == 'backward' else None) for i, d in DIRECTION.items()]
        edges = [dict(source=a, target=b, interaction=k, weight=w) for a, b, k, w in EDGES]
        groups = {g['id']: {r[1] for r in g['rows']} for g in sdg_highlights(nodes, edges)}
        self.assertEqual(groups, EXPECTED)

    def test_iges_roles(self):
        colab, neglect = colab_neglect()
        names = {k: f'{i}.1' for i, k in enumerate(DIRECTION, 1)}
        metrics = {names[k]: dict(Colab=colab[k], Neglect=neglect[k]) for k in DIRECTION}
        details = {names[k]: [names[k], 'n', 'i', 'd', .8 if d == 'forward' else .4, d, 'b']
                   for k, d in DIRECTION.items()}
        edges = [dict(TargetA=names[a], TargetB=names[b], interaction=k, weight=w) for a, b, k, w in EDGES]
        groups = {g['id']: {r[1] for r in g['rows']} for g in iges_highlights(metrics, details, edges)}
        self.assertEqual(groups, {k: {names[i] for i in v} for k, v in EXPECTED.items()})

    def test_old_rule_misses_bridge_with_low_neglect(self):
        # A has the lowest Neglect among deteriorating nodes but is a transmission bridge.
        _, neglect = colab_neglect()
        self.assertEqual(min(('A', 'B', 'C', 'D'), key=neglect.get), 'A')
        self.assertIn('A', EXPECTED['transmission_bridges'])

    def test_isolation_uses_synergy_sent_not_colab_balance(self):
        # X passes forward as much synergy as it receives (phi = 1) but also sends 0.9 of
        # trade-off: low Colab, still not isolated.
        direction = dict(X='forward', Y='forward', Z='backward', W='backward')
        edges = [('Z', 'X', 'trade-off', 1.0), ('X', 'Y', 'synergy', 1.0), ('X', 'W', 'trade-off', .9)]
        nodes = [dict(id=i, indicator=i, description='T', direction=d,
                      colab=sum((w if k == 'synergy' else -w) for a, _, k, w in edges if a == i),
                      neglect=sum(w for a, b, k, w in edges if b == i and k == 'trade-off'),
                      years_to_target=1.0 if d == 'forward' else None,
                      years_to_zero=1.0 if d == 'backward' else None) for i, d in direction.items()]
        groups = {g['id']: {r[1] for r in g['rows']} for g in sdg_highlights(
            nodes, [dict(source=a, target=b, interaction=k, weight=w) for a, b, k, w in edges])}
        self.assertEqual(groups['dependent_contributors'], {'X'})
        self.assertEqual(groups['isolated_beneficiaries'], set())

    def test_isolation_is_absolute_not_relative(self):
        # Both receivers pass synergy forward; only the one passing less than it receives is isolated.
        direction = dict(P='forward', Q='forward', R='forward', Z='backward')
        edges = [('Z', 'P', 'trade-off', 1.0), ('Z', 'Q', 'trade-off', 1.0),
                 ('P', 'R', 'synergy', .5), ('Q', 'R', 'synergy', 2.0)]
        nodes = [dict(id=i, indicator=i, description='T', direction=d, colab=0.0, neglect=0.0,
                      years_to_target=None, years_to_zero=None) for i, d in direction.items()]
        groups = {g['id']: {r[1] for r in g['rows']} for g in sdg_highlights(
            nodes, [dict(source=a, target=b, interaction=k, weight=w) for a, b, k, w in edges])}
        self.assertEqual(groups['isolated_beneficiaries'], {'P'})
        self.assertEqual(groups['dependent_contributors'], {'Q'})

    def test_link_shares_and_ponderation(self):
        shares = link_shares(DIRECTION, EDGES)
        self.assertEqual((shares['B']['links_out'], shares['B']['links_in']), (2, 2))
        self.assertAlmostEqual(shares['B']['share_out'], 2 / 14)
        self.assertAlmostEqual(sum(s['share_in'] for s in shares.values()), 1)
        m = interface_measures(DIRECTION, EDGES)
        b = ponderate(dict(m['B'], colab=1.1, neglect=1.4), shares['B'])
        relative = 2 / 14 * 8  # share x number of nodes; the mean node has 1
        self.assertAlmostEqual(shares['B']['relative_out'], relative)
        self.assertAlmostEqual(b['colab'], 1.1 / relative)
        self.assertAlmostEqual(b['neglect'], 1.4 / relative)
        self.assertAlmostEqual(b['bridge_flow'], m['B']['bridge_flow'] / relative ** 2)
        g = ponderate(dict(m['G'], colab=0.0, neglect=0.0), shares['G'])
        self.assertEqual(g['forward_ratio'], m['G']['forward_ratio'])
        self.assertEqual(g['forward_synergy_sent'], 0)  # no sent links: share zero, measure zero

    def test_weighted_iges_roles_run(self):
        colab, neglect = colab_neglect()
        names = {k: f'{i}.1' for i, k in enumerate(DIRECTION, 1)}
        metrics = {names[k]: dict(Colab=colab[k], Neglect=neglect[k]) for k in DIRECTION}
        details = {names[k]: [names[k], 'n', 'i', 'd', .5, d, 'b'] for k, d in DIRECTION.items()}
        edges = [dict(TargetA=names[a], TargetB=names[b], interaction=k, weight=w) for a, b, k, w in EDGES]
        groups = {g['id']: {r[1] for r in g['rows']} for g in iges_highlights(metrics, details, edges, pond=True)}
        # Small network: every positive value is in the top ten, so weighting leaves membership unchanged.
        self.assertEqual(groups, {k: {names[i] for i in v} for k, v in EXPECTED.items()})

    def test_stable_sources_do_not_create_bridges(self):
        direction = dict(S='stable', K='backward', L='backward')
        m = interface_measures(direction, [('S', 'K', 'trade-off', 1), ('K', 'L', 'synergy', 1)])
        self.assertEqual(m['K']['bridge_flow'], 0)


if __name__ == '__main__':
    unittest.main()
