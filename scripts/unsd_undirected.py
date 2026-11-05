"""Undirected interface test on UNSD SDG Global Database series for one country (no IGES/JRC inventory).

Usage: python scripts/unsd_undirected.py UNSD_76_2000.csv [--surrogates N] [--out FILE]
       (CSV from download_unsd.bat)

Selection (2010-2025):
  * aggregate variable of each series: every dimension empty or a total code (ALLAGE, ALLAREA, BOTHSEX,
    _T, TOTAL, ALL, ...); a series reported for a single age group keeps it;
  * at most 6 missing years and no run of more than 3;
  * one series per target: fewest missing years, ties broken by series code; a series already used by
    an earlier target is not reused (the next candidate is taken);
  * series in data/UNSD/series_excluded.csv (ordinal or binary) and --drop codes are skipped;
  * normative direction per series from data/UNSD/series_direction_proposed.csv (series without one
    are dropped and listed).
Construction: CAGR filling as in IGES/JRC; Pearson on levels and on first differences, cross-SDG pairs,
p < 0.10; original type = sign(r) x directions; progress direction = linear trend of the filled series
x direction; discordant ties excluded or reclassified by the main rule. One undirected tie per pair.
Output: trade-off rankings on each side and pair scores (undirected.py), plus surrogate densities.
"""
import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT), str(ROOT / 'sdg/engine/modules')]
from openpyxl import Workbook  # noqa: E402
from raw_sdgindex import cagr  # noqa: E402
from progress import divergent_decision, fit  # noqa: E402
from sdgindex_country import contemporaneous  # noqa: E402
from undirected import tradeoff_pairs  # noqa: E402
from validity import surrogate_density  # noqa: E402

YEARS = list(range(2010, 2026))
TOTALS = {'', 'ALLAGE', 'ALLAREA', 'BOTHSEX', '_T', 'TOTAL', 'ALL', 'ALLDOMAINS', 'DRUG_TOTAL', 'ANYS', 'G'}


