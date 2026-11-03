"""Coleta UNSD: indicadores IGES, 2000+, árvore continental sem países.
Python 3.9+; usa apenas a biblioteca padrão. Execute: py coletar_IGES_regioes_continentais.py
Reexecute para retomar páginas já salvas. Para nova atualização, use outra pasta de saída.
"""
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
INICIO = 2000
TAMANHO_PAGINA = 1000
TAMANHO_LOTE = 10
PASTA = Path(__file__).resolve().parent / 'IGES_continentais_2000_em_diante'
INDICADORES = '''
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
'''.split()


def salvar_json(caminho, objeto):
    temp = caminho.with_suffix(caminho.suffix + '.tmp')
    with temp.open('w', encoding='utf-8') as f:
        json.dump(objeto, f, ensure_ascii=False, allow_nan=False)
    os.replace(temp, caminho)


def obter(url):
    for tentativa in range(7):
        try:
            req = Request(url, headers={'Accept': 'application/json'})
            with urlopen(req, timeout=180) as resposta:
                return json.load(resposta)
        except HTTPError as erro:
            if erro.code not in (408, 429, 500, 502, 503, 504) or tentativa == 6:
                raise
            espera = min(60, 2 ** (tentativa + 1))
            if erro.headers.get('Retry-After', '').isdigit():
                espera = min(60, int(erro.headers['Retry-After']))
        except (URLError, TimeoutError, ConnectionError, json.JSONDecodeError):
            if tentativa == 6:
                raise
            espera = min(60, 2 ** (tentativa + 1))
        print(f'  Nova tentativa em {espera}s...', flush=True)
        time.sleep(espera)


def regioes_continentais(arvore):
    raiz = next(n for n in arvore
                if n['geoAreaName'] == 'World (total) by continental regions')
    resultado = {}

    def percorrer(no, pai=None, nivel=0):
        # Antarctica aparece como Country na árvore; países são excluídos.
        if no.get('type') != 'Region':
            return
        codigo = int(no['geoAreaCode'])
        resultado[codigo] = dict(codigo=codigo, nome=no['geoAreaName'],
                                 pai=pai, nivel=nivel)
        for filho in no.get('children') or []:
            percorrer(filho, codigo, nivel + 1)
    percorrer(raiz)
    return resultado


def achatar(objeto, prefixo=''):
    resultado = {}
    for chave, valor in objeto.items():
        nome = f'{prefixo}_{chave}' if prefixo else chave
        if isinstance(valor, dict):
            resultado.update(achatar(valor, nome))
        elif isinstance(valor, list):
            resultado[nome] = json.dumps(valor, ensure_ascii=False)
        else:
            resultado[nome] = valor
    return resultado


def nome_arquivo(nome):
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Za-z0-9]+', '_', nome).strip('_')


