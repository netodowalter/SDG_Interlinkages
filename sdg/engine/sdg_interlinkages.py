#!/usr/bin/env python3
"""Integrated IGES/JRC pipeline for Python 3.10+.
Collect UNSD observations or reuse a CSV, select/fill 2000–2025 series,
consolidate shared measures, calculate Pearson and apply literature direction
and temporal classification before network metrics. Final files contain audit,
local trends, target ambition, rankings and adverse cases. Formula caches are
preserved. Use python -m sdg for the shared command-line interface."""
from pathlib import Path
import argparse
import csv
import importlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASES = ROOT / 'bases'


def load_modules(folder):
    module_folder = ROOT / 'modules'
    if str(module_folder) not in sys.path:
        sys.path.insert(0, str(module_folder))
    return [importlib.import_module(name) for name in ('collection', 'preparation', 'pearson', 'networks', 'ranking')]


def choose_type(requested):
    if requested:
        return requested
    print("""
1. Regions
2. Countries""")
    while True:
        choice = input('Choose 1 or 2: ').strip()
        if choice in ('1', '2'):
            return 'regions' if choice == '1' else 'countries'
        print('Enter 1 or 2.')


def countries_from_tree(tree):
    # Deduplicate countries appearing in multiple UNSD groupings.
    countries = {}
    def visit(node):
        if str(node.get('type', '')).casefold() == 'country':
            code = int(node['geoAreaCode'])
            countries.setdefault(code, dict(code=code, name=node['geoAreaName'], level=0))
        for child in node.get('children') or []:
            visit(child)
    for node in tree:
        visit(node)
    if not countries:
        raise ValueError('Country).=The UNSD tree returned no countries (type=Country).=Country).')
    return dict(sorted(countries.items(), key=lambda item: item[1]['name'].casefold()))


def choose_region(regions, requested, kind='regions'):
    if requested is not None:
        try:
            return regions[int(requested)]
        except (KeyError, ValueError):
            matches = [r for r in regions.values() if r['name'].casefold() == requested.casefold()]
            if len(matches) == 1:
                return matches[0]
            raise ValueError('Region not found: ' + requested)
    label = 'country' if kind == 'countries' else 'region'
    print(f'\nEscolha a {label} by code:' if kind == 'regions' else """
Choose the country by code:""")
    for r in regions.values():
        print(f"  {r['code']:>3}  {'  ' * r.get('level', 0)}{r['name']}")
    while True:
        value = input(f'\nCode ({label}): ').strip()
        try:
            return regions[int(value)]
        except (ValueError, KeyError):
            print('Enter one of the listed codes.')


def download_csv(collection, region, output):
    rows, seen, columns = [], set(), {}
    lots = [collection.INDICATORS[i:i+collection.BATCH_SIZE]
            for i in range(0, len(collection.INDICATORS), collection.BATCH_SIZE)]
    for index, lot in enumerate(lots, 1):
        page = 1
        expected_pages = None
        while True:
            params = dict(indicator=lot, areaCode=[region['code']], timePeriodStart=2000,
                          page=page, pageSize=collection.PAGE_SIZE)
            response = collection.fetch(collection.BASE + '/Indicator/Data?' + collection.urlencode(params, doseq=True))
            if not isinstance(response, dict) or not isinstance(response.get('data'), list) or 'totalPages' not in response:
                raise ValueError('Incomplete API response; collection stopped.')
            total = int(response['totalPages'])
            if expected_pages is not None and total != expected_pages:
                raise ValueError('API pagination changed during collection. Run again.')
            expected_pages = total
            for record in response['data']:
                if int(record['geoAreaCode']) != region['code']:
                    raise ValueError('API returned a different region from the one requested.')
                signature = json.dumps(record, sort_keys=True, ensure_ascii=False)
                if signature in seen:
                    continue
                seen.add(signature)
                row = collection.flatten(record)
                columns.update(dict.fromkeys(row))
                rows.append(row)
            print(f'  Batch {index}/{len(lots)}, page {page}/{total}', flush=True)
            if page >= total:
                break
            if not response['data']:
                raise ValueError('API returned an empty page before collection ended.')
            page += 1
    if not rows:
        raise ValueError('The API returned no observations for this region.')
    with output.open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(rows)
    return output


