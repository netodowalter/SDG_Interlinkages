#!/usr/bin/env python3
"""Gera [region]_interlinkages.xlsx a partir de *_final.xlsx.

Python >= 3.10; dependência: openpyxl (py -m pip install openpyxl).
Uso: py rankings_interlinkages.py
     py rankings_interlinkages.py --entrada "C:\\dados"
     py rankings_interlinkages.py --entrada "World_correlacoes_final.xlsx"

Coloque ods_descricao.xlsx na pasta dos arquivos de entrada ou deste script.
Saída: ao lado da entrada (ou em --saida), somente MaisColaboradoras e
MaisNegligenciadas. Nenhum arquivo de entrada é alterado.

Rankings decrescentes de Colab e de Neglect (maior = mais negligenciada), incluindo todas as metas conectadas
presentes em metas_cytoscape. Empates compartilham posição (1, 1, 3).
Uma linha por meta, com indicadores múltiplos separados por ponto e vírgula.
MetaDescricao: ODS.Meta.ONU, sem adaptação brasileira.
IndicadorODS: indicator_used e IndicadorNome: description, ambos da aba Series,
vinculados à meta por targets. Preserva as descrições das séries/proxies usadas.
Direção do progresso: tendência local. Ambição: tabela integral por meta
fornecida pelo usuário, independente das séries disponíveis e das avaliações antigas.
Cada aba inclui somente seu escore (Colab ou Neglect), logo após MetaODS.
"""
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

from ambicao import ambition_for
from progresso import ambition_band

ROOT = Path(__file__).resolve().parent
COLUMNS = ['Ranking', 'MetaODS', 'MetaDescricao', 'IndicadorODS', 'IndicadorNome',
           'ambicao_meta', 'direcao_progresso', 'ambicao_faixa']
WIDTHS = [11, 13, 20, 75, 25, 75, 14, 22, 32]


def text(value):
    return '' if value is None else str(value).strip()


def unique(values):
    return list(dict.fromkeys(v for v in values if v != '' and v is not None))


def codes(value, indicator=False):
    pattern = r'(?<![\d.])(?:1[0-7]|[1-9])\.(?:\d+|[a-z])'
    pattern += r'\.\d+(?![\w.])' if indicator else r'(?![\w.])'
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
        raise ValueError(f'{label}: valor numérico ausente ou inválido.')
    try:
        result = float(str(value).replace(',', '.'))
    except (ValueError, TypeError):
        raise ValueError(f'{label}: valor numérico inválido: {value!r}') from None
    if not math.isfinite(result):
        raise ValueError(f'{label}: valor não finito.')
    return result


