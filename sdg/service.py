'Shared analysis interface for the terminal and Gradio.'
import csv
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from openpyxl import Workbook, load_workbook

from .engine import sdg_interlinkages as iges
from .render import render_networks

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
METHODS = ('IGES_JRC', 'SDGIndex')
SCOPES = ('region', 'country')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def normalize_scope(scope):
    return {"regiao": "region", "pais": "country"}.get(scope, scope)


def list_areas(version, scope):
    'Return stable codes and area names from local catalogs.'
    scope = normalize_scope(scope)
    if version not in METHODS or scope not in SCOPES:
        raise ValueError('Invalid dataset or area scope.')
    if version == 'IGES_JRC':
        from .engine.modules.collection import continental_regions
        tree = read_json(DATA / 'areas.json')
        areas = iges.countries_from_tree(tree) if scope == 'country' else continental_regions(tree)
        result = {str(code): row['name'] for code, row in areas.items()}
        if scope == 'region':
            for group in read_json(DATA / 'iges_comparison_regions.json')['groups']:
                result[str(group['code'])] = group['name']
        return result
    country = scope == 'country'
    records = read_json(DATA / 'SDGIndex' / ('countries.json' if country else 'catalog.json'))
    return {r['code' if country else 'region']: r['title'] for r in records}


def export_csv(path, records, required):
    columns = list(dict.fromkeys([*required, *(k for row in records for k in row)]))
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)


def sdg_run(folder, code, title, scope, method):
    from sdgindex_country import analyze
    base = DATA / 'SDGIndex'
    if scope == 'country':
        record = next(r for r in read_json(base / 'countries.json') if r['code'] == code)
        source = base / 'countries' / Path(record['url']).name
    else:
        source = base / 'regions' / f"Region_{code}.xlsx"
    prefix = f"{code}_{method}"
    folder.mkdir()
    full = folder / f"{prefix}_full.xlsx"
    result = analyze(source, base / 'mapping.json', method, code, title, full,
                     scope='country' if scope == 'country' else 'region')
    graph = result['network']
    export_csv(folder / f"{prefix}_nodes.csv", graph['nodes'], ['id', 'target', 'indicator'])
    export_csv(folder / f"{prefix}_network.csv", graph['edges'], ['source', 'target', 'interaction', 'weight'])
    book = load_workbook(full, read_only=True, data_only=True)
    from performance_ranking import format_years, RANK_KEYS
    from roles import MEASURES
    role = {row[1]: g['title'] for g in result['highlights'] for row in g['rows']}
    summary = Workbook()
    summary.remove(summary.active)
    try:
        for name, metric in [('TopCollaborators', 'colab'), ('TopNeglected', 'neglect')]:
            tab = summary.create_sheet(name)
            tab.append(['Target', 'Indicator', 'Value', 'Direction', 'years_to_target', 'years_to_zero', 'latest_score', 'latest_year', 'slope', *RANK_KEYS])
            for n in sorted(graph['nodes'], key=lambda n: (-n[metric], n['id'])):
                tab.append([n['target'], n['indicator'], n[metric], n['direction'], *[n[k] for k in ('years_to_target', 'years_to_zero', 'latest_score', 'latest_year', 'slope', *RANK_KEYS)]])
        for name in ['Target_time_ranking', 'Zero_time_ranking', 'Highlights', 'Dependence_diagnostics', 'Adverse cases']:
            tab = summary.create_sheet(name)
            for row in book[name].values:
                tab.append(row)
        tab = summary.create_sheet('Interface_measures')
        fields = ('colab', 'neglect', *MEASURES)
        tab.append(['Target', 'Indicator', 'Direction', 'Role', *fields])
        for n in sorted(graph['nodes'], key=lambda n: n['id']):
            tab.append([n['target'], n['indicator'], n['direction'], role.get(n['id'], ''), *[n.get(k) for k in fields]])
        # Formatting needs editable cells, so use a regular workbook.
        format_years(summary)
        summary.save(folder / f"{prefix}_interlinkages.xlsx")
    finally:
        book.close()
    render_networks(folder, prefix, title, graph, result['highlights'], DATA / 'icons')


