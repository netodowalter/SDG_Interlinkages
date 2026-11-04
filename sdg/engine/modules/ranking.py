#!/usr/bin/env python3
'Create interlinkage rankings from final workbooks. Rank all connected targets by descending Colab and Neglect, sharing tied positions. Include local progress direction, ambition, highlights and adverse cases. Preserve descriptions of the selected measures and proxies.'
from __future__ import annotations

import argparse
import math
import os
import re
import sys
import tempfile
import textwrap
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from ambition import ambition_for
from progress import ambition_band

ROOT = Path(__file__).resolve().parent
COLUMNS = ['Ranking', 'TargetCode', 'TargetDescription', 'IndicatorCode', 'IndicatorName',
           'target_ambition', 'progress_direction', 'ambition_band']
WIDTHS = [11, 13, 20, 75, 25, 75, 14, 22, 32]


def text(value):
    return '' if value is None else str(value).strip()


def unique(values):
    return list(dict.fromkeys(v for v in values if v != '' and v is not None))


def codes(value, indicator=False):
    pattern = '(?<![\\d.])(?:1[0-7]|[1-9])\\.(?:\\d+|[a-z])'
    pattern += '\\.\\d+(?![\\w.])' if indicator else '(?![\\w.])'
    return unique(re.findall(pattern, text(value)))


def key(target):
    goal, suffix = target.split('.', 1)
    return (int(goal), 0, int(suffix)) if suffix.isdigit() else (int(goal), 1, suffix)


def rows(sheet):
    iterator = iter(sheet.iter_rows(values_only=True))
    headers = [text(v) for v in next(iterator, ())]
    for values in iterator:
        if any(v is not None for v in values):
            yield dict(zip(headers, values))


def number(value, label):
    if isinstance(value, bool) or value is None or text(value) == '':
        raise ValueError(f'{label}: missing or invalid numeric value.')
    try:
        result = float(str(value).replace(',', '.'))
    except (ValueError, TypeError):
        raise ValueError(f'{label}: invalid numeric value: {value!r}') from None
    if not math.isfinite(result):
        raise ValueError(f'{label}: non-finite value.')
    return result