def load_descriptions(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    targets = defaultdict(list)
    indicators = defaultdict(list)
    try:
        found = False
        for sheet in workbook:
            header = next(sheet.iter_rows(values_only=True), ())
            if not {'ODS.Meta.Code', 'ODS.Meta.ONU'} <= set(header):
                continue
            found = True
            for row in rows(sheet):
                for target in codes(row.get('ODS.Meta.Code')):
                    targets[target].append(text(row.get('ODS.Meta.ONU')))
                for indicator in codes(row.get('ODS.Indicador.Code'), True):
                    indicators[indicator].append(text(row.get('ODS.Indicador.Nome')))
        if not found:
            raise ValueError(f'{path.name}: colunas ODS.Meta.Code e ODS.Meta.ONU ausentes.')
    finally:
        workbook.close()
    return ({k: ' | '.join(unique(v)) for k, v in targets.items()},
            {k: ' | '.join(unique(v)) for k, v in indicators.items()})


def read_source(path):
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        if 'metas_cytoscape' not in workbook.sheetnames:
            raise ValueError('Aba metas_cytoscape ausente. Execute o código das redes atualizado.')
        header = next(workbook['metas_cytoscape'].iter_rows(values_only=True), ())
        if not {'MetaODS', 'Colab', 'Neglect'} <= set(header):
            raise ValueError('metas_cytoscape deve conter MetaODS, Colab, Neglect.')
        metrics = {}
        for row in rows(workbook['metas_cytoscape']):
            target = text(row.get('MetaODS'))
            if codes(target) != [target]:
                raise ValueError(f'MetaODS inválida: {target!r}. Mantenha os códigos como texto.')
            values = {field: number(row.get(field), f'{target}/{field}')
                      for field in ('Colab', 'Neglect')}
            if target in metrics and metrics[target] != values:
                raise ValueError(f'Meta duplicada com escores conflitantes: {target}')
            metrics[target] = values
        # A tabela de nós já exclui isolados. Havendo arestas, confirma o recorte.
        if 'rede_cytoscape' in workbook.sheetnames:
            connected = set()
            edge_header = next(workbook['rede_cytoscape'].iter_rows(values_only=True), ())
            if not {'MetaA', 'MetaB'} <= set(edge_header):
                raise ValueError('rede_cytoscape deve conter MetaA e MetaB.')
            for row in rows(workbook['rede_cytoscape']):
                connected.update(codes(row.get('MetaA')))
                connected.update(codes(row.get('MetaB')))
            missing = connected - metrics.keys()
            if missing:
                raise ValueError('Metas conectadas sem escores: ' + ', '.join(sorted(missing, key=key)))
            metrics = {k: v for k, v in metrics.items() if k in connected}
        assessments = defaultdict(list)
        if 'Tendencia_local' in workbook.sheetnames:
            for trend in rows(workbook['Tendencia_local']):
                target=str(trend['MetaODS'])
                if not assessments[target]:assessments[target].append({})
                for assessment in assessments[target]:
                    assessment['direcao_progresso']=trend.get('direcao_progresso')
                    assessment['ambicao_faixa']=trend.get('ambicao_faixa')
        series = defaultdict(list)
        descriptions = defaultdict(list)
        if 'Series' not in workbook.sheetnames:
            raise ValueError('Aba Series ausente: necessária para identificar os indicadores utilizados.')
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
            raise ValueError(f'Múltiplas direções locais para {target}.')
        metadata = assessment[0] if assessment else {}
        indicators = unique(series.get(target, []))
        if not indicators:
            warnings['meta sem indicador associado em Series'].add(target)
        if not target_names.get(target):
            warnings['sem descrição ONU em ods_descricao.xlsx'].add(target)
        names = []
        for indicator in indicators:
            name = ' | '.join(unique(descriptions.get((target, indicator), [])))
            if not name:
                name = '[nome não disponível]'
                warnings['indicador sem description em Series'].add(indicator)
            names.append(f'{indicator}: {name}')
        ambition = ambition_for(target)
        details[target] = [target, target_names.get(target, ''), '; '.join(indicators),
                           '; '.join(names), ambition, metadata.get('direcao_progresso','indeterminada'), ambition_band(ambition)]
    return details, warnings


def ranked_rows(metrics, details, metric):
    # Ambos decrescentes: maior Colab = mais colaboradora; maior Neglect = mais negligenciada.
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
        for name, metric in [('MaisColaboradoras', 'Colab'), ('MaisNegligenciadas', 'Neglect')]:
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
                                           for part in text(cell.value).split('\n')))
                sheet.row_dimensions[row[0].row].height = min(409, max(30, lines * 16 + 8))
        from progresso import highlight_groups, case_sheet, dependence_diagnostics
        case_sheet(workbook,adverse_cases)
        diagnostics=dependence_diagnostics(metrics,details,edges)
        if 'Diagnostico_dependencia' in workbook.sheetnames:del workbook['Diagnostico_dependencia']
        ds=workbook.create_sheet('Diagnostico_dependencia')
        if diagnostics:
            headers=list(diagnostics[0]);ds.append(headers)
            for item in diagnostics:ds.append([item.get(k) for k in headers])
            ds.freeze_panes='B2';ds.auto_filter.ref=ds.dimensions
        highlights=workbook.create_sheet('Destaques')
        highlights.append(['Grupo','Metrica']+COLUMNS[:2]+['Escore']+COLUMNS[2:])
        for group in highlight_groups(metrics,details,edges):
            if not group['rows']:highlights.append([group['title'],group['metric'],'Nenhuma meta elegível'])
            for row in group['rows']:highlights.append([group['title'],group['metric']]+row)
        highlights.freeze_panes='E2';highlights.auto_filter.ref=highlights.dimensions
        for i in range(1,highlights.max_column+1):highlights.column_dimensions[get_column_letter(i)].width=25
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
    return re.sub(r'(?:_correlacoes)?_final$', '', path.stem, flags=re.I)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--entrada', type=Path, default=ROOT, help='Pasta ou um arquivo *_final.xlsx.')
    parser.add_argument('--descricoes', type=Path, help='Caminho de ods_descricao.xlsx.')
    parser.add_argument('--saida', type=Path, help='Pasta de saída; padrão: pasta de cada entrada.')
    args = parser.parse_args(argv)
    if not args.entrada.exists():
        parser.error(f'Entrada não encontrada: {args.entrada}')
    files = [args.entrada] if args.entrada.is_file() else sorted(args.entrada.glob('*_final.xlsx'))
    files = [p for p in files if not p.name.startswith(('~$', '.'))]
    if not files:
        parser.error('Nenhum arquivo *_final.xlsx encontrado.')
    failures = 0
    used = set()
    for source in files:
        try:
            description_path = args.descricoes
            if description_path is None:
                description_path = source.parent / 'ods_descricao.xlsx'
                if not description_path.is_file():
                    description_path = ROOT / 'ods_descricao.xlsx'
            if not description_path.is_file():
                raise ValueError(f'Descrições não encontradas: {description_path}')
            target_names, indicator_names = load_descriptions(description_path)
            metrics, assessments, series, descriptions = read_source(source)
            details, warnings = prepare_details(metrics, assessments, series, descriptions,
                                                target_names, indicator_names)
            output = (args.saida or source.parent) / (region_name(source) + '_interlinkages.xlsx')
            if output.resolve() in used:
                raise ValueError(f'Duas entradas gerariam a mesma saída: {output}')
            if output.resolve() in (source.resolve(), description_path.resolve()):
                raise ValueError('Saída não pode substituir arquivo de entrada.')
            used.add(output.resolve())
            from progresso import read_cases
            save_rankings(output, metrics, details,read_cases(source),__import__('progresso').workbook_edges(source))
            print(f'Criado: {output} — {len(metrics)} metas em cada ranking.', flush=True)
            for label, missing in warnings.items():
                print(f'  Aviso: {label}: ' + ', '.join(sorted(missing)), flush=True)
        except Exception as exc:
            failures += 1
            print(f'ERRO em {source.name}: {exc}', file=sys.stderr, flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
