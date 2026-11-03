"""Correlacoes de Pearson para todas as planilhas SDG API na pasta deste script.

Instalacao: py -m pip install openpyxl scipy
Execucao:   py pearson_todas_as_regioes.py

Originais sao preservados. Copias com a aba Pearson ficam em correlacoes/.
Tambem processa Europe_SDG_API_2000_2025.xlsx, caso esteja na mesma pasta.
"""
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

PASTA = Path(__file__).resolve().parent
PADRAO = '*_SDG_API_2000_2025.xlsx'
PASTA_SAIDA = PASTA / 'correlacoes'
ABA_RESULTADO = 'Pearson'
COLUNAS = [
    'IndicadorA', 'IndicadorB', 'Pearson', 'Sig',
    'Significance', 'MetaA', 'MetaB',
]


def numero(valor):
    # Preserva zero e negativos. Limites publicados como '<2.5' nao sao numeros.
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor) if isfinite(valor) else None
    return None


def significancia(p):
    if p < 0.01:
        return 'Muito alta'
    if p < 0.05:
        return 'alta'
    if p < 0.1:
        return 'Media'
    return 'Não'


from identidade import representatives

def ler_series(caminho):
    # data_only recupera os valores calculados, e nao o texto das formulas.
    livro = load_workbook(caminho, data_only=True, read_only=True)
    try:
        if 'Series' not in livro.sheetnames:
            raise ValueError('Aba Series nao encontrada.')
        linhas_meta = iter(livro['Series'].values)
        campos = {nome: i for i, nome in enumerate(next(linhas_meta))}
        metadata_rows = [dict(zip(campos, linha)) for linha in linhas_meta if linha[campos['series_id']]]
        canonical, legend = representatives(metadata_rows)
        metas = {row['series_id']: row['targets'] for row in metadata_rows}
        for item in legend:
            metas[item['canonical_series_id']]=item['representative']

        candidatas = []
        for aba in livro:
            if aba.title == 'Fill_status' or aba.title.endswith(('_original', '_long')):
                continue
            cabecalho = next(aba.iter_rows(min_row=1, max_row=1, values_only=True), ())
            if (
                len(cabecalho) >= 3
                and cabecalho[0:2] == ('year', 'region')
                and any(nome in metas for nome in cabecalho[2:])
            ):
                candidatas.append((aba.title, cabecalho))

        if len(candidatas) != 1:
            raise ValueError(
                'Era esperada uma unica aba regional; '
                f'foram encontradas {len(candidatas)}: '
                + ', '.join(nome for nome, _ in candidatas)
            )

        nome_aba, cabecalho = candidatas[0]
        indices = [(i, nome) for i, nome in enumerate(cabecalho) if nome in metas]
        series = {nome: [] for _, nome in indices}
        for linha in livro[nome_aba].iter_rows(min_row=2, values_only=True):
            if not linha or numero(linha[0]) is None:
                continue
            for i, nome in indices:
                series[nome].append(numero(linha[i] if i < len(linha) else None))

        if not any(any(v is not None for v in valores) for valores in series.values()):
            raise ValueError(
                'Nao ha valores numericos calculados. Abra o original no Excel, '
                'recalcule, salve e execute novamente.'
            )
        # Identidade conhecida, não correlação perfeita. Divergências entre
        # cópias da mesma medida são erro de entrada e não geram deduplicação silenciosa.
        for sid, representative in canonical.items():
            if sid!=representative and sid in series and representative in series:
                if series[sid]!=series[representative]:
                    raise ValueError('Cópias da mesma medida têm observações diferentes: '+sid+', '+representative)
        series = {sid:values for sid,values in series.items() if canonical.get(sid,sid)==sid}
        metas = {sid:target for sid,target in metas.items() if canonical.get(sid,sid)==sid}
        return nome_aba, series, metas
    finally:
        livro.close()


def calcular(series, metas):
    resultados = []
    ignorados = 0
    for a, b in combinations(series, 2):
        # Uma linha por par; sem diagonal e sem repetir B,A.
        pares = [
            (x, y) for x, y in zip(series[a], series[b])
            if x is not None and y is not None
        ]
        if len(pares) < 3:
            ignorados += 1
            continue
        x, y = zip(*pares)
        if len(set(x)) < 2 or len(set(y)) < 2:
            ignorados += 1
            continue
        r, p = pearsonr(x, y)
        r, p = float(r), float(p)
        if not (isfinite(r) and isfinite(p)):
            ignorados += 1
            continue
        resultados.append([
            a, b, r, p, significancia(p), metas.get(a, ''), metas.get(b, ''),
        ])
    return resultados, ignorados


def salvar(caminho, resultados, pasta_saida=PASTA_SAIDA):
    # Reabre com as formulas para preserva-las na copia de saida.
    livro = load_workbook(caminho)
    destino = pasta_saida / (caminho.stem + '_correlacoes.xlsx')
    temporario = destino.with_name(destino.stem + '.tmp.xlsx')
    try:
        if ABA_RESULTADO in livro.sheetnames:
            del livro[ABA_RESULTADO]
        aba = livro.create_sheet(ABA_RESULTADO)
        aba.append(COLUNAS)
        for linha in resultados:
            aba.append(linha)
        aba.freeze_panes = 'A2'
        aba.auto_filter.ref = aba.dimensions
        aba.sheet_view.showGridLines = False
        for celula in aba[1]:
            celula.font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
            celula.fill = PatternFill('solid', fgColor='23445E')
        for coluna in ('A', 'B'):
            aba.column_dimensions[coluna].width = 29
        for coluna in ('C', 'D', 'E', 'F', 'G'):
            aba.column_dimensions[coluna].width = 21
        for linha in aba.iter_rows(min_row=2):
            linha[2].number_format = '0.000000'
            linha[3].number_format = '0.000E+00'
        livro.calculation = CalcProperties(calcMode='auto', fullCalcOnLoad=True)
        livro.save(temporario)
        os.replace(temporario, destino)
        return destino
    finally:
        livro.close()
        if temporario.exists():
            temporario.unlink()


def main():
    arquivos = sorted(p for p in PASTA.glob(PADRAO) if not p.name.startswith('~$'))
    if not arquivos:
        print(f'Nenhuma planilha encontrada com o padrao {PADRAO} em {PASTA}')
        return 1
    PASTA_SAIDA.mkdir(exist_ok=True)
    print(f'{len(arquivos)} planilhas encontradas.', flush=True)
    falhas = []
    for i, caminho in enumerate(arquivos, 1):
        print(f'\n[{i}/{len(arquivos)}] {caminho.name}', flush=True)
        try:
            nome_aba, series, metas = ler_series(caminho)
            resultados, ignorados = calcular(series, metas)
            if not resultados:
                raise ValueError('Nenhum par com pelo menos tres anos comuns e variacao.')
            destino = salvar(caminho, resultados)
            print(
                f'  Aba: {nome_aba} | {len(resultados):,} pares calculados | '
                f'{ignorados:,} pares sem calculo', flush=True,
            )
            print(f'  Salvo: {destino.name}', flush=True)
        except Exception as erro:
            falhas.append((caminho.name, str(erro)))
            print(f'  ERRO: {erro}', flush=True)
    print(f'\nConcluido: {len(arquivos)-len(falhas)} de {len(arquivos)} planilhas.')
    print(f'Copias com Pearson em: {PASTA_SAIDA}')
    if falhas:
        print('\nArquivos nao processados:')
        for nome, erro in falhas:
            print(f'  {nome}: {erro}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
