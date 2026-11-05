"""SDGIndex network from raw indicator values (SDR database, sheet "All Raw Data").

Usage: python scripts/raw_sdgindex.py DATABASE.xlsx [ISO3] [--replicates N] [--surrogates N] [--out FILE]

Steps (country, 2000-2025):
 1. Indicators of mapping.json with at most 6 missing years in total and no run of more
    than 3 consecutive missing years.
 2. Gaps filled as in the IGES/JRC procedure: CAGR between neighbours, extrapolation from
    the first or last two points; positive endpoints required, two zero endpoints give zero,
    otherwise the gap stays empty.
 3. Pearson on filled raw values, cross-SDG pairs only, p < 0.10; orientation by lagged and
    conditional tests (p < 0.10 each), as in the main SDGIndex procedure.
 4. Normative sign from the Codebook: +1 if Optimum (=100) > Lower Bound (=0), else -1.
    Original interaction = sign(r) x sign_A x sign_B (synergy if positive).
 5. Progress direction, three options:
      endpoints  sign of (last observed - first observed) x normative sign
      raw_trend  linear trend of the filled raw series x normative sign
      score      linear trend of the normalised score (sheet "Backdated SDG Index")
    The discordance rule (exclusion by time R^2 and |r|, otherwise reclassification) uses
    the R^2 of the raw trend for endpoints and raw_trend, and of the score trend for score.
 6. Colab, Neglect, interface measures and roles as in the main procedure. Years to target
    or to zero (context only) come from the normalised scores.
"""
import argparse
import contextlib
import io
import json
import math
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'sdg/engine/modules')]

from openpyxl import Workbook, load_workbook  # noqa: E402
from sdgindex_country import analyze, bh, conditional, contemporaneous  # noqa: E402
from progress import divergent_decision, fit  # noqa: E402
from networks import node_metrics  # noqa: E402
from performance_ranking import highlight_groups, performance_time  # noqa: E402
from validity import null_model, role_sets, surrogate_density  # noqa: E402

YEARS = list(range(2000, 2026))
MAX_TOTAL, MAX_RUN = 6, 3
OPTIONS = ('endpoints', 'raw_trend', 'score')
DATA = ROOT / 'data' / 'SDGIndex'


def rows(book, name):
    it = iter(book[name].values)
    head = next(it)
    return [dict(zip(head, r)) for r in it]


