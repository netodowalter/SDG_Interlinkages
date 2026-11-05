"""Raw SDR values without trend: associations on levels, first differences and linear-trend
residuals (progress direction from the raw linear trend in all three).

Usage: python scripts/raw_detrended.py DATABASE.xlsx [ISO3] [--replicates N] [--surrogates N]"""
import argparse, json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT), str(ROOT / 'sdg/engine/modules')]
import raw_sdgindex as R  # noqa: E402
from openpyxl import Workbook, load_workbook  # noqa: E402
from validity import null_model, role_sets, surrogate_density  # noqa: E402

p = argparse.ArgumentParser(); p.add_argument('database'); p.add_argument('country', nargs='?', default='BRA')
p.add_argument('--replicates', type=int, default=200); p.add_argument('--surrogates', type=int, default=100)
a = p.parse_args()
mapping = {r['indicator'][2:]: r for r in json.loads((R.DATA / 'mapping.json').read_text(encoding='utf-8'))}
book = load_workbook(a.database, read_only=True, data_only=True)
raw_rows = [r for r in R.rows(book, 'All Raw Data') if r['id'] == a.country and r['year'] in R.YEARS]
score_rows = [r for r in R.rows(book, 'Backdated SDG Index') if r['id'] == a.country and r['year'] in R.YEARS]
codebook = {r['IndCode']: r for r in R.rows(book, 'Codebook')}
raw, scores, norm = {}, {}, {}
for c in sorted(mapping):
    v = {r['year']: R.number(r.get(c)) for r in raw_rows}; v = {y: x for y, x in v.items() if x is not None}
    total, run = R.gaps(v)
    if total <= R.MAX_TOTAL and run <= R.MAX_RUN and len(v) >= 2:
        cb = codebook[c]; norm[c] = 1 if cb['Optimum (= 100)'] > cb['Lower Bound (=0)'] else -1
        raw[c] = dict(observed=v, filled=R.fill(v)[0])
        scores[c] = {r['year']: R.number(r.get('n_' + c)) for r in score_rows if R.number(r.get('n_' + c)) is not None}
goal_of = {c: mapping[c]['goal'] for c in raw}
summary, roles_rows, nulls, surr, nets = [], [], [], [], {}
base_roles = None
for basis in ('levels', 'changes', 'detrended'):
    print('basis', basis, flush=True)
    res = R.build(raw, scores, norm, mapping, 'raw_trend', basis=basis)
    d = Counter(n['direction'] for n in res['nodes']); roles = role_sets(res['highlights'])
    base_roles = base_roles or roles
    n = len(res['nodes'])
    summary.append(dict(basis=basis, nodes=n, improving=d['forward'], deteriorating=d['backward'],
                        pairs_tested=sum(1 for _ in res['pairs']), pairs_p10=sum(x['p'] < .1 and x['r'] != 0 for x in res['pairs']),
                        arcs=len(res['edges']), density=len(res['edges']) / (n * (n - 1)) if n > 1 else None,
                        unidirectional_pairs=sum(x['p'] < .1 and x['direction'] in ('A_to_B', 'B_to_A') for x in res['pairs']),
                        arcs_retained=res['actions']['retained'], arcs_reclassified=res['actions']['reclassified'],
                        arcs_excluded=res['actions']['excluded'],
                        synergies=sum(e['interaction'] == 'synergy' for e in res['edges'])))
    for role, m in roles.items():
        b = base_roles[role]
        roles_rows.append(dict(basis=basis, role=role, members='; '.join(sorted(m)),
                               jaccard_with_levels=len(m & b) / len(m | b) if m | b else 1.0))
    s, members = null_model(res['nodes'], res['edges'], replicates=a.replicates)
    nulls += [dict(basis=basis, **r) for r in s]
    nets[basis] = (res, members)
    surr.append(dict(**surrogate_density(res['series'], goal_of, replicates=a.surrogates, basis=basis)))
out = ROOT / 'output' / 'validity' / f'{a.country}_raw_detrended.xlsx'
wb = Workbook(); wb.remove(wb.active)
for title, items in [('Summary', summary), ('Roles', roles_rows), ('Null_summary', nulls), ('Surrogates', surr)] + \
        [(f'Null_members_{b}', nets[b][1]) for b in nets]:
    sh = wb.create_sheet(title); head = list(dict.fromkeys(k for r in items for k in r)); sh.append(head)
    for r in items: sh.append([r.get(k) for k in head])
for b, (res, _) in nets.items():
    sh = wb.create_sheet(f'Network_{b}'); head = ['source', 'target', 'interaction', 'interaction_original', 'coefficient', 'weight', 'classification_action']
    sh.append(head)
    for e in res['edges']: sh.append([e[k] for k in head])
wb.save(out); print(out)
