"""Run the SDGIndex procedure of the package on the Eurostat country workbooks.

Usage: python scripts/eurostat_run.py ISO3 [ISO3 ...] [--start 2005] [--end 2024] [--method both]

Uses data/Eurostat/countries/<ISO3>_<Name>.xlsx and data/Eurostat/mapping_eurostat.json (built by
scripts/eurostat_prepare.py). The package code is unchanged: the service runs on a temporary data root
whose SDGIndex catalog points to the Eurostat files, and the association window is set to --start/--end.
Results: output/Eurostat/<Name>/<run>/{pearson,spearman}/ and a ZIP of each run.
"""
import argparse
import functools
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'sdg/engine/modules')]

import sdgindex_country  # noqa: E402
from sdg import service  # noqa: E402

EU = ROOT / 'data' / 'Eurostat'


def data_root(tmp):
    root = Path(tmp) / 'data'
    (root / 'SDGIndex').mkdir(parents=True)
    files = sorted((EU / 'countries').glob('*.xlsx'))
    records = [dict(code=f.stem.split('_', 1)[0], title=f.stem.split('_', 1)[1].replace('_', ' '),
                    url=f'/sdgindex/countries/{f.name}') for f in files]
    (root / 'SDGIndex' / 'countries.json').write_text(json.dumps(records), encoding='utf-8')
    (root / 'SDGIndex' / 'catalog.json').write_text('[]', encoding='utf-8')
    shutil.copy(EU / 'mapping_eurostat.json', root / 'SDGIndex' / 'mapping.json')
    (root / 'SDGIndex' / 'countries').symlink_to(EU / 'countries')
    for name in ('icons', 'areas.json', 'iges_comparison_regions.json'):
        (root / name).symlink_to(ROOT / 'data' / name)
    return root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('countries', nargs='+')
    parser.add_argument('--start', type=int, default=2005)
    parser.add_argument('--end', type=int, default=2024)
    parser.add_argument('--method', default='both', choices=('pearson', 'spearman', 'both'))
    parser.add_argument('--output', default=str(ROOT / 'output' / 'Eurostat'))
    args = parser.parse_args()
    original = sdgindex_country.analyze
    sdgindex_country.analyze = functools.partial(original, start=args.start, end=args.end)
    with tempfile.TemporaryDirectory() as tmp:
        service.DATA = data_root(tmp)
        for code in args.countries:
            folder = service.run_analysis('SDGIndex', 'country', code, method=args.method, output_dir=args.output)
            archive = shutil.make_archive(str(folder.parent / f'{code}_Eurostat_{args.start}_{args.end}_{folder.name}'),
                                          'zip', folder)
            print(folder)
            print(archive)


if __name__ == '__main__':
    main()