def main():
    PASTA.mkdir(exist_ok=True)
    cache = PASTA / 'paginas_salvas'
    cache.mkdir(exist_ok=True)
    config_path = PASTA / 'configuracao.json'
    parametros_fixos = dict(inicio=INICIO, indicadores=INDICADORES,
                            tamanho_lote=TAMANHO_LOTE, tamanho_pagina=TAMANHO_PAGINA)
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        if config['parametros'] != parametros_fixos:
            raise ValueError('Configuração mudou. Escolha outra PASTA para uma nova coleta.')
        regioes = {int(k): v for k, v in config['regioes'].items()}
    else:
        regioes = regioes_continentais(obter(BASE + '/GeoArea/Tree'))
        config = dict(parametros=parametros_fixos, regioes=regioes,
                      criado_em=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                      escopo='Códigos IGES; todas as séries/desagregações oficiais desses códigos. '
                             'Não equivale a uma seleção exata dos proxies históricos do IGES.')
        salvar_json(config_path, config)

    print(f'{len(INDICADORES)} indicadores; {len(regioes)} regiões; desde {INICIO}.')
    for r in regioes.values():
        print(f"{'  ' * r['nivel']}{r['codigo']}: {r['nome']}")
    arquivos = []
    lotes = [INDICADORES[i:i + TAMANHO_LOTE]
             for i in range(0, len(INDICADORES), TAMANHO_LOTE)]
    for numero, lote in enumerate(lotes, 1):
        pagina = 1
        while True:
            destino = cache / f'lote_{numero:03d}_pagina_{pagina:06d}.json'
            if destino.exists():
                resposta = json.loads(destino.read_text(encoding='utf-8'))
                origem = 'já salva'
            else:
                params = dict(indicator=lote, areaCode=list(regioes),
                              timePeriodStart=INICIO, page=pagina,
                              pageSize=TAMANHO_PAGINA)
                resposta = obter(BASE + '/Indicator/Data?' + urlencode(params, doseq=True))
                if not isinstance(resposta, dict) or not isinstance(resposta.get('data'), list):
                    raise ValueError(f'Resposta inesperada no lote {numero}, página {pagina}.')
                if 'totalPages' not in resposta:
                    raise ValueError('Resposta sem totalPages; não é seguro concluir a paginação.')
                salvar_json(destino, resposta)
                origem = 'baixada'
            arquivos.append(destino)
            total = int(resposta['totalPages'])
            print(f'Lote {numero}/{len(lotes)} | página {pagina}/{total} '
                  f"| {len(resposta['data'])} registros | {origem}", flush=True)
            if pagina >= total:
                break
            pagina += 1

    # Duas passagens evitam carregar a coleta inteira na memória.
    colunas = {}
    for arquivo in arquivos:
        for registro in json.loads(arquivo.read_text(encoding='utf-8'))['data']:
            for chave in achatar(registro):
                colunas.setdefault(chave, None)
    pasta_csv = PASTA / 'csv_por_regiao'
    pasta_csv.mkdir(exist_ok=True)
    saidas, escritores = {}, {}
    contagens = {c: 0 for c in regioes}
    vistos = set()
    duplicados = 0
    consolidado = PASTA / 'IGES_continentais_2000_em_diante.json'
    temporario = consolidado.with_suffix('.json.tmp')
    try:
        for codigo, regiao in regioes.items():
            caminho = pasta_csv / f"{codigo:03d}_{nome_arquivo(regiao['nome'])}.csv"
            saidas[codigo] = caminho.open('w', newline='', encoding='utf-8-sig')
            escritores[codigo] = csv.DictWriter(saidas[codigo], fieldnames=list(colunas))
            escritores[codigo].writeheader()
        with temporario.open('w', encoding='utf-8') as saida:
            saida.write('[')
            primeiro = True
            for arquivo in arquivos:
                registros = json.loads(arquivo.read_text(encoding='utf-8'))['data']
                for registro in registros:
                    codigo = int(registro['geoAreaCode'])
                    if codigo not in regioes:
                        raise ValueError(f'API retornou uma área não solicitada: {codigo}')
                    texto = json.dumps(registro, ensure_ascii=False, sort_keys=True)
                    assinatura = hashlib.sha256(texto.encode('utf-8')).digest()
                    if assinatura in vistos:
                        duplicados += 1
                        continue
                    vistos.add(assinatura)
                    saida.write(('' if primeiro else ',\n') + texto)
                    primeiro = False
                    escritores[codigo].writerow(achatar(registro))
                    contagens[codigo] += 1
            saida.write(']\n')
        os.replace(temporario, consolidado)
    finally:
        for f in saidas.values():
            f.close()
    salvar_json(PASTA / 'resumo_coleta.json', dict(
        registros=sum(contagens.values()), duplicados_exatos_removidos=duplicados,
        registros_por_regiao=contagens,
        concluido_em=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    print(f'\nConcluído: {sum(contagens.values()):,} registros únicos; '
          f'{duplicados:,} duplicatas exatas removidas.')
    print(f'JSON consolidado e CSVs por região em: {PASTA}')
    print('Regiões sem observações terão CSV apenas com cabeçalho.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrompido. Execute novamente para retomar as páginas salvas.')
        sys.exit(1)
    except Exception as erro:
        print(f'\nERRO: {erro}\nExecute novamente para retomar as páginas salvas.', file=sys.stderr)
        sys.exit(1)
