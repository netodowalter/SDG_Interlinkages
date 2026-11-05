"""Validity of the IGES/JRC procedure as implemented in the package: levels vs first differences.

Usage: python scripts/validity_iges.py UNSD.csv [AREA_CODE] [--replicates N] [--surrogates N] [--alpha A]

Runs the package pipeline unchanged (inventory pairs, CAGR filling, Pearson, p < alpha, normative and
progress classification, roles) twice: on the prepared series (levels) and on their year-on-year
differences (only the Pearson step changes). For each run it reports the network, roles, the undirected
trade-off pair ranking, the share of series pairs passing p < 0.10 against phase-shuffled surrogates,
and the degree- and direction-preserving null model for roles.
"""
import argparse
import contextlib
import csv
import io
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'sdg/engine/modules')]
from openpyxl import Workbook, load_workbook  # noqa: E402
from sdg.engine import sdg_interlinkages as iges  # noqa: E402
from undirected import tradeoff_pairs  # noqa: E402
from validity import _roles, null_model, surrogate_density  # noqa: E402


def differences(values):
    return [b - a if a is not None and b is not None else None for a, b in zip(values[:-1], values[1:])]


def run(csv_path, area, basis, alpha):
    modules = iges.load_modules(Path())
    pearson = modules[2]
    original = pearson.compute
    captured = {}

    def compute(series, targets):
        captured.update(series=dict(series), targets=dict(targets))
        if basis == 'changes':
            series = {k: differences(v) for k, v in series.items()}
        return original(series, targets)

    pearson.compute = compute
    try:
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            work = Path(tmp)
            (work / 'p').mkdir()
            produced = Path(iges.run_pipeline(modules, work / 'p', {'code': int(area), 'name': 'Area'},
                                              Path(csv_path), work / 'out', alpha=alpha))
            edges = list(csv.DictReader(open(next(produced.glob('*_network.csv')), encoding='utf-8-sig')))
            book = load_workbook(next(produced.glob('*_interlinkages.xlsx')), read_only=True)
            rows = list(book['Interface_measures'].values)
            book.close()
    finally:
        pearson.compute = original
    head = rows[0]
    measures = [dict(zip(head, r)) for r in rows[1:]]
    direction = {str(m['TargetCode']): m['progress_direction'] for m in measures}
    roles = {}
    for m in measures:
        for title in (m['role'] or '').split('; '):
            if title:
                roles.setdefault(title, []).append(str(m['TargetCode']))
    edges = [dict(source=e['TargetA'], target=e['TargetB'], interaction=e['interaction'],
                  weight=abs(float(e['weight']))) for e in edges]
    return dict(edges=edges, direction=direction, roles=roles, series=captured['series'],
                targets=captured['targets'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv')
    parser.add_argument('area', nargs='?', default='76')
    parser.add_argument('--replicates', type=int, default=200)
    parser.add_argument('--surrogates', type=int, default=100)
    parser.add_argument('--alpha', type=float, default=0.1)
    parser.add_argument('--out')
    args = parser.parse_args()
    summary, role_rows, pair_rows, null_rows = [], [], [], []
    for basis in ('levels', 'changes'):
        print(f'{basis}…', flush=True)
        res = run(args.csv, args.area, basis, args.alpha)
        series = {k: np.array([np.nan if v is None else v for v in vals], dtype=float)
                  for k, vals in res['series'].items()}
        goal = {k: str(t).split('.')[0] for k, t in res['targets'].items()}
        sur = surrogate_density(series, goal, replicates=args.surrogates, basis=basis)
        d = Counter(res['direction'].values())
        summary.append(dict(basis=basis, alpha=args.alpha, targets=len(res['direction']), improving=d['forward'],
                            deteriorating=d['backward'], arcs=len(res['edges']),
                            synergies=sum(e['interaction'] == 'synergy' for e in res['edges']),
                            tradeoffs=sum(e['interaction'] == 'trade-off' for e in res['edges']),
                            median_abs_r=float(np.median([e['weight'] for e in res['edges']])) if res['edges'] else None,
                            series_pairs_p10_observed=sur['observed_share'],
                            series_pairs_p10_surrogates=sur['surrogate_mean_share']))
        for role, members in sorted(res['roles'].items()):
            role_rows.append(dict(basis=basis, role=role, members='; '.join(sorted(members))))
        sides, pairs = tradeoff_pairs(res['direction'], [(e['source'], e['target'], e['interaction'], e['weight'])
                                                         for e in res['edges']])
        pair_rows += [dict(basis=basis, **p) for p in pairs[:20]]
        nodes = [dict(id=i, target=i, indicator=i, description=i, direction=dr, years_to_target=None,
                      years_to_zero=None) for i, dr in res['direction'].items()]
        observed, _ = _roles(nodes, res['edges'])
        from roles import ROLES
        package = {slug: set(res['roles'].get(title, [])) for slug, title, *_ in ROLES}
        summary[-1]['roles_recomputed_match'] = observed == package
        s, _ = null_model(nodes, res['edges'], replicates=args.replicates)
        null_rows += [dict(basis=basis, **r) for r in s]
        print(summary[-1], flush=True)
        for p in pairs[:3]:
            print('  pair', p['improving'], '–', p['deteriorating'], round(p['score'], 3))
        for r in s:
            print('  null', r['role'], r['observed_members'], round(r['mean_jaccard_with_null'], 2), r['members_beating_null_p05'])
    out = Path(args.out or ROOT / 'output' / 'validity' / f'IGES_{args.area}_validity.xlsx')
    out.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)
    for title, items in [('Summary', summary), ('Roles', role_rows), ('Pairs_undirected', pair_rows),
                         ('Null_summary', null_rows)]:
        sh = wb.create_sheet(title)
        head = list(dict.fromkeys(k for r in items for k in r))
        sh.append(head)
        for r in items:
            sh.append([r.get(k) for k in head])
    wb.save(out)
    print(out)


if __name__ == '__main__':
    main()
