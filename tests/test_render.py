"""Readable layouts preserve data and separate all icon bounding boxes."""
import unittest
import numpy as np
from sdg.two_step import two_step_scores, interface_positions
from sdg.render import positions, PLOT, components, edge_color


class NetworkRendering(unittest.TestCase):
    def assert_readable(self, ids, edges, sizes):
        xy = positions(ids, edges, sizes)
        x0,y0,x1,y1 = PLOT
        self.assertEqual(set(xy), set(ids))
        for index,a in enumerate(ids):
            self.assertGreaterEqual(xy[a][0]-sizes[a]/2, x0)
            self.assertLessEqual(xy[a][0]+sizes[a]/2, x1)
            self.assertGreaterEqual(xy[a][1]-sizes[a]/2, y0)
            self.assertLessEqual(xy[a][1]+sizes[a]/2, y1)
            for b in ids[index+1:]:
                delta = np.abs(xy[a]-xy[b])
                required = (sizes[a]+sizes[b])/2+17
                self.assertTrue(delta[0]>=required or delta[1]>=required, (a,b))
        return xy

    def test_dense_network_with_large_icons(self):
        ids = [str(i) for i in range(100)]
        edges = [dict(source=a,target=b,weight=.9) for index,a in enumerate(ids) for b in ids[index+1:]]
        sizes = {i:76 if int(i)%3==0 else 44 for i in ids}
        self.assert_readable(ids, edges, sizes)

    def test_disconnected_synergies_and_singletons(self):
        ids = [str(i) for i in range(100)]
        edges = [dict(source=str(i),target=str(i+1),weight=.8) for i in range(99) if i not in (59,94,95,96,97,98)]
        sizes = {i:68 for i in ids}
        xy = self.assert_readable(ids, edges, sizes)
        again = positions(ids,edges,sizes)
        for i in ids:
            np.testing.assert_array_equal(xy[i],again[i])
        self.assertEqual(len(components(ids,edges)),7)

    def test_empty_single_node_and_colors(self):
        self.assertEqual(positions([],[]),{})
        self.assert_readable(['a'],[],{'a':76})
        nodes = {'a':dict(direction='forward'),'b':dict(direction='backward')}
        self.assertEqual(edge_color(dict(source='a',interaction='synergy'),nodes),(51,51,51))
        self.assertEqual(edge_color(dict(source='a',interaction='trade-off'),nodes),(153,0,51))
        self.assertEqual(edge_color(dict(source='b',interaction='synergy'),nodes),(219,166,184))
        self.assertEqual(edge_color(dict(source='b',interaction='trade-off'),nodes),(184,184,184))

    def test_two_step_directed_channels(self):
        nodes = [dict(id=i,direction=d) for i,d in [('a','backward'),('b','forward'),('c','forward'),('u','stable')]]
        edges = [dict(source=a,target=b,weight=w,interaction=t) for a,b,w,t in [('a','b',-.5,'trade-off'),('b','c',.4,'synergy'),('c','b',.7,'synergy'),('u','b',1,'trade-off'),('b','b',1,'synergy')]]
        result = two_step_scores(nodes,edges)
        self.assertAlmostEqual(result['b'], .2)
        scaled = two_step_scores([dict(n, interface_scale=.5) for n in nodes], edges)
        self.assertAlmostEqual(scaled['b'], .4)
        self.assertEqual(result['a'], 0)
        self.assertEqual(result['c'], 0)
        sizes = {n['id']:76 for n in nodes}
        baseline = positions(list(sizes),edges,sizes)
        xy = interface_positions(nodes,edges,sizes,baseline,PLOT)
        for a in sizes:
            for b in sizes:
                if a != b:
                    delta = np.abs(xy[a]-xy[b])
                    self.assertTrue(delta[0]>=94 or delta[1]>=94)
        self.assertEqual(set(xy),set(sizes))
