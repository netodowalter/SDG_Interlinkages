#!/usr/bin/env python3
"""Pipeline ODS integrado — Python 3.10+ (Windows, Linux e macOS).

Instalação única: py -m pip install openpyxl scipy
Execução: py ods_interlinkages.py
Escolha o código da região no menu. Saída em output/ ao lado deste script: pasta da região ou país
com apenas <regiao>_full.xlsx, <regiao>_interlinkages.xlsx,
<regiao>_network.csv e <regiao>_nodes.csv.

Período: 2000–2025; Pearson bilateral, mínimo 3 pares, alpha=0.1.
Uma série por meta: mais anos numéricos originais; empate pela ordem IGES.
Uma única meta representa cada série/dimensões/unidade selecionada repetida.
Legenda em Representacao_metas; séries originais preservadas para auditoria.
CAGR e regras normativas preservados dos cinco scripts fornecidos.
Ambicao_metas usa a tabela integral fornecida pelo usuário; direção do progresso é local.
As cinco tabelas auxiliares estão em bases/ e os módulos em modulos/.
Mantenha essas pastas junto do programa. Use launch.bat no Windows.
Os intermediários são temporários e removidos inclusive em caso de erro.
Auditoria e pendências ficam em abas do full.xlsx. Fórmulas mantêm seus caches.

Opções: --tipo regions|countries --regiao CODIGO --saida PASTA --csv CSV_EXISTENTE (dispensa download).
Se a pasta de saída já existir, cria uma pasta com data/hora, preservando-a.
"""
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
    module_folder = ROOT / 'modulos'
    if str(module_folder) not in sys.path:
        sys.path.insert(0, str(module_folder))
    return [importlib.import_module(name) for name in ('coleta', 'preparo', 'pearson', 'redes', 'ranking')]


def choose_type(requested):
    if requested:
        return requested
    print('\n1. Regions\n2. Countries')
    while True:
        choice = input('Escolha 1 ou 2: ').strip()
        if choice in ('1', '2'):
            return 'regions' if choice == '1' else 'countries'
        print('Digite 1 ou 2.')


def countries_from_tree(tree):
    # Deduplica países que aparecem em mais de um agrupamento da UNSD.
    countries = {}
    def visit(node):
        if str(node.get('type', '')).casefold() == 'country':
            code = int(node['geoAreaCode'])
            countries.setdefault(code, dict(codigo=code, nome=node['geoAreaName'], nivel=0))
        for child in node.get('children') or []:
            visit(child)
    for node in tree:
        visit(node)
    if not countries:
        raise ValueError('A árvore da UNSD não retornou países (type=Country).')
    return dict(sorted(countries.items(), key=lambda item: item[1]['nome'].casefold()))


def choose_region(regions, requested, kind='regions'):
    if requested is not None:
        try:
            return regions[int(requested)]
        except (KeyError, ValueError):
            matches = [r for r in regions.values() if r['nome'].casefold() == requested.casefold()]
            if len(matches) == 1:
                return matches[0]
            raise ValueError('Região não encontrada: ' + requested)
    label = 'país' if kind == 'countries' else 'região'
    print(f'\nEscolha a {label} pelo código:' if kind == 'regions' else '\nEscolha o país pelo código:')
    for r in regions.values():
        print(f"  {r['codigo']:>3}  {'  ' * r.get('nivel', 0)}{r['nome']}")
    while True:
        value = input(f'\nCódigo ({label}): ').strip()
        try:
            return regions[int(value)]
        except (ValueError, KeyError):
            print('Digite um dos códigos listados.')


