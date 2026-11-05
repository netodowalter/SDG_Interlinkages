"""Targets with a usable UNSD series for one country, with and without the normative-direction table.

Usage: python scripts/unsd_coverage.py UNSD.csv [--end YEAR] [--drop-natures M E G]

Applies the selection rules of unsd_undirected.py (aggregate series, completeness, one series per
target, ordinal/binary series excluded) and counts the targets covered (a) if every series had a
direction and (b) with data/UNSD/series_direction_proposed.csv.
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT), str(ROOT / 'sdg/engine/modules')]
import unsd_undirected as U  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv')
    parser.add_argument('--end', type=int, default=2023)
    parser.add_argument('--drop-natures', nargs='*', default=['M', 'E', 'G'])
    args = parser.parse_args()
    U.YEARS[:] = range(2010, args.end + 1)
    excluded = {r['series'] for r in csv.DictReader(open(ROOT / 'data/UNSD/series_excluded.csv', encoding='utf-8'))}
    table = {r['series']: int(r['direction']) for r in
             csv.DictReader(open(ROOT / 'data/UNSD/series_direction_proposed.csv', encoding='utf-8'))}
    every = {r['series']: 1 for r in csv.DictReader(open(args.csv, encoding='utf-8-sig'))}
    possible, _ = U.select(args.csv, every, excluded, args.drop_natures)
    covered, dropped = U.select(args.csv, table, excluded, args.drop_natures)
    print(f'2010-{args.end}, natures dropped {args.drop_natures or "none"}: '
          f'{len(possible)} targets if every series had a direction; {len(covered)} with the direction table')
    for d in dropped:
        print('  no direction:', d['target'], d['series'])


if __name__ == '__main__':
    main()
