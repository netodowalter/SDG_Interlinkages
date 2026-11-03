"""Compute Pearson correlations for prepared SDG API workbooks. Preserve originals and write copies with a Pearson sheet to correlations/."""
from itertools import combinations
from math import isfinite
from pathlib import Path
import os
import sys
import warnings

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.workbook.properties import CalcProperties
from scipy.stats import pearsonr

FOLDER = Path(__file__).resolve().parent
PATTERN = '*_SDG_API_2000_2025.xlsx'
OUTPUT_FOLDER = FOLDER / 'correlations'
RESULT_SHEET = 'Pearson'
COLUMNS = [
    'IndicatorA', 'IndicatorB', 'Pearson', 'Sig',
    'Significance', 'TargetA', 'TargetB',
]


def number(value):
    # Preserve zero and negative values. Published bounds such as <2.5 are not numeric observations.
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) if isfinite(value) else None
    return None


def significance(p):
    if p < 0.01:
        return 'Very high'
    if p < 0.05:
        return 'high'
    if p < 0.1:
        return 'Mean'
    return 'No'


from identity import representatives

def read_series(path):
    # data_only retrieves calculated values rather than formula text.
    workbook = load_workbook(path, data_only=True, read_only=True)
    try:
        if 'Series' not in workbook.sheetnames:
            raise ValueError('Series sheet not found.')
        target_rows = iter(workbook['Series'].values)
        fields = {name: i for i, name in enumerate(next(target_rows))}
        metadata_rows = [dict(zip(fields, row)) for row in target_rows if row[fields['series_id']]]
        canonical, legend = representatives(metadata_rows)
        targets = {row['series_id']: row['targets'] for row in metadata_rows}
        for item in legend:
            targets[item['canonical_series_id']]=item['representative']

        candidates = []
        for sheet in workbook:
            if sheet.title == 'Fill_status' or sheet.title.endswith(('_original', '_long')):
                continue
            header = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
            if (
                len(header) >= 3
                and header[0:2] == ('year', 'region')
                and any(name in targets for name in header[2:])
            ):
                candidates.append((sheet.title, header))

        if len(candidates) != 1:
            raise ValueError(
                'Era esperada uma unica aba regional; '
                f'found {len(candidates)}: '
                + ', '.join(name for name, _ in candidates)
            )

        sheet_name, header = candidates[0]
        indices = [(i, name) for i, name in enumerate(header) if name in targets]
        series = {name: [] for _, name in indices}
        for row in workbook[sheet_name].iter_rows(min_row=2, values_only=True):
            if not row or number(row[0]) is None:
                continue
            for i, name in indices:
                series[name].append(number(row[i] if i < len(row) else None))

        if not any(any(v is not None for v in values) for values in series.values()):
            raise ValueError(
                'No calculated numeric values. Open the original in Excel, recalculate, save and run again.'
            )
        # Use known measure identity rather than perfect correlation. Differences between
        # copies of one measure are input errors and must not be silently deduplicated.
        for sid, representative in canonical.items():
            if sid!=representative and sid in series and representative in series:
                if series[sid]!=series[representative]:
                    raise ValueError('Copies of the same measure have different observations: '+sid+', '+representative)
        series = {sid:values for sid,values in series.items() if canonical.get(sid,sid)==sid}
        targets = {sid:target for sid,target in targets.items() if canonical.get(sid,sid)==sid}
        return sheet_name, series, targets
    finally:
        workbook.close()


def compute(series, targets):
    results = []
    ignored = 0
    for a, b in combinations(series, 2):
        # One row per pair; no diagonal or repeated reverse pair.
        pairs = [
            (x, y) for x, y in zip(series[a], series[b])
            if x is not None and y is not None
        ]
        if len(pairs) < 3:
            ignored += 1
            continue
        x, y = zip(*pairs)
        if len(set(x)) < 2 or len(set(y)) < 2:
            ignored += 1
            continue
        r, p = pearsonr(x, y)
        r, p = float(r), float(p)
        if not (isfinite(r) and isfinite(p)):
            ignored += 1
            continue
        results.append([
            a, b, r, p, significance(p), targets.get(a, ''), targets.get(b, ''),
        ])
    return results, ignored


def save(path, results, output_folder=OUTPUT_FOLDER):
    # Reopen with formulas to preserve them in the output copy.
    workbook = load_workbook(path)
    destination = output_folder / (path.stem + '_correlations.xlsx')
    temporary_path = destination.with_name(destination.stem + '.tmp.xlsx')
    try:
        if RESULT_SHEET in workbook.sheetnames:
            del workbook[RESULT_SHEET]
        sheet = workbook.create_sheet(RESULT_SHEET)
        sheet.append(COLUMNS)
        for row in results:
            sheet.append(row)
        sheet.freeze_panes = 'A2'
        sheet.auto_filter.ref = sheet.dimensions
        sheet.sheet_view.showGridLines = False
        for cell in sheet[1]:
            cell.font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='23445E')
        for column in ('A', 'B'):
            sheet.column_dimensions[column].width = 29
        for column in ('C', 'D', 'E', 'F', 'G'):
            sheet.column_dimensions[column].width = 21
        for row in sheet.iter_rows(min_row=2):
            row[2].number_format = '0.000000'
            row[3].number_format = '0.000E+00'
        workbook.calculation = CalcProperties(calcMode='auto', fullCalcOnLoad=True)
        workbook.save(temporary_path)
        os.replace(temporary_path, destination)
        return destination
    finally:
        workbook.close()
        if temporary_path.exists():
            temporary_path.unlink()


def main():
    files = sorted(p for p in FOLDER.glob(PATTERN) if not p.name.startswith('~$'))
    if not files:
        print(f'No workbook matches the pattern {PATTERN} in {FOLDER}')
        return 1
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    print(f'{len(files)} workbooks found.', flush=True)
    failures = []
    for i, path in enumerate(files, 1):
        print(f'\n[{i}/{len(files)}] {path.name}', flush=True)
        try:
            sheet_name, series, targets = read_series(path)
            results, ignored = compute(series, targets)
            if not results:
                raise ValueError('No pair has at least three common years and variation.')
            destination = save(path, results)
            print(
                f'  Sheet: {sheet_name} | {len(results):,} calculated pairs | '
                f'{ignored:,} pairs without a calculation', flush=True,
            )
            print(f'  Saved: {destination.name}', flush=True)
        except Exception as error:
            failures.append((path.name, str(error)))
            print(f'  ERROR: {error}', flush=True)
    print(f'\nCompleted: {len(files)-len(failures)} of {len(files)} workbooks.')
    print(f'Pearson copies saved in: {OUTPUT_FOLDER}')
    if failures:
        print("""
Files not processed:""")
        for name, error in failures:
            print(f'  {name}: {error}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