def download_csv(coleta, region, output):
    rows, seen, columns = [], set(), {}
    lots = [coleta.INDICADORES[i:i+coleta.TAMANHO_LOTE]
            for i in range(0, len(coleta.INDICADORES), coleta.TAMANHO_LOTE)]
    for index, lot in enumerate(lots, 1):
        page = 1
        expected_pages = None
        while True:
            params = dict(indicator=lot, areaCode=[region['codigo']], timePeriodStart=2000,
                          page=page, pageSize=coleta.TAMANHO_PAGINA)
            response = coleta.obter(coleta.BASE + '/Indicator/Data?' + coleta.urlencode(params, doseq=True))
            if not isinstance(response, dict) or not isinstance(response.get('data'), list) or 'totalPages' not in response:
                raise ValueError('Resposta da API incompleta; coleta interrompida.')
            total = int(response['totalPages'])
            if expected_pages is not None and total != expected_pages:
                raise ValueError('A paginação da API mudou durante a coleta. Execute novamente.')
            expected_pages = total
            for record in response['data']:
                if int(record['geoAreaCode']) != region['codigo']:
                    raise ValueError('API retornou uma região diferente da solicitada.')
                signature = json.dumps(record, sort_keys=True, ensure_ascii=False)
                if signature in seen:
                    continue
                seen.add(signature)
                row = coleta.achatar(record)
                columns.update(dict.fromkeys(row))
                rows.append(row)
            print(f'  Lote {index}/{len(lots)}, página {page}/{total}', flush=True)
            if page >= total:
                break
            if not response['data']:
                raise ValueError('API retornou página vazia antes do fim da coleta.')
            page += 1
    if not rows:
        raise ValueError('A API não retornou observações para esta região.')
    with output.open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(rows)
    return output