def number(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def gaps(values):
    missing = [values.get(y) is None for y in YEARS]
    run = best = 0
    for m in missing:
        run = run + 1 if m else 0
        best = max(best, run)
    return sum(missing), best


def cagr(x0, x1, t0, t1, t):
    if x0 == x1 == 0:
        return 0.0
    if x0 <= 0 or x1 <= 0:
        return None
    return x0 * (x1 / x0) ** ((t - t0) / (t1 - t0))


def fill(values):
    """IGES/JRC rule. Returns (array, counts of interpolated, extrapolated, left empty)."""
    years = sorted(y for y in YEARS if values.get(y) is not None)
    out, kind = [], Counter()
    for t in YEARS:
        if values.get(t) is not None:
            out.append(values[t])
            continue
        p = sum(y < t for y in years)
        a, b = (years[:2] if p == 0 else years[-2:] if p == len(years) else years[p - 1:p + 1])
        v = cagr(values[a], values[b], a, b, t) if len(years) >= 2 else None
        kind['empty' if v is None else 'interpolated' if a < t < b else 'extrapolated'] += 1
        out.append(np.nan if v is None else v)
    return np.array(out, dtype=float), kind


def build(raw, scores, norm, mapping, option, **role_options):
    codes = sorted(raw)
    series = {c: raw[c]['filled'] for c in codes}
    raw_trend = {c: fit([(y, v) for y, v in zip(YEARS, series[c]) if np.isfinite(v)], norm[c]) for c in codes}
    score_trend = {c: fit(list(scores[c].items()), 1) for c in codes}
    trends = {}
    for c in codes:
        if option == 'score':
            trends[c] = score_trend[c]
        elif option == 'raw_trend':
            trends[c] = raw_trend[c]
        else:
            obs = sorted(raw[c]['observed'].items())
            change = (obs[-1][1] - obs[0][1]) * norm[c]
            scale = max(1, max(abs(v) for _, v in obs)) * 1e-12
            direction = 'stable' if abs(change) <= scale else 'forward' if change > 0 else 'backward'
            trends[c] = dict(raw_trend[c], progress_direction=direction)
    pairs = []
    for a, b in combinations(codes, 2):
        ma, mb = mapping[a], mapping[b]
        if ma['goal'] == mb['goal'] or ma['target'] == mb['target']:
            continue
        x, y = series[a], series[b]
        r, p, n = contemporaneous(x, y, 'pearson')
        if r is None:
            continue
        rab, pab, _ = contemporaneous(x[:-1], y[1:], 'pearson')
        rba, pba, _ = contemporaneous(y[:-1], x[1:], 'pearson')
        _, pcab, _ = conditional(x[:-1], y[:-1], y[1:], 'pearson')
        _, pcba, _ = conditional(y[:-1], x[:-1], x[1:], 'pearson')
        ab = pab is not None and pcab is not None and pab < .1 and pcab < .1 and rab != 0
        ba = pba is not None and pcba is not None and pba < .1 and pcba < .1 and rba != 0
        pairs.append(dict(a=a, b=b, r=r, p=p, n=n, q_BH=None,
                          direction='both' if ab and ba else 'A_to_B' if ab else 'B_to_A' if ba else 'undetermined'))
    bh(pairs)
    ids = {c: mapping[c]['target'] + '::' + c.split('_', 1)[1] for c in codes}
    edges, actions = [], Counter()
    for pair in pairs:
        if pair['p'] >= .1 or pair['r'] == 0:
            continue
        a, b = pair['a'], pair['b']
        normative = pair['r'] * norm[a] * norm[b]
        original = 'synergy' if normative > 0 else 'trade-off'
        action, kind, _ = divergent_decision(original, trends[a], trends[b], normative)
        arcs = ([(a, b)] if pair['direction'] == 'A_to_B' else [(b, a)] if pair['direction'] == 'B_to_A'
                else [(a, b), (b, a)])
        actions[action] += len(arcs)
        if action == 'excluded':
            continue
        for s, t in arcs:
            edges.append(dict(source=ids[s], target=ids[t], interaction=kind, interaction_original=original,
                              coefficient=pair['r'], weight=abs(pair['r']), classification_action=action))
    connected = {e[k] for e in edges for k in ('source', 'target')}
    nodes = []
    for c in codes:
        if ids[c] not in connected:
            continue
        timing = performance_time(list(scores[c].items()), score_trend[c])
        if trends[c]['progress_direction'] != score_trend[c]['progress_direction']:
            timing.update(years_to_target=None, years_to_zero=None)
        nodes.append(dict(id=ids[c], target=mapping[c]['target'], indicator=c, description=mapping[c]['description'],
                          direction=trends[c]['progress_direction'], **timing))
    metrics = node_metrics([n['id'] for n in nodes],
                           [dict(TargetA=e['source'], TargetB=e['target'], interaction=e['interaction'],
                                 weight=e['weight']) for e in edges],
                           {n['id']: n['direction'] for n in nodes})
    for n in nodes:
        n.update(colab=metrics[n['id']]['collaboration'], neglect=metrics[n['id']]['neglect'])
    highlights = highlight_groups(nodes, edges, **role_options)
    return dict(nodes=nodes, edges=edges, highlights=highlights, pairs=pairs, actions=actions, series=series,
                trends=trends)


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    parser.add_argument('country', nargs='?', default='BRA')
    parser.add_argument('--replicates', type=int, default=200)
    parser.add_argument('--surrogates', type=int, default=100)
    parser.add_argument('--out')
    args = parser.parse_args()

    mapping = {r['indicator'][2:]: r for r in json.loads((DATA / 'mapping.json').read_text(encoding='utf-8'))}
    book = load_workbook(args.database, read_only=True, data_only=True)
    raw_rows = [r for r in rows(book, 'All Raw Data') if r['id'] == args.country and r['year'] in YEARS]
    score_rows = [r for r in rows(book, 'Backdated SDG Index') if r['id'] == args.country and r['year'] in YEARS]
    codebook = {r['IndCode']: r for r in rows(book, 'Codebook')}
    book.close()

    coverage, raw, scores, norm = [], {}, {}, {}
    for c in sorted(mapping):
        values = {r['year']: number(r.get(c)) for r in raw_rows}
        values = {y: v for y, v in values.items() if v is not None}
        total, run = gaps(values)
        keep = total <= MAX_TOTAL and run <= MAX_RUN and len(values) >= 2
        row = dict(indicator=c, target=mapping[c]['target'], description=mapping[c]['description'],
                   missing_years=total, longest_gap=run, kept=keep)
        if keep:
            book_row = codebook[c]
            norm[c] = 1 if book_row['Optimum (= 100)'] > book_row['Lower Bound (=0)'] else -1
            filled, kind = fill(values)
            raw[c] = dict(observed=values, filled=filled)
            scores[c] = {r['year']: number(r.get('n_' + c)) for r in score_rows if number(r.get('n_' + c)) is not None}
            row.update(normative_sign=norm[c], **{f'n_{k}': kind[k] for k in ('interpolated', 'extrapolated', 'empty')})
        coverage.append(row)

    # Reference: the main procedure on the package's normalised scores (all 101 indicators).
    record = next(r for r in json.loads((DATA / 'countries.json').read_text(encoding='utf-8')) if r['code'] == args.country)
    with contextlib.redirect_stdout(io.StringIO()):
        reference = analyze(DATA / 'countries' / Path(record['url']).name, DATA / 'mapping.json', 'pearson', '', '', None)
    ref_roles = role_sets(reference['highlights'])

    summary, roles_rows, directions, nulls, surrogates = [], [], [], [], []
    kept_ids = {mapping[c]['target'] + '::' + c.split('_', 1)[1] for c in raw}
    results = {}
    for option in OPTIONS:
        print(f'Option {option}…', flush=True)
        res = build(raw, scores, norm, mapping, option)
        results[option] = res
        d = Counter(n['direction'] for n in res['nodes'])
        roles = role_sets(res['highlights'])
        possible = len(res['nodes']) * (len(res['nodes']) - 1)
        summary.append(dict(option=option, indicators=len(raw), nodes=len(res['nodes']), improving=d['forward'],
                            deteriorating=d['backward'], stable_or_undetermined=d['stable'] + d['undetermined'],
                            pairs_tested=sum(p['r'] is not None for p in res['pairs']),
                            pairs_p10=sum(p['p'] < .1 and p['r'] != 0 for p in res['pairs']),
                            arcs=len(res['edges']), density=len(res['edges']) / possible if possible else None,
                            arcs_retained=res['actions']['retained'], arcs_reclassified=res['actions']['reclassified'],
                            arcs_excluded=res['actions']['excluded'],
                            synergies=sum(e['interaction'] == 'synergy' for e in res['edges'])))
        for role, members in roles.items():
            roles_rows.append(dict(option=option, role=role, members='; '.join(sorted(members)),
                                   jaccard_with_scores_procedure=jaccard(members, ref_roles[role]),
                                   jaccard_with_scores_restricted=jaccard(members, ref_roles[role] & kept_ids),
                                   scores_procedure_members_dropped='; '.join(sorted(ref_roles[role] - kept_ids))))
        print(f'  null model and surrogates…', flush=True)
        s, _ = null_model(res['nodes'], res['edges'], replicates=args.replicates)
        nulls += [dict(option=option, **r) for r in s]
        goal_of = {c: mapping[c]['goal'] for c in raw}
        for basis in ('levels', 'changes'):
            surrogates.append(dict(option=option, **surrogate_density(res['series'], goal_of, replicates=args.surrogates,
                                                                      basis=basis)))
    for c in sorted(raw):
        directions.append(dict(indicator=c, target=mapping[c]['target'], normative_sign=norm[c],
                               **{o: results[o]['trends'][c]['progress_direction'] for o in OPTIONS},
                               raw_time_r2=results['raw_trend']['trends'][c]['time_r2'],
                               score_time_r2=results['score']['trends'][c]['time_r2'],
                               scores_procedure=reference['trends']['n_' + c]['progress_direction']))

    out = Path(args.out or ROOT / 'output' / 'validity' / f'{args.country}_raw.xlsx')
    out.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)
    for title, items in [('Summary', summary), ('Roles', roles_rows), ('Directions', directions),
                         ('Null_summary', nulls), ('Surrogates', surrogates), ('Coverage', coverage)]:
        sheet = wb.create_sheet(title)
        head = list(dict.fromkeys(k for r in items for k in r))
        sheet.append(head)
        for r in items:
            sheet.append([r.get(k) for k in head])
        sheet.freeze_panes = 'B2'
    for option in OPTIONS:
        sheet = wb.create_sheet(f'Network_{option}')
        head = ['source', 'target', 'interaction', 'interaction_original', 'coefficient', 'weight', 'classification_action']
        sheet.append(head)
        for e in results[option]['edges']:
            sheet.append([e[k] for k in head])
    wb.save(out)
    print(out)


if __name__ == '__main__':
    main()
