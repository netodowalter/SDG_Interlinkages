'Collect UNSD observations for IGES indicator codes from 2000 onward. Resume saved pages and export regional CSVs. Uses only the Python standard library.'
import csv
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg'
START_YEAR = 2000
PAGE_SIZE = 1000
BATCH_SIZE = 10
FOLDER = Path(__file__).resolve().parent / 'IGES_continental_2000_onward'
INDICATORS = """
1.1.1 1.2.1 1.3.1 1.5.1 1.a.2
2.1.1 2.2.1 2.2.2 2.3.1 2.4.1 2.5.1 2.5.2 2.a.1 2.a.2 2.c.1
3.1.1 3.2.1 3.3.1 3.3.2 3.3.3 3.4.1 3.5.2 3.6.1 3.7.1 3.7.2
3.8.2 3.9.2 3.9.3 3.a.1 3.b.1 3.c.1 3.d.1
4.1.1 4.2.1 4.2.2 4.3.1 4.4.1 4.5.1 4.6.1 4.a.1 4.b.1 4.c.1
5.2.1 5.3.1 5.4.1 5.5.1 5.6.1 5.b.1
6.1.1 6.2.1 6.3.1 6.4.1 6.4.2 6.6.1 6.a.1
7.1.1 7.1.2 7.2.1 7.3.1
8.1.1 8.10.1 8.2.1 8.3.1 8.4.2 8.5.1 8.5.2 8.6.1 8.8.1 8.a.1
9.1.2 9.2.1 9.3.1 9.3.2 9.4.1 9.5.1 9.5.2 9.a.1 9.b.1 9.c.1
10.1.1 10.4.1 10.5.1 10.6.1 10.a.1 10.b.1 10.c.1
11.1.1 11.2.1 11.5.1 11.6.2 11.b.1 11.b.2
12.2.2 12.4.1 12.5.1 12.a.1 12.c.1 13.1.1
14.4.1 14.5.1 14.a.1
15.1.1 15.2.1 15.3.1 15.4.1 15.5.1 15.a.1 15.b.1
16.1.1 16.3.2 16.5.2 16.6.1 16.8.1 16.9.1
17.1.1 17.2.1 17.3.2 17.4.1 17.6.2 17.8.1 17.9.1 17.11.1
17.12.1 17.13.1 17.15.1 17.17.1 17.19.1
""".split()


def save_json(path, object_value):
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8') as f:
        json.dump(object_value, f, ensure_ascii=False, allow_nan=False)
    os.replace(temp, path)


def fetch(url):
    for attempt in range(7):
        try:
            req = Request(url, headers={'Accept': 'application/json'})
            with urlopen(req, timeout=180) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (408, 429, 500, 502, 503, 504) or attempt == 6:
                raise
            wait_seconds = min(60, 2 ** (attempt + 1))
            if error.headers.get('Retry-After', '').isdigit():
                wait_seconds = min(60, int(error.headers['Retry-After']))
        except (URLError, TimeoutError, ConnectionError, json.JSONDecodeError):
            if attempt == 6:
                raise
            wait_seconds = min(60, 2 ** (attempt + 1))
        print(f'  Retry in {wait_seconds}s...', flush=True)
        time.sleep(wait_seconds)


def continental_regions(tree):
    root_node = next(n for n in tree
                if n['geoAreaName'] == 'World (total) by continental regions')
    result = {}

    def traverse(node, parent=None, level=0):
        # Antarctica is a Country in the tree; exclude countries from this region traversal.
        if node.get('type') != 'Region':
            return
        code = int(node['geoAreaCode'])
        result[code] = dict(code=code, name=node['geoAreaName'],
                                 parent=parent, level=level)
        for child in node.get('children') or []:
            traverse(child, code, level + 1)
    traverse(root_node)
    return result


def flatten(object_value, prefix=''):
    result = {}
    for key, value in object_value.items():
        name = f'{prefix}_{key}' if prefix else key
        if isinstance(value, dict):
            result.update(flatten(value, name))
        elif isinstance(value, list):
            result[name] = json.dumps(value, ensure_ascii=False)
        else:
            result[name] = value
    return result


def file_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub('[^A-Za-z0-9]+', '_', name).strip('_')