def csv_number(value):
    """Converte texto numérico com ponto decimal (CSV) em número para o XLSX."""
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
    coleta, prep, pearson, net, ranking = modules
    regions = prep.read_csv_groups(csv_path)
    if not regions or str(region['codigo']) not in regions:
        raise ValueError('CSV não contém a região escolhida ou não tem as colunas esperadas.')
    data = regions[str(region['codigo'])]
    name = coleta.nome_arquivo('World' if region['codigo'] == 1 else region['nome'])
    if not name:
        raise ValueError('Nome de região vazio.')
    iges = prep.load_iges(BASES/'table_iges.xlsx')
    rules = {prep.rule_key(r):r for r in prep.DEFAULT_CONFIG['rules']}
    print('[2/5] Seleção dos indicadores e preenchimento por CAGR...', flush=True)
    selections = prep.select_series(iges, rules, data['groups'], 2000, 2025)
    selected = sum(s['status'] == 'selecionada' for s in selections)
    if not selected:
        raise ValueError('Nenhuma série com valores numéricos e correspondência IGES nesta região.')
    initial = folder / (name + '.xlsx')
    prep.write_region(initial, name, str(region['codigo']), selections, 2000, 2025,
                      'UNSD API; região '+str(region['codigo'])+'; coleta '+datetime.now(timezone.utc).isoformat())
    caches = formula_cache(initial)
    print(f'  {selected}/{len(selections)} metas com série numérica.', flush=True)
    print('[3/5] Pearson...', flush=True)
    _, series, targets = pearson.ler_series(initial)
    results, ignored = pearson.calcular(series, targets)
    if not results:
        raise ValueError('Nenhum par de séries permite calcular Pearson.')
    correlations = pearson.salvar(initial, results, folder)
    prep.cache_formulas(correlations,caches)
    print('[4/5] Interlinkages e arquivos Cytoscape...', flush=True)
    directions, _ = net.load_directions(BASES/'iges_decisao.xlsx', BASES/'jrc_decisao.xlsx')
    norm = net.Normativity(BASES/'normatividade.xlsx', ROOT/'sentidos_series.csv')
    audit_folder = folder/'auditoria'
    counts = net.process_file(correlations, audit_folder, norm, directions, 0.1)
    final = correlations.with_name(correlations.stem+'_final.xlsx')
    print('[5/5] Rankings e organização dos quatro arquivos finais...', flush=True)
    prep.cache_formulas(final, caches)
    from progresso import analyze_workbook
    analyze_workbook(final,norm)
    target_names, indicator_names = ranking.load_descriptions(BASES/'ods_descricao.xlsx')
    metrics, assessments, series, descriptions = ranking.read_source(final)
    details, warnings = ranking.prepare_details(metrics, assessments, series, descriptions, target_names, indicator_names)
    ready = folder/'entrega'
    ready.mkdir()
    from progresso import read_cases
    ranking.save_rankings(ready/(name+'_interlinkages.xlsx'), metrics, details,read_cases(final),__import__('progresso').workbook_edges(final))
    # Mantém a auditoria sem criar arquivos adicionais na pasta entregue.
    from openpyxl import load_workbook
    workbook = load_workbook(final)
    for filename, sheetname in [('auditoria_arestas.csv','Auditoria_arestas'),
                                 ('pendencias_normatividade.csv','Pendencias_normatividade'),
                                 ('graus_por_meta.csv','Graus_por_meta')]:
        sheet = workbook.create_sheet(sheetname)
        with (audit_folder/filename).open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            sheet.append(header)
            numeric = [name in net.NUMERIC_COLUMNS for name in header]
            for row in reader:
                # CSV mantém ponto decimal; no XLSX os valores viram números,
                # exibidos com vírgula decimal no Excel em português.
                sheet.append([csv_number(v) if i < len(numeric) and numeric[i] else v
                              for i, v in enumerate(row)])
        prep.format_sheet(sheet)
    # Inclui as mesmas listas no full baixado pelo app.
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
    shutil.copyfile(folder/(name+'_metas_cytoscape.csv'), ready/(name+'_nodes.csv'))
    output_parent.mkdir(parents=True, exist_ok=True)
    destination = output_parent/name
    if destination.exists():
        destination = output_parent/(name+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    # Cópia oculta no mesmo volume; publica a pasta somente quando completa.
    staging = Path(tempfile.mkdtemp(prefix='.ods_', dir=output_parent))
    try:
        for file in ready.iterdir():
            shutil.copy2(file, staging/file.name)
        os.rename(staging, destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(f"\nConcluído: {counts['arestas_finais']} arestas, {len(metrics)} metas nos rankings.")
    print(f"Pares com normatividade pendente: {counts['pendencias_normatividade']} (consulte o full.xlsx).")
    for label, missing in warnings.items():
        print('Aviso: '+label+': '+', '.join(sorted(missing)))
    print('Direção do progresso: tendência linear local. Ambição: tabela integral de 169 metas fornecida pelo usuário.')
    print('Arquivos finais em: '+str(destination.resolve()))
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--tipo', choices=('regions', 'countries'), help='Tipo de área; padrão: menu Regions/Countries.')
    parser.add_argument('--regiao', help='Código UNSD ou nome exato da região; padrão: menu.')
    parser.add_argument('--saida', type=Path, default=ROOT/'output', help='Pasta de resultados; padrão: output/ ao lado do programa.')
    parser.add_argument('--csv', type=Path, help='Opcional: reutilizar uma coleta CSV existente.')
    args = parser.parse_args(argv)
    try:
        import openpyxl
        import scipy
    except ImportError:
        raise RuntimeError('Instale as dependências: py -m pip install openpyxl scipy')
    with tempfile.TemporaryDirectory(prefix='ods_interlinkages_') as temporary:
        folder = Path(temporary)
        modules = load_modules(folder)
        coleta, prep = modules[:2]
        if args.csv:
            available = prep.read_csv_groups(args.csv)
            if not available:
                raise ValueError('CSV inválido ou vazio.')
            regions = {int(code):dict(codigo=int(code), nome=r['name'], nivel=0) for code,r in available.items()}
        else:
            kind = choose_type(args.tipo)
            print('Carregando a lista de áreas da UNSD...', flush=True)
            tree = coleta.obter(coleta.BASE+'/GeoArea/Tree')
            regions = countries_from_tree(tree) if kind == 'countries' else coleta.regioes_continentais(tree)
        region = choose_region(regions, args.regiao, (args.tipo or 'regions') if args.csv else kind)
        print('[1/5] '+('Lendo CSV existente...' if args.csv else 'Baixando dados de '+region['nome']+'...'), flush=True)
        csv_path = args.csv or download_csv(coleta, region, folder/'api.csv')
        run_pipeline(modules, folder, region, csv_path, args.saida)
    return 0



if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\nExecução cancelada; arquivos temporários removidos.', file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print('\nERRO: '+str(exc), file=sys.stderr)
        sys.exit(1)
