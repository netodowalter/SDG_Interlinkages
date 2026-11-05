"""Section 7 tests (scripts/validity_sdgindex.py) on a Eurostat country workbook, plus diagnostics.

Usage: python scripts/eurostat_validity.py ISO3 [--start 2005] [--end 2024] [--top-n 10]
                                            [--replicates 500] [--surrogates 200] [--out FILE]

Same variants, null model and surrogates as scripts/validity_sdgindex.py, on
data/Eurostat/countries/<ISO3>_*.xlsx with data/Eurostat/mapping_eurostat.json. The window variants
start 5 and 10 years after --start (2010 and 2015 for the default window). Surrogates are also run on
residuals from a linear trend. Extra sheet Diagnostics: zero annual changes, Spearman between degree and
time R^2, bridges among the deteriorating indicators with the most linear trends, share of significant
pairs oriented by the lag tests.
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT), str(ROOT / 'sdg/engine/modules')]

import validity_sdgindex as vs  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from validity import null_model, surrogate_density  # noqa: E402

EU = ROOT / 'data' / 'Eurostat'


def diagnostics(main, start):
    nodes, edges = main['nodes'], main['edges']
    series = main['series']
    zeros = [int(np.sum(np.abs(np.diff(v[np.isfinite(v)])) < 1e-9)) for v in series.values()]
    degree = {n['id']: 0 for n in nodes}
    for e in edges:
        degree[e['source']] += 1
        degree[e['target']] += 1
    r2 = {n['id']: main['trends'][n['indicator']]['time_r2'] for n in nodes}
    ids = sorted(degree)
    rho, p = stats.spearmanr([degree[i] for i in ids], [r2[i] for i in ids])
    bridges = {r[1] for g in main['highlights'] if g['title'].startswith('D-2') for r in g['rows']}
    backward = sorted((n for n in nodes if n['direction'] == 'backward'), key=lambda n: -r2[n['id']])
    top10 = {n['id'] for n in backward[:10]}
    sig = [x for x in main['pairs'] if x['p'] < .1 and x['r'] != 0]
    oriented = sum(x['direction'] in ('A_to_B', 'B_to_A') for x in sig)
    possible = len(nodes) * (len(nodes) - 1)
    return [
        dict(diagnostic='Indicators in the network', value=len(nodes)),
        dict(diagnostic=f'Median zero annual changes (of {len(next(iter(series.values()))) - 1})',
             value=float(np.median(zeros))),
        dict(diagnostic='Share of zero annual changes', value=float(np.sum(zeros) / sum(len(v) - 1 for v in series.values()))),
        dict(diagnostic='Spearman degree x time R2', value=float(rho), p=float(p)),
        dict(diagnostic='Bridges among the 10 deteriorating indicators with the most linear trends',
             value=f'{len(bridges & top10)} of {len(bridges)}', members='; '.join(sorted(bridges))),
        dict(diagnostic='Network density', value=len(edges) / possible if possible else None),
        dict(diagnostic='Significant pairs oriented in one direction by lag tests',
             value=f'{oriented}/{len(sig)}', share=oriented / len(sig) if sig else None),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('country')
    parser.add_argument('--start', type=int, default=2005)
    parser.add_argument('--end', type=int, default=2024)
    parser.add_argument('--top-n', type=int, default=10)
    parser.add_argument('--replicates', type=int, default=500)
    parser.add_argument('--surrogates', type=int, default=200)
    parser.add_argument('--out')
    parser.add_argument('--inputs', default='countries', help='folder under data/Eurostat with the country workbooks')
    args = parser.parse_args()
    source = next((EU / args.inputs).glob(f'{args.country}_*.xlsx'))
    with tempfile.TemporaryDirectory() as tmp:
        vs.DATA = Path(tmp)
        shutil.copy(EU / 'mapping_eurostat.json', vs.DATA / 'mapping.json')
        vs.MAIN.update(start=args.start, end=args.end, top_n=args.top_n)
        vs.VARIANTS[:] = [(f'window_{args.start + 5}_{args.end}' if n == 'window_2010_2025' else
                           f'window_{args.start + 10}_{args.end}' if n == 'window_2015_2025' else n,
                           dict(c, start=args.start + 5) if n == 'window_2010_2025' else
                           dict(c, start=args.start + 10) if n == 'window_2015_2025' else c)
                          for n, c in vs.VARIANTS]
        variants, stability, results = [], [], {}
        for name, change in vs.VARIANTS:
            spec = dict(vs.MAIN, **change)
            print(f'Variant {name}…', flush=True)
            results[name] = vs.run(source, spec)
            row, roles = vs.describe(name, spec, results[name])
            variants.append(row)
            results[name]['roles'] = roles
        base = results['main']['roles']
        for name, _ in vs.VARIANTS[1:]:
            stability.append(dict(variant=name, **{r: vs.jaccard(base[r], results[name]['roles'][r]) for r in base}))
        main_res = results['main']
        print('Null model…', flush=True)
        null_summary, null_members = null_model(main_res['nodes'], main_res['edges'], replicates=args.replicates)
        print('Surrogates…', flush=True)
        mapping = {r['indicator']: r for r in json.loads((EU / 'mapping_eurostat.json').read_text(encoding='utf-8'))}
        goal_of = {c: mapping[c]['goal'] for c in main_res['series']}
        surrogates = [surrogate_density(main_res['series'], goal_of, replicates=args.surrogates, basis=b)
                      for b in ('levels', 'changes', 'detrended')]
        diag = diagnostics(main_res, args.start)
    out = Path(args.out or ROOT / 'output' / 'validity' / f'{args.country}_eurostat_{args.inputs}_validity_top{args.top_n}.xlsx')
    out.parent.mkdir(parents=True, exist_ok=True)
    book = Workbook()
    book.remove(book.active)
    for title, rows in [('Variants', variants), ('Role_stability', stability), ('Null_summary', null_summary),
                        ('Null_members', null_members), ('Surrogates', surrogates), ('Diagnostics', diag)]:
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