def main():
    FOLDER.mkdir(exist_ok=True)
    cache = FOLDER / 'saved_pages'
    cache.mkdir(exist_ok=True)
    config_path = FOLDER / 'configuration.json'
    fixed_parameters = dict(start=START_YEAR, indicators=INDICATORS,
                            batch_size=BATCH_SIZE, page_size=PAGE_SIZE)
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        if config['parameters'] != fixed_parameters:
            raise ValueError('Configuration changed. Choose another folder for a new collection.')
        regions = {int(k): v for k, v in config['regions'].items()}
    else:
        regions = continental_regions(fetch(BASE + '/GeoArea/Tree'))
        config = dict(parameters=fixed_parameters, regions=regions,
                      created_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                      scope='IGES codes and all their official series/disaggregations. This is not an exact selection of historical IGES proxies.')
        save_json(config_path, config)

    print(f'{len(INDICATORS)} indicadores; {len(regions)} regions; since {START_YEAR}.')
    for r in regions.values():
        print(f"{'  ' * r['level']}{r['code']}: {r['name']}")
    files = []
    batches = [INDICATORS[i:i + BATCH_SIZE]
             for i in range(0, len(INDICATORS), BATCH_SIZE)]
    for number, batch in enumerate(batches, 1):
        page = 1
        while True:
            destination = cache / f'lote_{number:03d}_pagina_{page:06d}.json'
            if destination.exists():
                response = json.loads(destination.read_text(encoding='utf-8'))
                source = 'already saved'
            else:
                params = dict(indicator=batch, areaCode=list(regions),
                              timePeriodStart=START_YEAR, page=page,
                              pageSize=PAGE_SIZE)
                response = fetch(BASE + '/Indicator/Data?' + urlencode(params, doseq=True))
                if not isinstance(response, dict) or not isinstance(response.get('data'), list):
                    raise ValueError(f'Unexpected response in batch {number}, page {page}.')
                if 'totalPages' not in response:
                    raise ValueError('Response lacks totalPages; pagination cannot be safely completed.')
                save_json(destination, response)
                source = 'downloaded'
            files.append(destination)
            total = int(response['totalPages'])
            print(f'Batch {number}/{len(batches)} | page {page}/{total} '
                  f"| {len(response['data'])} records | {source}", flush=True)
            if page >= total:
                break
            page += 1

    # Two passes avoid loading the complete collection into memory.
    columns = {}
    for file in files:
        for record in json.loads(file.read_text(encoding='utf-8'))['data']:
            for key in flatten(record):
                columns.setdefault(key, None)
    csv_folder = FOLDER / 'csv_by_region'
    csv_folder.mkdir(exist_ok=True)
    outputs, writers = {}, {}
    counts = {c: 0 for c in regions}
    seen = set()
    duplicates = 0
    consolidated = FOLDER / 'IGES_continental_2000_onward.json'
    temporary_path = consolidated.with_suffix('.json.tmp')
    try:
        for code, region in regions.items():
            path = csv_folder / f"{code:03d}_{file_name(region['name'])}.csv"
            outputs[code] = path.open('w', newline='', encoding='utf-8-sig')
            writers[code] = csv.DictWriter(outputs[code], fieldnames=list(columns))
            writers[code].writeheader()
        with temporary_path.open('w', encoding='utf-8') as output:
            output.write('[')
            first = True
            for file in files:
                records = json.loads(file.read_text(encoding='utf-8'))['data']
                for record in records:
                    code = int(record['geoAreaCode'])
                    if code not in regions:
                        raise ValueError(f'API returned an unrequested area: {code}')
                    text_value = json.dumps(record, ensure_ascii=False, sort_keys=True)
                    signature = hashlib.sha256(text_value.encode('utf-8')).digest()
                    if signature in seen:
                        duplicates += 1
                        continue
                    seen.add(signature)
                    output.write(('' if first else """,
""") + text_value)
                    first = False
                    writers[code].writerow(flatten(record))
                    counts[code] += 1
            output.write("""]
""")
        os.replace(temporary_path, consolidated)
    finally:
        for f in outputs.values():
            f.close()
    save_json(FOLDER / 'collection_summary.json', dict(
        records=sum(counts.values()), exact_duplicates_removed=duplicates,
        records_per_region=counts,
        completed_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    print(f'\nCompleted: {sum(counts.values()):,} unique records; '
          f'{duplicates:,} duplicatas exatas removidas.')
    print(f'JSON consolidado e CSVs por region em: {FOLDER}')
    print('Regions without observations will receive a header-only CSV.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("""
Interrupted. Run again to resume saved pages.""")
        sys.exit(1)
    except Exception as error:
        print(f'\nERROR: {error}\nRun again to resume saved pages.', file=sys.stderr)
        sys.exit(1)
