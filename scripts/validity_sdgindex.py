"""Validity and sensitivity of SDGIndex roles for one country (TODO.md, "Before submission").

Usage: python scripts/validity_sdgindex.py [ISO3] [--replicates N] [--surrogates N] [--top-n N] [--out FILE]

Stability variants use a cut-off of --top-n per role (default 10, more favourable to stability);
the null model uses the Section 5 cut-off of three (roles.ROLE_TOP).

Writes one workbook with:
  Variants        network size and role membership for each specification
  Role_stability  Jaccard similarity of each role with the main specification
  Null_summary    observed roles vs degree- and direction-preserving rewired networks
  Null_members    per observed member: share of null networks giving it the same role, empirical p
  Surrogates      share of cross-SDG pairs passing p<0.10, observed vs phase-shuffled surrogates
"""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'sdg/engine/modules'))

from openpyxl import Workbook  # noqa: E402
from sdgindex_country import analyze  # noqa: E402
from validity import null_model, role_sets, surrogate_density  # noqa: E402

DATA = ROOT / 'data' / 'SDGIndex'
MAIN = dict(method='pearson', start=2000, end=2025, basis='levels', selection='p', top_n=10, isolation='ratio')
VARIANTS = [
    ('main', {}),
    ('spearman', dict(method='spearman')),
    ('changes', dict(basis='changes')),
    ('window_2010_2025', dict(start=2010)),
    ('window_2015_2025', dict(start=2015)),
    ('bh_q', dict(selection='q')),
    ('top_5', dict(top_n=5)),
    ('top_15', dict(top_n=15)),
    ('isolation_zero', dict(isolation='zero')),
]


def run(source, spec):
    spec = dict(spec)
    method = spec.pop('method')
    with contextlib.redirect_stdout(io.StringIO()):
        return analyze(source, DATA / 'mapping.json', method, '', '', None, **spec)


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def describe(name, spec, result):
    nodes, edges = result['nodes'], result['edges']
    direction = {n['id']: n['direction'] for n in nodes}
    syn = [e for e in edges if e['interaction'] == 'synergy']
    interface = [e for e in syn if direction[e['source']] in ('forward', 'backward')
                 and direction[e['target']] in ('forward', 'backward')]
    same = sum(direction[e['source']] == direction[e['target']] for e in interface)
    possible = len(nodes) * (len(nodes) - 1)
    roles = role_sets(result['highlights'])
    row = dict(variant=name, **spec, nodes=len(nodes),
               improving=sum(d == 'forward' for d in direction.values()),
               deteriorating=sum(d == 'backward' for d in direction.values()),
               arcs=len(edges), density=len(edges) / possible if possible else None,
               synergy_share_same_direction=same / len(interface) if interface else None,
               discordant_excluded=sum(c['Adverse_action'] == 'excluded' for c in result['cases']),
               discordant_reclassified=sum(c['Adverse_action'] == 'reclassified' for c in result['cases']))
    for role, members in roles.items():
        row[role] = '; '.join(sorted(members))
    return row, roles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('country', nargs='?', default='BRA')
    parser.add_argument('--replicates', type=int, default=500)
    parser.add_argument('--surrogates', type=int, default=200)
    parser.add_argument('--out')
    parser.add_argument('--top-n', type=int, default=10,
                        help='role cut-off of the stability variants (the null model always uses ROLE_TOP = 3)')
    args = parser.parse_args()
    MAIN['top_n'] = args.top_n
    record = next(r for r in json.loads((DATA / 'countries.json').read_text(encoding='utf-8'))
                  if r['code'] == args.country)
    source = DATA / 'countries' / Path(record['url']).name
    out = Path(args.out or ROOT / 'output' / 'validity' / f'{args.country}_validity.xlsx')
    out.parent.mkdir(parents=True, exist_ok=True)

    variants, stability, results = [], [], {}
    for name, change in VARIANTS:
        spec = dict(MAIN, **change)
        print(f'Variant {name}…', flush=True)
        results[name] = run(source, spec)
        row, roles = describe(name, spec, results[name])
        variants.append(row)
        results[name]['roles'] = roles
    base = results['main']['roles']
    for name, _ in VARIANTS[1:]:
        roles = results[name]['roles']
        stability.append(dict(variant=name, **{r: jaccard(base[r], roles[r]) for r in base}))

    main = results['main']
    print('Null model…', flush=True)
    null_summary, null_members = null_model(main['nodes'], main['edges'], replicates=args.replicates)

    print('Surrogates…', flush=True)
    mapping = {r['indicator']: r for r in json.loads((DATA / 'mapping.json').read_text(encoding='utf-8'))}
    goal_of = {c: mapping[c]['goal'] for c in main['series']}
    surrogates = [surrogate_density(main['series'], goal_of, replicates=args.surrogates, basis=b)
                  for b in ('levels', 'changes')]

    book = Workbook()
    book.remove(book.active)
    for title, rows in [('Variants', variants), ('Role_stability', stability), ('Null_summary', null_summary),
                        ('Null_members', null_members), ('Surrogates', surrogates)]:
        sheet = book.create_sheet(title)
        headers = list(dict.fromkeys(k for r in rows for k in r))
        sheet.append(headers)
        for r in rows:
            sheet.append([r.get(k) for k in headers])
        sheet.freeze_panes = 'B2'
    book.save(out)
    print(out)


if __name__ == '__main__':
    main()
