"""Build SDGIndex-format country workbooks from Eurostat EU SDG indicator CSVs.

Usage: python scripts/eurostat_prepare.py [--countries FI:FIN:Finland BG:BGR:Bulgaria] [--start 2005] [--end 2024]

Inputs (data/Eurostat):
  csv/sdg_*.csv     SDMX-CSV downloads of the EU SDG indicator set (Eurostat)
  selection.json    one headline series per dataset, its desired direction and editorial target

Steps for each country, within the window:
 1. Headline series from selection.json (flagged values kept; confidential or missing values are gaps).
 2. Completeness rule of scripts/raw_sdgindex.py: at most 6 missing years and no run of more than 3.
 3. Gaps filled by the IGES/JRC CAGR rule (scripts/raw_sdgindex.fill); an indicator with a gap left empty
    is dropped.
 4. Scores on 0-100 by min-max over every Eurostat observation of the series (all countries, all years),
    oriented so that 100 is the best value. The transform is linear and never clips, so Pearson
    associations and linear-trend directions equal those of the raw values with the normative sign;
    no carried values are created by bounds.

Outputs (data/Eurostat):
  mapping_eurostat.json              indicators -> target and goal (format of data/SDGIndex/mapping.json)
  countries/<ISO3>_<Name>.xlsx       Component_observations (package format), Raw_values, Coverage, README
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT), str(ROOT / 'sdg/engine/modules')]
import raw_sdgindex as rs  # noqa: E402
from openpyxl import Workbook  # noqa: E402

BASE = ROOT / 'data' / 'Eurostat'


def code_of(entry):
    goal = int(entry['file'][4:6])
    return goal, f"n_sdg{goal}_eu{entry['file'][4:].replace('_', '')}"


def load(entry):
    df = pd.read_csv(BASE / 'csv' / f"{entry['file']}.csv", low_memory=False)
    for k, v in entry['filter'].items():
        df = df[df[k].astype(str) == v]
    df = df.dropna(subset=['OBS_VALUE'])
    if df.duplicated(['geo', 'TIME_PERIOD']).any():
        raise ValueError(f"{entry['file']}: filter does not identify one series per country-year")
    return df


def gaps(values, years):
    missing = [y not in values for y in years]
    run = best = 0
    for m in missing:
        run = run + 1 if m else 0
        best = max(best, run)
    return sum(missing), best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--countries', nargs='+', default=['FI:FIN:Finland', 'BG:BGR:Bulgaria'])
    parser.add_argument('--start', type=int, default=2005)
    parser.add_argument('--end', type=int, default=2024)
    args = parser.parse_args()
    years = list(range(args.start, args.end + 1))
    rs.YEARS = years
    selection = json.loads((BASE / 'selection.json').read_text(encoding='utf-8'))['indicators']

    mapping, frames = [], {}
    for entry in selection:
        goal, code = code_of(entry)
        df = load(entry)
        lo, hi = float(df.OBS_VALUE.min()), float(df.OBS_VALUE.max())
        frames[code] = (entry, df, lo, hi)
        mapping.append(dict(indicator=code, target=entry['target'], goal=goal, description=entry['description'],
                            rule=f"Eurostat {entry['file']} {json.dumps(entry['filter'])}; editorial target association.",
                            ambition=None, eurostat=entry['file'], sign=entry['sign']))
    (BASE / 'mapping_eurostat.json').write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding='utf-8')

    out_dir = BASE / 'countries'
    out_dir.mkdir(exist_ok=True)
    for spec in args.countries:
        geo, iso3, name = spec.split(':')
        obs, raw_rows, coverage = [], [], []
        for code, (entry, df, lo, hi) in frames.items():
            sub = df[df.geo == geo]
            values = {int(y): float(v) for y, v in zip(sub.TIME_PERIOD, sub.OBS_VALUE) if args.start <= y <= args.end}
            flags = {int(y): f for y, f in zip(sub.TIME_PERIOD, sub.OBS_FLAG.fillna('').astype(str)) if f not in ('', 'nan')}
            total, run = gaps(values, years)
            row = dict(indicator=code, eurostat=entry['file'], target=entry['target'], sign=entry['sign'],
                       description=entry['description'], first_year=min(sub.TIME_PERIOD, default=None),
                       last_year=max(sub.TIME_PERIOD, default=None), observed_in_window=len(values),
                       missing_years=total, longest_gap=run,
                       break_flags=sum('b' in flags.get(y, '') for y in years), kept=False, reason='')
            if total > 6 or run > 3 or len(values) < 2:
                row['reason'] = 'completeness rule'
                coverage.append(row)
                continue
            filled, kind = rs.fill(values)
            if not np.isfinite(filled).all():
                row['reason'] = 'gap not fillable by CAGR rule'
                coverage.append(row)
                continue
            if hi - lo <= 0 or np.std(filled) == 0:
                row['reason'] = 'constant series'
                coverage.append(row)
                continue
            row.update(kept=True, interpolated=kind['interpolated'], extrapolated=kind['extrapolated'])
            coverage.append(row)
            goal = int(entry['file'][4:6])
            for y, v in zip(years, filled):
                score = 100 * ((v - lo) if entry['sign'] > 0 else (hi - v)) / (hi - lo)
                obs.append(dict(geography=iso3, year=y, SDG=goal, indicator=code, indcode=code[2:],
                                description=entry['description'], indicator_score=round(score, 6)))
                raw_rows.append(dict(indicator=code, eurostat=entry['file'], year=y, value=v,
                                     observed=y in values, flag=flags.get(y)))
        book = Workbook()
        book.remove(book.active)
        for title, rows in [('Component_observations', obs), ('Raw_values', raw_rows), ('Coverage', coverage)]:
            sheet = book.create_sheet(title)
            head = list(dict.fromkeys(k for r in rows for k in r))
            sheet.append(head)
            for r in rows:
                sheet.append([None if isinstance(r.get(k), float) and math.isnan(r.get(k)) else r.get(k) for k in head])
            sheet.freeze_panes = 'B2'
        kept = sum(r['kept'] for r in coverage)
        readme = book.create_sheet('README')
        for item in [('Field', 'Definition'), ('Object', f'{iso3}_{name}'), ('Source', 'Eurostat, EU SDG indicator set (SDMX-CSV)'),
                     ('Years', f'{args.start}–{args.end}'),
                     ('Indicators', f'{kept} of {len(coverage)} selected headline series pass the completeness rule'),
                     ('Completeness', 'At most 6 missing years in the window and no run of more than 3 (as scripts/raw_sdgindex.py)'),
                     ('Gaps', 'IGES/JRC CAGR rule: interpolation between neighbours, extrapolation from the first or last two points'),
                     ('Scores', '0–100 min-max over all Eurostat observations of the series, oriented so that 100 is best; linear, no clipping'),
                     ('Targets', 'Editorial association (data/Eurostat/selection.json)')]:
            readme.append(item)
        path = out_dir / f'{iso3}_{name}.xlsx'
        book.save(path)
        print(path, kept, 'indicators')


if __name__ == '__main__':
    main()
