"""Interface and subsystem roles: worked example in both procedures."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sdg/engine/modules'))
from roles import interface_measures, link_shares, ponderate
from performance_ranking import highlight_groups as sdg_highlights
from progress import highlight_groups as iges_highlights

# Eight hypothetical targets: A-D deteriorating, E-H improving.
DIRECTION = dict(A='backward', B='backward', C='backward', D='backward',
                 E='forward', F='forward', G='forward', H='forward')
EDGES = [('A', 'B', 'synergy', .8), ('A', 'C', 'synergy', .5), ('B', 'C', 'synergy', .7),
         ('C', 'D', 'synergy', .6), ('B', 'D', 'synergy', .4),
         ('E', 'F', 'synergy', .8), ('F', 'E', 'synergy', .5), ('E', 'H', 'synergy', .6),
         ('E', 'B', 'trade-off', .6), ('F', 'A', 'trade-off', .4), ('H', 'D', 'trade-off', .3),
         ('D', 'G', 'trade-off', .7), ('C', 'G', 'trade-off', .6), ('D', 'E', 'trade-off', .5)]
EXPECTED = dict(
    improvement_sender={'E', 'F', 'H'},
    improvement_receiver={'G', 'E'},
    improvement_relay={'E', 'F', 'H'},
    deterioration_sender={'D', 'C'},
    deterioration_receiver={'B', 'A', 'D'},
    deterioration_relay={'B', 'C', 'A'},
)


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
        self.assertAlmostEqual(m['E']['tradeoff_sent_to_backward'], .6)
        self.assertAlmostEqual(m['F']['tradeoff_sent_to_backward'], .4)
        self.assertAlmostEqual(m['G']['tradeoff_received_from_backward'], 1.3)
        self.assertAlmostEqual(m['E']['forward_synergy_degree'], 1.9)
        self.assertAlmostEqual(m['D']['tradeoff_sent_to_forward'], 1.2)
        self.assertAlmostEqual(m['B']['tradeoff_received_from_forward'], .6)
        self.assertAlmostEqual(m['B']['backward_synergy_degree'], 1.9)
        self.assertAlmostEqual(m['C']['backward_synergy_degree'], 1.8)

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

    def test_top_three_without_exclusions_or_backfilling(self):
        direction = dict(I1='forward', I2='forward', I3='forward', I4='forward', D1='backward')
        edges = [('I1', 'D1', 'trade-off', 4.0), ('I2', 'D1', 'trade-off', 3.0),
                 ('I3', 'D1', 'trade-off', 2.0), ('I4', 'D1', 'trade-off', 1.0)]
        nodes = [dict(id=i, indicator=i, description='T', direction=d, colab=0.0, neglect=0.0,
                      years_to_target=None, years_to_zero=None) for i, d in direction.items()]
        groups = {g['id']: [r[1] for r in g['rows']] for g in sdg_highlights(
            nodes, [dict(source=a, target=b, interaction=k, weight=w) for a, b, k, w in edges])}
        self.assertEqual(groups['improvement_sender'], ['I1', 'I2', 'I3'])
        self.assertEqual(groups['deterioration_receiver'], ['D1'])
        self.assertEqual(groups['improvement_receiver'], [])

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
        self.assertAlmostEqual(b['backward_synergy_degree'], m['B']['backward_synergy_degree'] / relative)
        g = ponderate(dict(m['G'], colab=0.0, neglect=0.0), shares['G'])
        self.assertEqual(g['forward_synergy_sent'], 0)  # no sent links: share zero, measure zero

    def test_weighted_iges_roles_run(self):
        colab, neglect = colab_neglect()
        names = {k: f'{i}.1' for i, k in enumerate(DIRECTION, 1)}
        metrics = {names[k]: dict(Colab=colab[k], Neglect=neglect[k]) for k in DIRECTION}
        details = {names[k]: [names[k], 'n', 'i', 'd', .5, d, 'b'] for k, d in DIRECTION.items()}
        edges = [dict(TargetA=names[a], TargetB=names[b], interaction=k, weight=w) for a, b, k, w in EDGES]
        groups = {g['id']: {r[1] for r in g['rows']} for g in iges_highlights(metrics, details, edges, pond=True)}
        self.assertEqual(set(groups), set(EXPECTED))
        self.assertEqual(len(groups['deterioration_relay']), 3)

    def test_stable_sources_do_not_enter_role_measures(self):
        direction = dict(S='stable', K='backward', L='backward')
        m = interface_measures(direction, [('S', 'K', 'trade-off', 1), ('K', 'L', 'synergy', 1)])
        self.assertEqual(m['K']['tradeoff_received_from_forward'], 0)
        self.assertEqual(m['K']['backward_synergy_degree'], 1)


if __name__ == '__main__':
    unittest.main()