def iges_run(folder, code, title, csv_path, work, modules, alpha=0.1):
    region = {'code': int(code), 'name': title}
    source = csv_path or iges.download_csv(modules[0], region, work / 'api.csv')
    pipeline_work = work / 'processing'
    pipeline_work.mkdir()
    produced = iges.run_pipeline(modules, pipeline_work, region, source, work / 'result', alpha=alpha)
    shutil.copytree(produced, folder, dirs_exist_ok=True)
    full = next(folder.glob('*_full.xlsx'))
    ranking = modules[4]
    metrics, assessments, series, descriptions = ranking.read_source(full)
    names = ranking.load_descriptions(iges.BASES / 'sdg_descriptions.xlsx')
    details, _ = ranking.prepare_details(metrics, assessments, series, descriptions, *names)
    from progress import workbook_edges, highlight_groups
    edges = workbook_edges(full)
    graph = dict(nodes=[dict(id=t, target=t, direction=details[t][5], colab=v['Colab'],
                             neglect=v['Neglect']) for t, v in metrics.items()],
                 edges=[dict(source=str(e['TargetA']), target=str(e['TargetB']),
                             weight=abs(float(e['weight'])), interaction=e['interaction']) for e in edges])
    prefix = full.stem.removesuffix('_full')
    render_networks(folder, prefix, title, graph, highlight_groups(metrics, details, edges), DATA / 'icons')
    # Link-share weighted version (NT Dinte 77): same network, weighted measures, sizes and roles.
    from progress import interface_nodes
    weighted = interface_nodes(metrics, details, edges, pond=True)
    graph_pond = dict(graph, nodes=[dict(n, colab=weighted[n['id']]['colab'], neglect=weighted[n['id']]['neglect'],
                                         interface_scale=weighted[n['id']]['relative_out'] * weighted[n['id']]['relative_in'])
                                    for n in graph['nodes']])
    render_networks(folder, prefix, title + ' · weighted by link share', graph_pond,
                    highlight_groups(metrics, details, edges, pond=True), DATA / 'icons', suffix='_pond')


def run_analysis(version, scope, code, *, method=None, csv_path=None, output_dir=None, alpha=0.1):
    'Run without input(). Return the complete execution folder. Suitable for a queued callback.'
    scope = normalize_scope(scope)
    method = "both" if method == "ambos" else method
    areas = list_areas(version, scope)
    code = str(code)
    if code not in areas:
        raise ValueError(f"Invalid code for {version}/{scope}: {code}")
    if method not in (None, 'pearson', 'spearman', 'both'):
        raise ValueError('Unknown correlation method.')
    if version == 'IGES_JRC' and method not in (None, 'pearson'):
        raise ValueError('IGES/JRC uses Pearson.')
    if csv_path is not None and version != 'IGES_JRC':
        raise ValueError('The UNSD CSV applies only to IGES/JRC.')
    root = Path(output_dir or ROOT / 'output').resolve()
    for branch in METHODS:
        (root / branch).mkdir(parents=True, exist_ok=True)
    area_name = "World" if version == "IGES_JRC" and code == "1" else iges.load_modules(Path())[0].file_name(areas[code])
    parent = root / version / scope / area_name
    parent.mkdir(parents=True, exist_ok=True)
    destination = parent / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid4().hex[:12])
    with tempfile.TemporaryDirectory(dir=parent, prefix='.tmp-') as tmp:
        work = Path(tmp)
        ready = work / 'delivery'
        ready.mkdir()
        modules = iges.load_modules(work)
        if version == 'IGES_JRC':
            iges_run(ready, code, areas[code], Path(csv_path) if csv_path else None, work, modules, alpha)
        else:
            methods = ('pearson', 'spearman') if method in (None, 'both') else (method,)
            for selected in methods:
                sdg_run(ready / selected, code, areas[code], scope, selected)
        ready.rename(destination)
    return destination

