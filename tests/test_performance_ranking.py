"""Performance times, rank intersections, precedence, and cutoff regressions."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sdg/engine/modules'))
from performance_ranking import performance_time, highlight_groups, positions
from progress import highlight_groups as iges_highlights, dependence_diagnostics


class PerformanceRanking(unittest.TestCase):
    def test_years_and_boundaries(self):
        forward = dict(slope=2, progress_direction='forward')
        backward = dict(slope=-.5, progress_direction='backward')
        result = performance_time([(2025, None), (2024, 80), (2000, 20)], forward)
        self.assertEqual((result['latest_year'], result['years_to_target']), (2024, 10))
        self.assertEqual(performance_time([(2025, 90)], backward)['years_to_zero'], 180)
        self.assertEqual(performance_time([(2025, 100)], forward)['years_to_target'], 0)
        self.assertEqual(performance_time([(2025, 0)], backward)['years_to_zero'], 0)
        for direction in ('stable', 'undetermined'):
            value = performance_time([(2025, 50)], dict(slope=0, progress_direction=direction))
            self.assertIsNone(value['years_to_target'])
            self.assertIsNone(value['years_to_zero'])

    def test_intersections_precedence_and_tenth_place(self):
        nodes = []
        for direction, prefix in [('forward', 'f'), ('backward', 'b')]:
            for i in range(12):
                nodes.append(dict(id=f'{prefix}{i:02}', indicator=f'{prefix}{i:02}',
                    description='Test', direction=direction, colab=100-i, neglect=100-i,
                    years_to_target=i+1 if direction == 'forward' else None,
                    years_to_zero=100-i if direction == 'backward' else None))
        edges = [dict(source=f'b{i:02}', target=f'f{i:02}', interaction='trade-off', weight=i+1)
                 for i in range(6)]
        edges += [dict(source=f'b{i:02}', target='b11', interaction='synergy', weight=i+1)
                  for i in range(6)]
        groups = {g['id']: {r[1] for r in g['rows']} for g in highlight_groups(nodes, edges)}
        self.assertEqual(groups['contributors'], {'f06', 'f07', 'f08', 'f09'})
        # Receivers that pass no synergy forward are isolated beneficiaries, not dependent contributors.
        self.assertEqual(groups['dependent_contributors'], set())
        self.assertEqual(groups['isolated_beneficiaries'], {f'f{i:02}' for i in range(6)})
        self.assertEqual(groups['exposed'], {'b06', 'b07', 'b08', 'b09'})
        # No trade-off reaches the deteriorating nodes and b11 passes nothing on.
        self.assertEqual(groups['transmission_bridges'], set())
        self.assertEqual(groups['deterioration_relays'], set())
        # Times characterise roles but no longer filter them.
        nodes[-1]['years_to_zero'] = 1000
        result = {g['id']: {r[1] for r in g['rows']} for g in highlight_groups(nodes, edges)}
        self.assertIn('b09', result['exposed'])
        self.assertEqual(nodes[-1]['zero_time_rank'], 1)
        self.assertEqual(nodes[0]['tradeoff_received_from_backward'], 1)

    def test_exact_ties_have_reproducible_ten_entry_cutoff(self):
        nodes = [dict(id=f'n{i:02}', direction='forward', colab=1) for i in range(12)]
        ranks = positions(list(reversed(nodes)), 'colab', 'forward', positive=True)
        self.assertEqual([i for i, rank in ranks.items() if rank <= 10], [f'n{i:02}' for i in range(10)])

    def test_iges_ambition_does_not_filter_and_extends_to_tenth(self):
        metrics = {f'{i}.1': dict(Colab=30-i, Neglect=0) for i in range(1, 13)}
        details = {t: [t, 'Test', 'indicator', 'Test', .8, 'forward', 'high'] for t in metrics}
        details['9.1'][4] = .5
        groups = iges_highlights(metrics, details)
        ids = {r[1] for r in groups[0]['rows']}
        self.assertIn('10.1', ids)
        self.assertNotIn('11.1', ids)
        self.assertIn('9.1', ids)  # low ambition is reported, not excluded
        self.assertEqual(next(r for r in groups[0]['rows'] if r[1] == '9.1')[6], .5)
        # The diagnostic uses the same widened intersection.
        details['12.1'][5] = 'backward'
        edges = [dict(TargetA='12.1', TargetB=t, interaction='trade-off', weight=1)
                 for t in metrics if t != '12.1']
        diagnostic = {r['TargetCode']: r for r in dependence_diagnostics(metrics, details, edges)}
        self.assertTrue(diagnostic['10.1']['strict_highlight'])
        self.assertFalse(diagnostic['11.1']['strict_highlight'])
