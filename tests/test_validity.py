'Sensitivity options and validity checks for SDGIndex roles.'
import contextlib
import io
import sys
import unittest
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'sdg/engine/modules')]
from sdgindex_country import analyze  # noqa: E402
from roles import select_roles  # noqa: E402
from validity import _roles, phase_surrogate, rewire, role_sets  # noqa: E402

SOURCE = ROOT / 'data/SDGIndex/countries/BRA_Brazil.xlsx'
MAPPING = ROOT / 'data/SDGIndex/mapping.json'


def run(**options):
    with contextlib.redirect_stdout(io.StringIO()):
        return analyze(SOURCE, MAPPING, 'pearson', 'BRA', 'Brazil', None, **options)


class Validity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = run()

    def test_defaults_match_workbook_run(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            full = analyze(SOURCE, MAPPING, 'pearson', 'BRA', 'Brazil', Path(temp) / 'x.xlsx')
        self.assertEqual(len(full['network']['edges']), len(self.main['edges']))
        self.assertEqual(role_sets(full['highlights']), role_sets(self.main['highlights']))

    def test_window_and_changes(self):
        late = run(start=2010)
        self.assertTrue(all(v.size == 16 for v in late['series'].values()))
        changes = run(basis='changes')
        self.assertLess(len(changes['edges']), len(self.main['edges']))
        # Directions still come from levels.
        self.assertEqual({c: t['progress_direction'] for c, t in changes['trends'].items()},
                         {c: t['progress_direction'] for c, t in self.main['trends'].items()})

    def test_bh_selection_is_subset(self):
        arcs = lambda d: {(e['source'], e['target']) for e in d['edges']}
        self.assertLessEqual(arcs(run(selection='q')), arcs(self.main))

    def test_isolation_zero_is_stricter(self):
        top = lambda field, direction: {'a', 'b'} if field == 'tradeoff_received_from_backward' else set()
        ratio = {'a': 0.0, 'b': 0.5}
        self.assertEqual(select_roles(top, ratio)['isolated_beneficiaries'], {'a', 'b'})
        self.assertEqual(select_roles(top, ratio, isolation='zero')['isolated_beneficiaries'], {'a'})

    def test_rewiring_preserves_degrees_and_rules(self):
        direction = {n['id']: n['direction'] for n in self.main['nodes']}
        edges = rewire(self.main['edges'], direction, np.random.default_rng(3), swaps=3)
        for side in ('source', 'target'):
            self.assertEqual(Counter(e[side] for e in edges), Counter(e[side] for e in self.main['edges']))
        self.assertEqual(sorted(e['weight'] for e in edges), sorted(e['weight'] for e in self.main['edges']))
        pairs = [(e['source'], e['target']) for e in edges]
        self.assertEqual(len(pairs), len(set(pairs)))
        for e in edges:
            self.assertNotEqual(e['source'].split('.')[0], e['target'].split('.')[0])
            same = direction[e['source']] == direction[e['target']]
            self.assertEqual(e['interaction'], 'synergy' if same else 'trade-off')

    def test_zero_swaps_reproduce_observed_roles(self):
        direction = {n['id']: n['direction'] for n in self.main['nodes']}
        roles, _ = _roles(self.main['nodes'], rewire(self.main['edges'], direction,
                                                     np.random.default_rng(0), swaps=0))
        self.assertEqual(roles, role_sets(self.main['highlights']))

    def test_phase_surrogate_keeps_spectrum(self):
        rng = np.random.default_rng(5)
        x = np.cumsum(rng.normal(size=26))
        s = phase_surrogate(x, rng)
        self.assertTrue(np.allclose(np.abs(np.fft.rfft(x - x.mean())), np.abs(np.fft.rfft(s - s.mean()))))
        self.assertAlmostEqual(s.mean(), x.mean())


if __name__ == '__main__':
    unittest.main()
