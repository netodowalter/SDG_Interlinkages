"""Download every UNSD SDG Global Database observation for one country (all indicators, all series).

Usage: python -X utf8 scripts/download_unsd_country.py [AREA_CODE] [--start YEAR]
Default: 76 (Brazil), from 2000. Writes output/unsd/UNSD_<code>_<start>.csv and keeps the downloaded
pages in output/unsd/pages_<code>_<start>/ so an interrupted run resumes where it stopped.
Standard library only (shares fetch/flatten with the package's collection module).
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sdg/engine/modules'))
from collection import BASE, fetch, flatten, save_json  # noqa: E402

BATCH, PAGE_SIZE = 10, 1000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('area', nargs='?', default='76')
    parser.add_argument('--start', type=int, default=2000)
    args = parser.parse_args()
    folder = ROOT / 'output' / 'unsd'
    pages = folder / f'pages_{args.area}_{args.start}'
    pages.mkdir(parents=True, exist_ok=True)

    listing = pages / 'indicator_list.json'
    if not listing.exists():
        print('Listing indicators…', flush=True)
        save_json(listing, fetch(BASE + '/Indicator/List'))
    codes = sorted({item['code'] for item in json.loads(listing.read_text(encoding='utf-8'))},
                   key=lambda c: [int(p) if p.isdigit() else p for p in c.split('.')])
    print(f'{len(codes)} indicators.', flush=True)

    rows, seen, columns = [], set(), {}
    lots = [codes[i:i + BATCH] for i in range(0, len(codes), BATCH)]
    for number, lot in enumerate(lots, 1):
        page = 1
        while True:
            cache = pages / f'lot{number:03}_page{page:03}.json'
            if cache.exists():
                response = json.loads(cache.read_text(encoding='utf-8'))
            else:
                params = dict(indicator=lot, areaCode=[args.area], timePeriodStart=args.start,
                              page=page, pageSize=PAGE_SIZE)
                response = fetch(BASE + '/Indicator/Data?' + urlencode(params, doseq=True))
                if not isinstance(response, dict) or not isinstance(response.get('data'), list):
                    raise SystemExit('Incomplete API response; run again to resume.')
                save_json(cache, response)
            total = int(response.get('totalPages') or 1)
            print(f'Lot {number}/{len(lots)} ({lot[0]}…{lot[-1]}): page {page}/{total}, '
                  f'{len(response["data"])} records', flush=True)
            for record in response['data']:
                signature = json.dumps(record, sort_keys=True, ensure_ascii=False)
                if signature in seen:
                    continue
                seen.add(signature)
                row = flatten(record)
                columns.update(dict.fromkeys(row))
                rows.append(row)
            if page >= total:
                break
            page += 1

    out = folder / f'UNSD_{args.area}_{args.start}.csv'
    with out.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(rows)
    print(f'\n{len(rows)} observations written to {out}')


if __name__ == '__main__':
    main()
