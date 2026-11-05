"""IGES/JRC procedure with and without the significance filter (levels), as in IGES practice.

Usage: python scripts/iges_nofilter.py UNSD.csv AREA_CODE

Runs the package pipeline at alpha = 0.10 and alpha = 1.0 (no filter) and reports the arcs added
without the filter, their median |r| against the significant ones, how many become trade-offs, and
the Jaccard similarity of each role between the two runs.
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validity_iges as V  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv')
    parser.add_argument('area')
    args = parser.parse_args()
    sig = V.run(args.csv, args.area, 'levels', 0.1)
    allr = V.run(args.csv, args.area, 'levels', 1.0)
    kept = {(e['source'], e['target']) for e in sig['edges']}
    added = [e for e in allr['edges'] if (e['source'], e['target']) not in kept]
    print(f"arcs p<0.10: {len(sig['edges'])}; without filter: {len(allr['edges'])}; added: {len(added)}")
    if added:
        print(f"median |r| added: {np.median([e['weight'] for e in added]):.2f}; "
              f"significant: {np.median([e['weight'] for e in sig['edges']]):.2f}; "
              f"added trade-offs: {sum(e['interaction'] == 'trade-off' for e in added)}")
    a = {k: set(v) for k, v in sig['roles'].items()}
    b = {k: set(v) for k, v in allr['roles'].items()}
    for role in sorted(a.keys() | b.keys()):
        x, y = a.get(role, set()), b.get(role, set())
        print(f"  {role}: Jaccard {len(x & y) / len(x | y) if x | y else 1:.2f}")


if __name__ == '__main__':
    main()