def csv_number(value):
    'Convert CSV decimal-point numeric text into numeric XLSX values.'
    text = (value or '').strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return value
    return int(number) if number.is_integer() and 'e' not in text.lower() and '.' not in text else number


def formula_cache(path):
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    result = {}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.startswith('xl/worksheets/sheet') or not name.endswith('.xml'):
                continue
            values = {}
            for cell in ET.fromstring(archive.read(name)).iter(ns+'c'):
                if cell.find(ns+'f') is None:
                    continue
                value = cell.find(ns+'v')
                text = value.text if value is not None else None
                values[cell.get('r')] = (text if cell.get('t') == 'str' else float(text)) if text else None
            if values:
                result[name] = values
    return result


def run_pipeline(modules, folder, region, csv_path, output_parent):
    collection, prep, pearson, net, ranking = modules
    regions = prep.read_csv_groups(csv_path)
    if not regions or str(region['code']) not in regions:
        raise ValueError('The CSV lacks the selected region or expected columns.')
    data = regions[str(region['code'])]
    name = collection.file_name('World' if region['code'] == 1 else region['name'])
    if not name:
        raise ValueError('Empty region name.')
    iges = prep.load_iges(BASES/'iges_correspondence.xlsx')
    rules = {prep.rule_key(r):r for r in prep.DEFAULT_CONFIG['rules']}
    print('[2/5] Selecting indicators and filling gaps with CAGR...', flush=True)
    selections = prep.select_series(iges, rules, data['groups'], 2000, 2025)
    selected = sum(s['status'] == 'selected' for s in selections)
    if not selected:
        raise ValueError('No numeric series with an IGES mapping is available for this region.')
    initial = folder / (name + '.xlsx')
    prep.write_region(initial, name, str(region['code']), selections, 2000, 2025,
                      'UNSD API; region '+str(region['code'])+'; collection '+datetime.now(timezone.utc).isoformat())
    caches = formula_cache(initial)
    print(f'  {selected}/{len(selections)} targets with a numeric series.', flush=True)
    print('[3/5] Pearson...', flush=True)
    _, series, targets = pearson.read_series(initial)
    results, ignored = pearson.compute(series, targets)
    if not results:
        raise ValueError('No series pair supports Pearson calculation.')
    correlations = pearson.save(initial, results, folder)
    prep.cache_formulas(correlations,caches)
    print('[4/5] Interlinkages and Cytoscape files...', flush=True)
    directions, _ = net.load_directions(BASES/'iges_decisions.xlsx', BASES/'jrc_decisions.xlsx')
    norm = net.Normativity(BASES/'indicator_directionality.xlsx', ROOT/'series_directions.csv')
    audit_folder = folder/'auditoria'
    counts = net.process_file(correlations, audit_folder, norm, directions, 0.1)
    final = correlations.with_name(correlations.stem+'_final.xlsx')
    print('[5/5] Rankings and four final data files...', flush=True)
    prep.cache_formulas(final, caches)
    from progress import analyze_workbook
    analyze_workbook(final,norm)
    target_names, indicator_names = ranking.load_descriptions(BASES/'sdg_descriptions.xlsx')
    metrics, assessments, series, descriptions = ranking.read_source(final)
    details, warnings = ranking.prepare_details(metrics, assessments, series, descriptions, target_names, indicator_names)
    ready = folder/'delivery'
    ready.mkdir()
    from progress import read_cases
    ranking.save_rankings(ready/(name+'_interlinkages.xlsx'), metrics, details,read_cases(final),__import__('progress').workbook_edges(final))
    # Link-share weighted version (NT Dinte 77): own workbook, always produced for IGES/JRC.
    ranking.save_rankings(ready/(name+'_interlinkages_pond.xlsx'), metrics, details,read_cases(final),__import__('progress').workbook_edges(final),pond=True)
    # Preserve the audit inside the final workbook.
    from openpyxl import load_workbook
    workbook = load_workbook(final)
    for filename, sheetname in [('edge_audit.csv','Edge_audit'),
                                 ('unresolved_directionality.csv','Unresolved_directionality'),
                                 ('target_degrees.csv','Target_degrees')]:
        sheet = workbook.create_sheet(sheetname)
        with (audit_folder/filename).open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            sheet.append(header)
            numeric = [name in net.NUMERIC_COLUMNS for name in header]
            for row in reader:
                # CSV decimals become numeric XLSX cells,
                # displayed according to the Excel locale.
                sheet.append([csv_number(v) if i < len(numeric) and numeric[i] else v
                              for i, v in enumerate(row)])
        prep.format_sheet(sheet)
    # Include the same tables in the full workbook downloaded by the app.
    rankings_book=load_workbook(ready/(name+'_interlinkages.xlsx'),data_only=True)
    for ranked_sheet in rankings_book:
        if ranked_sheet.title in workbook.sheetnames:del workbook[ranked_sheet.title]
        target_sheet=workbook.create_sheet(ranked_sheet.title)
        for values in ranked_sheet.values:target_sheet.append(values)
        prep.format_sheet(target_sheet)
    rankings_book.close()
    full = ready/(name+'_full.xlsx')
    workbook.save(full)
    workbook.close()
    prep.cache_formulas(full, caches)
    shutil.copyfile(folder/(name+'_rede_cytoscape.csv'), ready/(name+'_network.csv'))
    shutil.copyfile(folder/(name+'_targets_cytoscape.csv'), ready/(name+'_nodes.csv'))
    output_parent.mkdir(parents=True, exist_ok=True)
    destination = output_parent/name
    if destination.exists():
        destination = output_parent/(name+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    # Stage on the same volume and publish the directory only when complete.
    staging = Path(tempfile.mkdtemp(prefix='.sdg_', dir=output_parent))
    try:
        for file in ready.iterdir():
            shutil.copy2(file, staging/file.name)
        os.rename(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(f"\nCompleted: {counts['final_edges']} edges, {len(metrics)} targets in the rankings.")
    print(f"Pairs with unresolved directionality: {counts['unresolved_directionality']} (see full.xlsx).")
    for label, missing in warnings.items():
        print('Warning: '+label+': '+', '.join(sorted(missing)))
    print('Progress direction: local linear trend. Ambition: complete user-supplied table for all 169 targets.')
    print('Final files: '+str(destination.resolve()))
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--scope', choices=('regions', 'countries'), help='Area scope; default: Regions/Countries menu.')
    parser.add_argument('--region', help='UNSD code or exact region name; default: menu.')
    parser.add_argument('--output', type=Path, default=ROOT/'output', help='Results folder; default: output/ beside the program.')
    parser.add_argument('--csv', type=Path, help='Optional: reuse an existing CSV collection.')
    args = parser.parse_args(argv)
    try:
        import openpyxl
        import scipy
    except ImportError:
        raise RuntimeError('Install dependencies: py -m pip install openpyxl scipy')
    with tempfile.TemporaryDirectory(prefix='sdg_interlinkages_') as temporary:
        folder = Path(temporary)
        modules = load_modules(folder)
        collection, prep = modules[:2]
        if args.csv:
            available = prep.read_csv_groups(args.csv)
            if not available:
                raise ValueError('Invalid or empty CSV.')
            regions = {int(code):dict(code=int(code), name=r['name'], level=0) for code,r in available.items()}
        else:
            kind = choose_type(args.scope)
            print('Loading the UNSD area list...', flush=True)
            tree = collection.fetch(collection.BASE+'/GeoArea/Tree')
            regions = countries_from_tree(tree) if kind == 'countries' else collection.continental_regions(tree)
        region = choose_region(regions, args.region, (args.scope or 'regions') if args.csv else kind)
        print('[1/5] '+('Reading an existing CSV...' if args.csv else 'Downloading data for '+region['name']+'...'), flush=True)
        csv_path = args.csv or download_csv(collection, region, folder/'api.csv')
        run_pipeline(modules, folder, region, csv_path, args.output)
    return 0



if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("""
Execution cancelled; temporary files removed.""", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print("""
ERROR: """+str(exc), file=sys.stderr)
        sys.exit(1)