def load_descriptions(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    targets = defaultdict(list)
    indicators = defaultdict(list)
    try:
        found = False
        for sheet in workbook:
            header = next(sheet.iter_rows(values_only=True), ())
            if not {'SDG.Target.Code', 'SDG.Target.UN'} <= set(header):
                continue
            found = True
            for row in rows(sheet):
                for target in codes(row.get('SDG.Target.Code')):
                    targets[target].append(text(row.get('SDG.Target.UN')))
                for indicator in codes(row.get('SDG.Indicator.Code'), True):
                    indicators[indicator].append(text(row.get('SDG.Indicator.Name')))
        if not found:
            raise ValueError(f'{path.name}: required SDG.Target.Code and SDG.Target.UN columns are missing.')
    finally:
        workbook.close()
    return ({k: ' | '.join(unique(v)) for k, v in targets.items()},
            {k: ' | '.join(unique(v)) for k, v in indicators.items()})


def read_source(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        if 'cytoscape_nodes' not in workbook.sheetnames:
            raise ValueError('Missing cytoscape_nodes sheet. Run the updated network code.')
        header = next(workbook['cytoscape_nodes'].iter_rows(values_only=True), ())
        if not {'TargetCode', 'Colab', 'Neglect'} <= set(header):
            raise ValueError('cytoscape_nodes must contain TargetCode, Colab and Neglect.')
        metrics = {}
        for row in rows(workbook['cytoscape_nodes']):
            target = text(row.get('TargetCode'))
            if codes(target) != [target]:
                raise ValueError(f'Invalid TargetCode: {target!r}. Keep codes as text.')
            values = {field: number(row.get(field), f'{target}/{field}')
                      for field in ('Colab', 'Neglect')}
            if target in metrics and metrics[target] != values:
                raise ValueError(f'Duplicate target with conflicting scores: {target}')
            metrics[target] = values
        # Node rows already exclude isolates. Check the edge-defined scope when edges exist.
        if 'cytoscape_edges' in workbook.sheetnames:
            connected = set()
            edge_header = next(workbook['cytoscape_edges'].iter_rows(values_only=True), ())
            if not {'TargetA', 'TargetB'} <= set(edge_header):
                raise ValueError('cytoscape_edges must contain TargetA and TargetB.')
            for row in rows(workbook['cytoscape_edges']):
                connected.update(codes(row.get('TargetA')))
                connected.update(codes(row.get('TargetB')))
            missing = connected - metrics.keys()
            if missing:
                raise ValueError('Connected targets without scores: ' + ', '.join(sorted(missing, key=key)))
            metrics = {k: v for k, v in metrics.items() if k in connected}
        assessments = defaultdict(list)
        if 'Local_trends' in workbook.sheetnames:
            for trend in rows(workbook['Local_trends']):
                target=str(trend['TargetCode'])
                if not assessments[target]:assessments[target].append({})
                for assessment in assessments[target]:
                    assessment['progress_direction']=trend.get('progress_direction')
                    assessment['ambition_band']=trend.get('ambition_band')
        series = defaultdict(list)
        descriptions = defaultdict(list)
        if 'Series' not in workbook.sheetnames:
            raise ValueError('Missing Series sheet, required to identify the indicators used.')
        for row in rows(workbook['Series']):
            indicators = codes(row.get('indicator_used') or row.get('indicator'), True)
            for target in codes(row.get('targets') or row.get('target')):
                series[target].extend(indicators)
                for indicator in indicators:
                    descriptions[target, indicator].append(text(row.get('description')))
        return metrics, assessments, series, descriptions
    finally:
        workbook.close()


def prepare_details(metrics, assessments, series, descriptions, target_names, indicator_names):
    details = {}
    warnings = defaultdict(set)
    for target in metrics:
        assessment = assessments.get(target, [])
        if len(assessment) > 1:
            raise ValueError(f'Multiple local directions for {target}.')
        metadata = assessment[0] if assessment else {}
        indicators = unique(series.get(target, []))
        if not indicators:
            warnings['target has no associated indicator in Series'].add(target)
        if not target_names.get(target):
            warnings['no UN description in sdg_descriptions.xlsx'].add(target)
        names = []
        for indicator in indicators:
            name = ' | '.join(unique(descriptions.get((target, indicator), [])))
            if not name:
                name = '[name unavailable]'
                warnings['indicator without description in Series'].add(indicator)
            names.append(f'{indicator}: {name}')
        ambition = ambition_for(target)
        details[target] = [target, target_names.get(target, ''), '; '.join(indicators),
                           '; '.join(names), ambition, metadata.get('progress_direction','undetermined'), ambition_band(ambition)]
    return details, warnings


def ranked_rows(metrics, details, metric):
    # Both rankings descend: greater Colab means more collaboration; greater Neglect means more neglect.
    ordered = sorted(metrics, key=lambda t: (-metrics[t][metric], key(t)))
    previous = None
    rank = 0
    for position, target in enumerate(ordered, 1):
        score = metrics[target][metric]
        if previous is None or score != previous:
            rank = position
        previous = score
        yield [rank, target, metrics[target][metric]] + details[target][1:]


def save_rankings(output, metrics, details, adverse_cases=(), edges=()):
    workbook = Workbook()
    workbook.remove(workbook.active)
    temporary = None
    try:
        for name, metric in [('TopCollaborators', 'Colab'), ('TopNeglected', 'Neglect')]:
            sheet = workbook.create_sheet(name)
            sheet.append(COLUMNS[:2] + [metric] + COLUMNS[2:])
            for row in ranked_rows(metrics, details, metric):
                sheet.append(row)
            sheet.freeze_panes = 'C2'
            sheet.auto_filter.ref = sheet.dimensions
            sheet.sheet_view.showGridLines = False
            sheet.row_dimensions[1].height = 32
            for i, width in enumerate(WIDTHS, 1):
                sheet.column_dimensions[get_column_letter(i)].width = width
            for cell in sheet[1]:
                cell.font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
                cell.fill = PatternFill('solid', fgColor='17365D')
                cell.alignment = Alignment(vertical='center', wrap_text=True)
            for row in sheet.iter_rows(min_row=2):
                lines = 1
                for i, cell in enumerate(row):
                    cell.font = Font(name='Calibri', size=11)
                    cell.alignment = Alignment(vertical='top', wrap_text=True)
                    if i in (1, 4):
                        cell.number_format = '@'
                    if i in (2, 6):
                        cell.number_format = '0.000' if i==6 else '0.########'
                    lines = max(lines, sum(max(1, len(textwrap.wrap(part, width=max(8, int(WIDTHS[i])-3))))
                                           for part in text(cell.value).split("""
""")))
                sheet.row_dimensions[row[0].row].height = min(409, max(30, lines * 16 + 8))
        from progress import highlight_groups, case_sheet, dependence_diagnostics
        case_sheet(workbook,adverse_cases)
        diagnostics=dependence_diagnostics(metrics,details,edges)
        if 'Dependence_diagnostics' in workbook.sheetnames:del workbook['Dependence_diagnostics']
        ds=workbook.create_sheet('Dependence_diagnostics')
        if diagnostics:
            headers=list(diagnostics[0]);ds.append(headers)
            for item in diagnostics:ds.append([item.get(k) for k in headers])
            ds.freeze_panes='B2';ds.auto_filter.ref=ds.dimensions
        highlights=workbook.create_sheet('Highlights')
        highlights.append(['Group','Metric']+COLUMNS[:2]+['Score']+COLUMNS[2:])
        for group in highlight_groups(metrics,details,edges):
            if not group['rows']:highlights.append([group['title'],group['metric'],'No eligible target'])
            for row in group['rows']:highlights.append([group['title'],group['metric']]+row)
        highlights.freeze_panes='E2';highlights.auto_filter.ref=highlights.dimensions
        for i in range(1,highlights.max_column+1):highlights.column_dimensions[get_column_letter(i)].width=25
        from progress import interface_rows
        interface=workbook.create_sheet('Interface_measures')
        measures=interface_rows(metrics,details,edges)
        if measures:
            headers=list(measures[0]);interface.append(headers)
            for item in measures:interface.append([item.get(k) for k in headers])
            interface.freeze_panes='B2';interface.auto_filter.ref=interface.dimensions
            for i in range(1,interface.max_column+1):interface.column_dimensions[get_column_letter(i)].width=22
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix='.' + output.stem + '_', suffix='.xlsx',
                                         dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
        workbook.save(temporary)
        workbook.close()
        os.replace(temporary, output)
    finally:
        workbook.close()
        if temporary is not None and temporary.exists():
            temporary.unlink()


def region_name(path):
    return re.sub('(?:_correlations)?_final$', '', path.stem, flags=re.I)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input', type=Path, default=ROOT, help='Folder or a single *_final.xlsx file.')
    parser.add_argument('--descriptions', type=Path, help='Caminho of ods_descricao.xlsx.')
    parser.add_argument('--output', type=Path, help='Output folder; default: each input folder.')
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f'Input not found: {args.input}')
    files = [args.input] if args.input.is_file() else sorted(args.input.glob('*_final.xlsx'))
    files = [p for p in files if not p.name.startswith(('~$', '.'))]
    if not files:
        parser.error('No *_final.xlsx file found.')
    failures = 0
    used = set()
    for source in files:
        try:
            description_path = args.descriptions
            if description_path is None:
                description_path = source.parent / 'sdg_descriptions.xlsx'
                if not description_path.is_file():
                    description_path = ROOT / 'sdg_descriptions.xlsx'
            if not description_path.is_file():
                raise ValueError(f'Descriptions not found: {description_path}')
            target_names, indicator_names = load_descriptions(description_path)
            metrics, assessments, series, descriptions = read_source(source)
            details, warnings = prepare_details(metrics, assessments, series, descriptions,
                                                target_names, indicator_names)
            output = (args.output or source.parent) / (region_name(source) + '_interlinkages.xlsx')
            if output.resolve() in used:
                raise ValueError(f'Two inputs would produce the same output: {output}')
            if output.resolve() in (source.resolve(), description_path.resolve()):
                raise ValueError('Output cannot replace the input file.')
            used.add(output.resolve())
            from progress import read_cases
            save_rankings(output, metrics, details,read_cases(source),__import__('progress').workbook_edges(source))
            print(f'Created: {output} — {len(metrics)} targets in each ranking.', flush=True)
            for label, missing in warnings.items():
                print(f'  Warning: {label}: ' + ', '.join(sorted(missing)), flush=True)
        except Exception as exc:
            failures += 1
            print(f'ERROR in {source.name}: {exc}', file=sys.stderr, flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