def number(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def order(code):
    return [(0, int(p), '') if p.isdigit() else (1, 0, p) for p in code.split('.')]


def gaps(values):
    run = best = 0
    for y in YEARS:
        run = run + 1 if y not in values else 0
        best = max(best, run)
    return sum(y not in values for y in YEARS), best


def fill(values):
    years = sorted(values)
    out = []
    for t in YEARS:
        if t in values:
            out.append(values[t])
            continue
        p = sum(y < t for y in years)
        a, b = years[:2] if p == 0 else years[-2:] if p == len(years) else years[p - 1:p + 1]
        v = cagr(values[a], values[b], a, b, t)
        out.append(np.nan if v is None else v)
    return np.array(out, dtype=float)


extra_meta = {}


def ibge(path):
    """IBGE series of the NT Dinte 77 workbook (sheets Fontes, Series_Coleta, Series_SentidoAlvo).

    Returns (candidates by target, directions by series key). Series keys are 'IBGE:<indicator>'."""
    from openpyxl import load_workbook
    book = load_workbook(path, read_only=True, data_only=True)
    rows = list(book['Fontes'].values)
    sources = [dict(zip(rows[0], r)) for r in rows[1:] if r[0]]
    data = list(book['Series_Coleta'].values)
    head, body = data[0], data[1:]
    sense = {r[0]: r[1] for r in list(book['Series_SentidoAlvo'].values)[1:]}
    book.close()
    candidates, directions = defaultdict(list), {}
    for r in sources:
        code = r['ODS.Indicador.Code']
        if r['ODS.Indicador.Fonte'] != 'IBGE' or code not in head or sense.get(code) not in (1, -1):
            continue
        j = head.index(code)
        values = {int(row[0]): float(row[j]) for row in body
                  if isinstance(row[j], (int, float)) and int(row[0]) in YEARS}
        missing, run = gaps(values)
        if missing <= 6 and run <= 3 and len(values) >= 2:
            key = 'IBGE:' + code
            directions[key] = int(sense[code])
            extra_meta[key] = dict(description=r['Indicador.Descricao'], units='')
            candidates[r['ODS.Meta.Code']].append((missing, key, '', (key, ()), values))
    return candidates, directions


def select(path, directions, excluded=(), drop_natures=(), extra=None):
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    dims = [c for c in rows[0] if c.startswith('dimensions_')]
    data, meta, natures = defaultdict(lambda: defaultdict(list)), {}, defaultdict(set)
    for r in rows:
        y, v = number(r['timePeriodStart']), number(r['value'])
        if y is None or v is None:
            continue
        key = (r['series'], tuple((d[11:], r[d]) for d in dims if r[d]))
        data[key][int(y)].append(v)
        if y in YEARS:
            natures[key].add(r.get('attributes_Nature', ''))
        targets = json.loads(r['target']) if r['target'].startswith('[') else [r['target']]
        meta[key] = dict(series=r['series'], description=r['seriesDescription'], units=r['attributes_Units'],
                         targets=targets)
    by_series = defaultdict(list)
    for key in data:
        by_series[key[0]].append(key)
    candidates = defaultdict(list)
    for series, keys in by_series.items():
        ok = [k for k in keys if all(v in TOTALS for d, v in k[1] if d != 'Age')]
        agg = [k for k in ok if dict(k[1]).get('Age', '') in ('', 'ALLAGE')]
        if not agg and len({dict(k[1]).get('Age', '') for k in ok}) == 1:
            agg = ok
        for k in agg:
            if natures[k] & set(drop_natures):
                continue
            values = {y: float(np.mean(v)) for y, v in data[k].items() if y in YEARS}
            missing, run = gaps(values)
            if missing <= 6 and run <= 3 and len(values) >= 2:
                for target in meta[k]['targets']:
                    candidates[target].append((missing, series, str(k[1]), k, values))
    for target, items in (extra or {}).items():
        candidates[target] += items
    chosen, used, dropped = {}, set(), []
    for target in sorted(candidates, key=order):
        # fewest missing years; ties: IBGE before UNSD (rank 0 < 1), then series code
        for missing, series, _, key, values in sorted(candidates[target], key=lambda c: (c[0], 0 if c[1].startswith('IBGE:') else 1, c[1], c[2])):
            if series in used or series in excluded:
                continue
            if series not in directions:
                dropped.append(dict(target=target, series=series, reason='no normative direction'))
                continue
            used.add(series)
            info = meta.get(key) or extra_meta[series]
            chosen[target] = dict(target=target, goal=target.split('.')[0], series=series, missing=missing,
                                  source='IBGE' if series.startswith('IBGE:') else 'UNSD',
                                  dimensions=dict(key[1]), values=values, direction=directions[series],
                                  description=info['description'], units=info['units'],
                                  natures=', '.join(sorted(natures.get(key, ()))))
            break
    return chosen, dropped


def build(chosen, basis):
    codes = sorted(chosen, key=order)
    series = {c: fill(chosen[c]['values']) for c in codes}
    trends = {c: fit([(y, v) for y, v in zip(YEARS, series[c]) if np.isfinite(v)], chosen[c]['direction'])
              for c in codes}
    tested = {c: np.diff(series[c]) if basis == 'changes' else series[c] for c in codes}
    ties, actions, tested_pairs = [], Counter(), 0
    for a, b in combinations(codes, 2):
        if chosen[a]['goal'] == chosen[b]['goal']:
            continue
        r, p, n = contemporaneous(tested[a], tested[b], 'pearson')
        if r is None:
            continue
        tested_pairs += 1
        if p >= .1 or r == 0:
            continue
        normative = r * chosen[a]['direction'] * chosen[b]['direction']
        original = 'synergy' if normative > 0 else 'trade-off'
        action, kind, _ = divergent_decision(original, trends[a], trends[b], normative)
        actions[action] += 1
        if action != 'excluded':
            ties.append((a, b, kind, abs(r)))
    direction = {c: trends[c]['progress_direction'] for c in codes}
    return dict(series=series, trends=trends, ties=ties, actions=actions, tested=tested_pairs,
                direction=direction, **dict(zip(('sides', 'pairs'), tradeoff_pairs(direction, ties))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv')
    parser.add_argument('--surrogates', type=int, default=100)
    parser.add_argument('--out')
    parser.add_argument('--drop', nargs='*', default=[], help='further series codes to exclude')
    parser.add_argument('--end', type=int, default=2025, help='last year of the window (start 2010)')
    parser.add_argument('--ibge', help='NT Dinte 77 workbook (rede_NT.xlsx): add its IBGE series as candidates')
    parser.add_argument('--drop-natures', nargs='*', default=[], help='skip series with any observation of these natures (e.g. M E G)')
    args = parser.parse_args()
    YEARS[:] = range(2010, args.end + 1)
    directions = {r['series']: int(r['direction']) for r in
                  csv.DictReader(open(ROOT / 'data/UNSD/series_direction_proposed.csv', encoding='utf-8'))}
    excluded = {r['series'] for r in csv.DictReader(open(ROOT / 'data/UNSD/series_excluded.csv', encoding='utf-8'))}
    extra = None
    if args.ibge:
        extra, ibge_directions = ibge(args.ibge)
        directions.update(ibge_directions)
    chosen, dropped = select(args.csv, directions, excluded | set(args.drop), args.drop_natures, extra)
    print(Counter(c['source'] for c in chosen.values()))
    print(f'{len(chosen)} targets in {len({c["goal"] for c in chosen.values()})} SDGs; {len(dropped)} candidates dropped')
    label = {c: f"{c} {v['series']}" for c, v in chosen.items()}
    book = Workbook()
    book.remove(book.active)

    def sheet(title, items):
        s = book.create_sheet(title)
        head = list(dict.fromkeys(k for r in items for k in r))
        s.append(head or ['No records'])
        for r in items:
            s.append([json.dumps(r[k], ensure_ascii=False) if isinstance(r.get(k), (dict, list)) else r.get(k)
                      for k in head])

    summary = []
    for basis in ('levels', 'changes'):
        res = build(chosen, basis)
        d = Counter(res['direction'].values())
        sur = surrogate_density(res['series'], {c: chosen[c]['goal'] for c in chosen},
                                replicates=args.surrogates, basis=basis)
        summary.append(dict(basis=basis, targets=len(chosen), improving=d['forward'], deteriorating=d['backward'],
                            other=d['stable'] + d['undetermined'], pairs_tested=res['tested'],
                            ties=len(res['ties']), retained=res['actions']['retained'],
                            reclassified=res['actions']['reclassified'], excluded=res['actions']['excluded'],
                            tradeoffs=sum(t[2] == 'trade-off' for t in res['ties']),
                            observed_share_p10=sur['observed_share'], surrogate_share_p10=sur['surrogate_mean_share']))
        for side, name in (('forward', 'improving'), ('backward', 'deteriorating')):
            sheet(f'{basis}_{name}', [dict(r, label=label[r['node']], description=chosen[r['node']]['description'])
                                       for r in res['sides'][side]])
        sheet(f'{basis}_pairs', [dict(p, improving_label=label[p['improving']],
                                      deteriorating_label=label[p['deteriorating']]) for p in res['pairs']])
        print(f'\n== {basis}: {len(res["ties"])} ties, {summary[-1]["tradeoffs"]} trade-offs; '
              f'p<0.10 observed {sur["observed_share"]:.1%} vs surrogates {sur["surrogate_mean_share"]:.1%}')
        for side in ('forward', 'backward'):
            print(' ', side, ', '.join(f"{label[r['node']]} ({r['tradeoff_degree']:.2f})" for r in res['sides'][side][:5]))
        for p in res['pairs'][:5]:
            print(f"  {label[p['improving']]} (#{p['improving_rank']}) – {label[p['deteriorating']]} "
                  f"(#{p['deteriorating_rank']}): {p['improving_normalised']:.3f} + {p['deteriorating_normalised']:.3f}"
                  f" + {p['tie']:.3f} = {p['score']:.3f}")
    trend = build(chosen, 'levels')['trends']
    sheet('Summary', summary)
    sheet('Selected_series', [dict({k: v for k, v in c.items() if k != 'values'},
                                   progress_direction=trend[c['target']]['progress_direction'],
                                   time_r2=trend[c['target']]['time_r2'])
                              for c in sorted(chosen.values(), key=lambda c: order(c['target']))])
    sheet('Dropped', dropped)
    out = Path(args.out or ROOT / 'output' / 'validity' / 'UNSD_undirected.xlsx')
    out.parent.mkdir(parents=True, exist_ok=True)
    book.save(out)
    print('\n' + str(out))


if __name__ == '__main__':
    main()
