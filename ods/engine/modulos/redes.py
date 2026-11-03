#!/usr/bin/env python3
"""Redes ODS a partir de abas Pearson existentes. Python >= 3.10; openpyxl.
Execute: py pearson_para_cytoscape.py
Não baixa dados, interpola nem recalcula Pearson.
Cria uma cópia *_final.xlsx com rede_cytoscape e metas_cytoscape.
Preserva o XLSX de entrada e salva os CSVs com o nome da região.
"""
from __future__ import annotations
import argparse
import csv
import itertools
import json
import math
import re
import sys
import os
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

from identidade import representatives
from normas_series import resolve_api
from progresso import divergent_decision, workbook_trends, case_sheet, ADVERSE_COLUMNS

ROOT = Path(__file__).resolve().parent
# Complementos da nota UNSD 2026 e interpretações documentadas no LEIA-ME.
# Valores presentes na planilha do usuário têm precedência.
NORM_COMPLEMENTAR = {'1.1.1': -1, '1.2.1': -1, '1.3.1': 1, '1.4.1': 1, '1.5.1': -1, '1.5.3': 1, '1.a.1': 1, '1.a.2': 1, '10.1.1': 1, '10.2.1': -1, '10.4.1': 1, '10.6.1': 1, '10.7.2': 1, '10.7.3': -1, '10.7.4': -1, '10.a.1': -1, '10.b.1': 1, '10.c.1': -1, '11.1.1': -1, '11.2.1': 1, '11.5.1': -1, '11.6.2': -1, '11.a.1': 1, '11.b.1': 1, '11.b.2': 1, '12.1.1': 1, '12.2.1': -1, '12.2.2': -1, '12.3.1': -1, '12.4.1': 1, '12.4.2': -1, '12.5.1': 1, '12.6.1': 1, '12.a.1': 1, '12.b.1': 1, '12.c.1': -1, '13.1.1': -1, '13.1.2': 1, '13.2.2': -1, '13.a.1': 1, '14.1.1': -1, '14.2.1': 1, '14.3.1': 1, '14.4.1': 1, '14.5.1': 1, '14.6.1': 1, '14.a.1': 1, '14.b.1': 1, '14.c.1': 1, '15.1.1': 1, '15.1.2': 1, '15.2.1': 1, '15.3.1': -1, '15.4.1': 1, '15.4.2': 1, '15.5.1': 1, '15.6.1': 1, '15.8.1': 1, '15.9.1': 1, '15.a.1': 1, '15.b.1': 1, '16.1.1': -1, '16.1.2': -1, '16.10.1': -1, '16.10.2': 1, '16.3.2': -1, '16.5.2': -1, '16.7.1': 1, '16.8.1': 1, '16.9.1': 1, '16.a.1': 1, '17.1.1': 1, '17.1.2': 1, '17.10.1': -1, '17.11.1': -1, '17.12.1': -1, '17.13.1': 1, '17.15.1': 1, '17.17.1': 1, '17.18.1': 1, '17.18.2': 1, '17.18.3': 1, '17.19.1': 1, '17.19.2': 1, '17.2.1': 1, '17.3.1': 1, '17.3.2': 1, '17.4.1': -1, '17.6.1': 1, '17.6.2': 1, '17.7.1': 1, '17.8.1': 1, '17.9.1': 1, '2.1.1': -1, '2.1.2': -1, '2.2.1': -1, '2.2.2': -1, '2.2.3': -1, '2.2.4': 1, '2.3.1': 1, '2.4.1': 1, '2.5.1': 1, '2.5.2': -1, '2.a.1': 1, '2.a.2': 1, '2.b.1': -1, '2.c.1': -1, '3.1.1': -1, '3.2.1': -1, '3.3.1': -1, '3.3.2': -1, '3.3.3': -1, '3.3.4': -1, '3.3.5': -1, '3.4.1': -1, '3.4.2': -1, '3.5.1': 1, '3.5.2': -1, '3.6.1': -1, '3.7.1': 1, '3.7.2': -1, '3.8.1': 1, '3.8.2': -1, '3.9.2': -1, '3.9.3': -1, '3.a.1': -1, '3.b.1': 1, '3.c.1': 1, '3.d.1': 1, '4.1.1': 1, '4.1.2': 1, '4.2.1': 1, '4.2.2': 1, '4.3.1': 1, '4.4.1': 1, '4.5.1': 1, '4.6.1': 1, '4.a.1': 1, '4.b.1': 1, '4.c.1': 1, '5.1.1': 1, '5.2.1': -1, '5.3.1': -1, '5.5.1': 1, '5.5.2': 1, '5.6.1': 1, '5.b.1': 1, '5.c.1': 1, '6.1.1': 1, '6.2.1': 1, '6.3.1': 1, '6.3.2': 1, '6.4.1': 1, '6.4.2': -1, '6.5.1': 1, '6.5.2': 1, '6.6.1': 1, '6.a.1': 1, '7.1.1': 1, '7.1.2': 1, '7.2.1': 1, '7.3.1': -1, '7.a.1': 1, '7.b.1': 1, '8.1.1': 1, '8.10.1': 1, '8.10.2': 1, '8.2.1': 1, '8.3.1': -1, '8.4.1': -1, '8.4.2': -1, '8.5.1': 1, '8.5.2': -1, '8.6.1': -1, '8.7.1': -1, '8.8.1': -1, '8.8.2': -1, '8.9.1': 1, '8.9.2': 1, '8.a.1': 1, '9.1.2': 1, '9.2.1': 1, '9.2.2': 1, '9.3.1': 1, '9.3.2': 1, '9.4.1': -1, '9.5.1': 1, '9.5.2': 1, '9.a.1': 1, '9.b.1': 1, '9.c.1': 1}

def default_base(name):
    direct = ROOT / name
    return direct if direct.exists() else ROOT / 'bases' / name
EDGE_COLUMNS = ['MetaA','GoalA','MetaB','GoalB','interaction','weight']
NODE_COLUMNS = ['Meta','Goal','synergy_out','synergy_in','synergy_out_minus_in',
                'tradeoff_out','tradeoff_in','tradeoff_out_minus_in','colaboracao','negligencia','synergy_in_oposta']
TARGET_COLUMNS = ['MetaODS','Colab','Neglect']
AUDIT_COLUMNS = ['IndicadorA','IndicadorB','CodigoA','CodigoB','SerieAPIA','SerieAPIB',
                 'MetaA','MetaB','Pearson','Sig','SentidoA','SentidoB','interaction',
                 'Literatura','Regra','Evidencia','FonteSentidoA','FonteSentidoB','Motivo']
AUDIT_COLUMNS += [k for k in ADVERSE_COLUMNS if k not in AUDIT_COLUMNS] + ['Admitida_literatura']
# Colunas numéricas dos CSVs auxiliares; no XLSX entram como número, não texto.
NUMERIC_COLUMNS = {'Pearson','Sig','SentidoA','SentidoB','weight','GoalA','GoalB','Goal','sentido',
                   *NODE_COLUMNS[2:], 'R2A','R2B','InclinacaoA','InclinacaoB','AnosA','AnosB','InicioA','FimA','InicioB','FimB'}


def text(x):
    return '' if x is None else str(x).strip()


def normalize(x):
    return ''.join(c for c in unicodedata.normalize('NFKD', text(x).lower())
                   if not unicodedata.combining(c))


def code(x):
    # Códigos ODS são identificadores textuais; nunca arredondar 8.10 para 8.1.
    return text(x)


def numeric(x):
    if isinstance(x, bool) or x is None:
        return None
    try:
        n = float(x) if not isinstance(x,str) else float(x.strip().replace(',','.'))
        return n if math.isfinite(n) else None
    except (ValueError,TypeError):
        return None


def target_codes(x):
    if isinstance(x,(list,tuple)):
        values=x
    else:
        s=text(x)
        try:
            values=json.loads(s) if s.startswith('[') else [s]
        except json.JSONDecodeError:
            values=[s]
    found=[]
    for val in values:
        for c in re.findall(r'(?<![\d.])(?:1[0-7]|[1-9])\.(?:\d+|[a-z])(?![\w.])',text(val)):
            if c not in found:found.append(c)
    return tuple(found)


def indicator_code(x):
    # Funciona com códigos puros e com identificadores EU_001_1.1.1.
    m=re.search(r'(?<!\d)((?:1[0-7]|[1-9])\.(?:\d+|[a-z])\.\d+)(?!\d)',text(x))
    return m.group(1) if m else ''


def rows_as_dict(sheet):
    it=iter(sheet.iter_rows(values_only=True))
    header=next(it,())
    names=[text(h) for h in header]
    for row in it:
        if any(v is not None for v in row):
            yield {k:row[i] if i<len(row) else None for i,k in enumerate(names) if k}


def sheet_rows(path,sheet=None):
    w=load_workbook(path,read_only=True,data_only=True)
    try:
        yield from rows_as_dict(w[sheet] if sheet else w.worksheets[0])
    finally:
        w.close()


def write_csv(path,columns,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        out=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore',lineterminator='\n')
        out.writeheader()
        out.writerows(rows)


def target_sort_key(value):
    goal, suffix = value.split('.', 1)
    return (int(goal), 0, int(suffix)) if suffix.isdigit() else (int(goal), 1, suffix)


def write_network_sheets(path, final_path, edges, targets):
    """Preserva as outras abas e fórmulas; substitui somente as duas saídas.

    Grava primeiro em arquivo temporário na mesma pasta e só então substitui
    a cópia final. O arquivo de correlações original não é substituído.
    Feche a cópia final no Excel antes de executar novamente.
    """
    workbook = load_workbook(path, data_only=False, keep_links=True)
    temporary = None
    try:
        for name, columns, rows in [
            ('rede_cytoscape', EDGE_COLUMNS, edges),
            ('metas_cytoscape', TARGET_COLUMNS, targets),
        ]:
            position = workbook.sheetnames.index(name) if name in workbook.sheetnames else len(workbook.sheetnames)
            if name in workbook.sheetnames:
                del workbook[name]
            sheet = workbook.create_sheet(name, position)
            sheet.append(columns)
            for record in rows:
                sheet.append([record.get(column) for column in columns])
            for cell in sheet[1]:
                cell.font = Font(bold=True, color='FFFFFF')
                cell.fill = PatternFill('solid', fgColor='17365D')
            sheet.freeze_panes = 'A2'
            sheet.auto_filter.ref = sheet.dimensions
            for cells in sheet.iter_cols():
                sheet.column_dimensions[cells[0].column_letter].width = max(16, len(str(cells[0].value)) + 2)
                for cell in cells[1:]:
                    if cells[0].value in ('MetaA', 'MetaB', 'MetaODS'):
                        cell.number_format = '@'
                    elif isinstance(cell.value, (int, float)) and cells[0].value not in ('GoalA', 'GoalB'):
                        cell.number_format = '0.###############'
        with tempfile.NamedTemporaryFile(prefix='.' + final_path.stem + '_', suffix='.xlsx',
                                         dir=final_path.parent, delete=False) as handle:
            temporary = Path(handle.name)
        workbook.save(temporary)
        workbook.close()
        os.replace(temporary, final_path)
    finally:
        workbook.close()
        if temporary is not None and temporary.exists():
            temporary.unlink()


ONE_SIDE_CLEAR='one side clear'
SINGLE_CLEAR='single side clear'
SINGLE_UNCLEAR='single side unclear'
UNCLEAR='unclear'
DOUBLE_CLEAR='double sides clear'


def literature_label(x):
    # 'one side unclear' (grafia usada nas regras) equivale a 'single side unclear' no JRC.
    label=' '.join(normalize(x).split())
    return {'one side unclear':SINGLE_UNCLEAR,'single sides clear':SINGLE_CLEAR}.get(label,label)


class Literature:
    """Linhas dirigidas do IGES e do JRC e a regra de manutenção por sentido.

    Uma linha em qualquer sentido faz o par "constar" na fonte, qualquer que
    seja o rótulo. O sentido A→B é excluído somente nos casos abaixo, em que
    "oposto" é a linha B→A da fonte:
      0.0  par ausente do IGES e do JRC;
      0.1  só no IGES, com B→A 'one side clear'; ou só no JRC, com B→A
           'single side clear' ou 'single side unclear';
      1.1  IGES B→A 'one side clear' e JRC B→A 'single side clear';
      1.2  IGES B→A 'one side clear' e JRC B→A 'single side unclear';
      2    IGES B→A 'one side clear' e JRC 'unclear'.
    Exceção: se o JRC marca o próprio sentido A→B como 'single side clear' ou
    'double sides clear', A→B nunca é excluído.
    Nos demais casos o sentido é mantido. Como cada sentido do par é avaliado
    separadamente, um par sem exclusão entra nas duas direções, com a mesma
    interaction e o mesmo weight.
    'one side clear' vem de DoubleSided.IGES (linha sem o inverso no IGES);
    sem essa coluna, é deduzido da ausência da linha inversa.
    """
    def __init__(self):
        self.iges={};self.jrc={}

    def __len__(self):
        return len({frozenset(k) for k in (*self.iges,*self.jrc)})

    def iges_opposite_one_side(self,a,b):
        row=self.iges.get((b,a))
        if row is None:return False
        if row['one_side']:return row['one_side']==ONE_SIDE_CLEAR
        return (a,b) not in self.iges

    def decide(self,a,b):
        in_iges=(a,b) in self.iges or (b,a) in self.iges
        in_jrc=(a,b) in self.jrc or (b,a) in self.jrc
        iges_opp=self.iges_opposite_one_side(a,b)
        jrc_opp=self.jrc.get((b,a))
        jrc_unclear=UNCLEAR in (self.jrc.get((a,b)),jrc_opp)
        sources='|'.join(s for s,ok in (('IGES',in_iges),('JRC',in_jrc)) if ok)
        if not in_iges and not in_jrc:
            return False,'0.0',sources,'ausente do IGES e do JRC'
        if self.jrc.get((a,b)) in (SINGLE_CLEAR,DOUBLE_CLEAR):
            # JRC claro no próprio sentido A→B: nunca exclui.
            return True,'mantida',sources,'mantida'
        if in_iges and not in_jrc and iges_opp:
            return False,'0.1',sources,"só no IGES, 'one side clear' no sentido oposto"
        if in_jrc and not in_iges and jrc_opp in (SINGLE_CLEAR,SINGLE_UNCLEAR):
            return False,'0.1',sources,f"só no JRC, '{jrc_opp}' no sentido oposto"
        if iges_opp and jrc_opp==SINGLE_CLEAR:
            return False,'1.1',sources,"IGES 'one side clear' e JRC 'single side clear' no sentido oposto"
        if iges_opp and jrc_opp==SINGLE_UNCLEAR:
            return False,'1.2',sources,"IGES 'one side clear' e JRC 'single side unclear' no sentido oposto"
        if iges_opp and jrc_unclear:
            return False,'2',sources,"IGES 'one side clear' no sentido oposto e JRC 'unclear'"
        return True,'mantida',sources,'mantida'

    def evidence(self,a,b):
        def lab(table,key,extra=False):
            row=table.get(key)
            if row is None:return '—'
            if not extra:return row
            return row['label']+(' ['+row['one_side']+']' if row['one_side'] else '')
        return (f'IGES A→B: {lab(self.iges,(a,b),True)}; IGES B→A: {lab(self.iges,(b,a),True)}; '
                f'JRC A→B: {lab(self.jrc,(a,b))}; JRC B→A: {lab(self.jrc,(b,a))}')


def load_directions(iges,jrc):
    """Lê IGES e JRC como linhas dirigidas (MetaA→MetaB), sem filtrar rótulos.
    Linhas do IGES com Decisao_IGES diferente de Manter são desconsideradas.
    """
    lit=Literature()
    counts=Counter()
    for path,source,field,ca,cb in [(iges,'IGES','Literatura','Edge.MetaA','Edge.MetaB'),
                                   (jrc,'JRC','Edge.DirectionFinal','MetaA','MetaB')]:
        for r in sheet_rows(path):
            if field not in r or ca not in r or cb not in r:
                raise ValueError(f'{path.name}: colunas esperadas ausentes ({field}, {ca}, {cb}).')
            a,b=code(r[ca]),code(r[cb]);label=literature_label(r[field])
            if not a or not b:continue
            if source=='IGES' and normalize(r.get('Decisao_IGES')) not in ('','manter'):
                counts[source+':decisao_excluida']+=1;continue
            if not target_codes(a) or not target_codes(b):
                raise ValueError(f'Meta inválida em {path.name}: {a}, {b}')
            table=lit.iges if source=='IGES' else lit.jrc
            if (a,b) in table:
                raise ValueError(f'{path.name}: linha duplicada {a}→{b}.')
            if source=='IGES':
                table[a,b]={'label':label,'one_side':literature_label(r.get('DoubleSided.IGES'))}
            else:
                table[a,b]=label
            counts[source+':'+label]+=1
    return lit,dict(counts)


@dataclass(frozen=True)
class Series:
    id: str
    indicator: str
    api: str
    description: str
    dimensions: str
    targets: tuple[str,...]
    unit: str = ''


class Normativity:
    def __init__(self,path,overrides=None):
        self.by_indicator=defaultdict(list)
        for r in sheet_rows(path):
            i=code(r.get('ODS.Indicador.Code'));s=numeric(r.get('Serie.SentidoAlvo'))
            if i and s in (-1,1):self.by_indicator[i].append((int(s),r))
        self.rules=[]
        if overrides and overrides.exists():
            with overrides.open(encoding='utf-8-sig',newline='') as f:
                for n,r in enumerate(csv.DictReader(f),2):
                    if not any(text(v) for v in r.values()):continue
                    s=numeric(r.get('sentido'))
                    if s not in (-1,1):raise ValueError(f'{overrides.name}, linha {n}: sentido deve ser +1 ou -1.')
                    if not any(text(r.get(k)) for k in ('series_id','api_series','indicador','descricao_regex','dimensoes_regex')):
                        raise ValueError(f'{overrides.name}, linha {n}: regra sem seletor.')
                    for k in ('descricao_regex','dimensoes_regex'):
                        if text(r.get(k)):re.compile(r[k],re.I)
                    self.rules.append((r,int(s)))

    def resolve(self,s):
        # Regra explícita sempre tem precedência; seletores da mesma linha são AND.
        matches=[]
        for r,d in self.rules:
            if any(text(r.get(k)) and text(r[k])!=val for k,val in
                   [('series_id',s.id),('api_series',s.api),('indicador',s.indicator)]):continue
            if any(text(r.get(k)) and not re.search(r[k],val,re.I) for k,val in
                   [('descricao_regex',s.description),('dimensoes_regex',s.dimensions)]):continue
            matches.append(d)
        if matches:
            if len(set(matches))!=1:return None,'regras específicas conflitantes'
            return matches[0],'sentidos_series.csv'
        if s.api:
            return resolve_api(s.api)
        i=s.indicator;desc=normalize(s.description+' '+s.api)
        # Medidas heterogêneas: resolver pela série, nunca pelo sentido da meta.
        if i=='6.2.1':
            if any(x in desc for x in ('open defecation','defecacao')):return -1,'série: defecação a céu aberto (UNSD)'
            if any(x in desc for x in ('sanitation','handwashing','saneamento')):return 1,'série: saneamento/higiene (UNSD)'
            return None,'6.2.1: série de saneamento/higiene não identificada'
        if i=='12.4.2':
            if any(x in desc for x in ('collected','collection','recycled','recycling','treated','coleta','tratado')):
                return 1,'série: coleta/tratamento de resíduos'
            if any(x in desc for x in ('generated','generation','gerado','geracao')):
                return -1,'série: geração de resíduos'
            return None,'12.4.2: distinguir geração de coleta/tratamento'
        if i=='10.5.1':
            if any(x in desc for x in ('non-performing','nonperforming','non performing')):
                return -1,'série: créditos inadimplentes (UNSD)'
            if any(x in desc for x in ('regulatory tier','capital to risk','return on assets')):
                return 1,'série: capital regulatório/retorno sobre ativos (UNSD)'
            return None,'10.5.1: medida financeira não identificada'
        if i in ('5.4.1','16.6.1'):
            return None,i+': exige regra específica em sentidos_series.csv'
        # Proxies conhecidos que invertem a direção da série oficial.
        if i=='15.3.1' and ('forest area' in desc or 'area florestal' in desc):
            return 1,'proxy: área florestal, não proporção de terra degradada'
        if i=='14.4.1' and any(x in desc for x in ('total fisheries production','total fish production')):
            return None,'14.4.1: produção pesqueira não equivale a sustentabilidade; definir regra da proxy'
        if i=='2.4.1' and ('fertilizer' in desc or 'fertilizante' in desc):
            return None,'2.4.1: consumo de fertilizante não equivale ao escore de sustentabilidade'
        values=self.by_indicator.get(i,[])
        if not values and i in NORM_COMPLEMENTAR:
            return NORM_COMPLEMENTAR[i],'complemento normativo por indicador (UNSD/interpretação documentada)'
        signs={a for a,_ in values}
        if len(signs)==1:
            return next(iter(signs)),'normatividade.xlsx: indicador '+i
        if not signs:return None,'indicador sem sentido definido: '+(i or s.id)
        return None,'indicador com sentidos distintos; definir regra para a série '+s.id


def metadata(workbook):
    result={}
    if 'Series' not in workbook.sheetnames:return result
    for r in rows_as_dict(workbook['Series']):
        sid=text(r.get('series_id'))
        if not sid:continue
        result[sid]=Series(sid,indicator_code(r.get('indicator_used') or r.get('indicator') or sid),
            text(r.get('api_series') or r.get('series')),text(r.get('description')),
            text(r.get('dimensions')),target_codes(r.get('targets') or r.get('target')),text(r.get('unit')))
    return result


def identity(id,meta,rawtargets):
    if id in meta:
        s=meta[id]
        return Series(s.id,s.indicator,s.api,s.description,s.dimensions,s.targets or target_codes(rawtargets),s.unit)
    i=indicator_code(id)
    targets=target_codes(rawtargets)
    if not targets and i:targets=(i.rsplit('.',1)[0],)
    return Series(id,i,'','','',targets)


def classify(r,da,db):
    value=r*da*db
    return 'synergy' if value>0 else 'trade-off' if value<0 else None


def node_metrics(nodes,edges,target_directions=None):
    target_directions=target_directions or {}
    sums={n:{'synergy_out':0.0,'synergy_in':0.0,'tradeoff_out':0.0,'tradeoff_in':0.0,'synergy_in_oposta':0.0} for n in nodes}
    for e in edges:
        typ='synergy' if e['interaction']=='synergy' else 'tradeoff'
        for n in (e['MetaA'],e['MetaB']):
            sums.setdefault(n,{'synergy_out':0.0,'synergy_in':0.0,'tradeoff_out':0.0,'tradeoff_in':0.0,'synergy_in_oposta':0.0})
        w=abs(e['weight'])
        sums[e['MetaA']][typ+'_out']+=w;sums[e['MetaB']][typ+'_in']+=w
        if typ=='synergy' and target_directions.get(e['MetaA'])=='oposta':sums[e['MetaB']]['synergy_in_oposta']+=w
    rows={}
    for n,v in sums.items():
        rows[n]={'Meta':n,'Goal':int(n.split('.')[0]),**v,
            'synergy_out_minus_in':v['synergy_out']-v['synergy_in'],
            'tradeoff_out_minus_in':v['tradeoff_out']-v['tradeoff_in'],
            'colaboracao':v['synergy_out']-v['tradeoff_out'],
            'negligencia':v['tradeoff_in']+v['synergy_in_oposta']}
    return rows


def process_rows(rows,meta,norm,directions,alpha=0.1,trends=None):
    identity_rows=[dict(series_id=s.id,targets='; '.join(s.targets),indicator_used=s.indicator,api_series=s.api,dimensions=s.dimensions,unit=s.unit) for s in meta.values()]
    canonical, legend = representatives(identity_rows)
    single_targets={item['canonical_series_id']:item['representative'] for item in legend}
    meta={sid:replace(s,targets=(single_targets[sid],)) if sid in single_targets else s for sid,s in meta.items()}
    edges=[];audit=[];nodes={t for s in meta.values() if canonical.get(s.id,s.id)==s.id for t in s.targets};seen={};counts=Counter()
    for rownum,row in enumerate(rows,2):
        counts['linhas_pearson']+=1
        ida,idb=text(row.get('IndicadorA')),text(row.get('IndicadorB'))
        if not ida or not idb:raise ValueError(f'Pearson, linha {rownum}: identificadores ausentes.')
        sa=identity(ida,meta,row.get('MetaA'));sb=identity(idb,meta,row.get('MetaB'))
        # Não introduz nós omitidos na consolidação.
        for item in (sa,sb):
            if canonical.get(item.id,item.id)==item.id:nodes.update(item.targets)
        r,p=numeric(row.get('Pearson')),numeric(row.get('Sig'))
        detail={'IndicadorA':ida,'IndicadorB':idb,'CodigoA':sa.indicator,'CodigoB':sb.indicator,
                'SerieAPIA':sa.api,'SerieAPIB':sb.api,'Pearson':r,'Sig':p}
        reason=''
        if r is None or p is None or not -1<=r<=1 or not 0<=p<=1:reason='r ou p inválido'
        elif canonical.get(ida,ida)!=ida or canonical.get(idb,idb)!=idb:reason='cópia de medida excluída: usar apenas representante'
        elif ida==idb:reason='mesma série'
        else:
            key=tuple(sorted((ida,idb)))
            if key in seen:
                if not (math.isclose(r,seen[key][0],abs_tol=1e-10) and math.isclose(p,seen[key][1],abs_tol=1e-10)):
                    raise ValueError(f'Pearson duplicado conflitante: {ida}, {idb}.')
                reason='par de séries duplicado (inclui inverso)'
            else:seen[key]=(r,p)
        if not reason and p>alpha:reason='p > '+str(alpha)
        if not reason and r==0:reason='correlação zero'
        if not reason and (not sa.targets or not sb.targets):reason='meta não identificada'
        da,fa=norm.resolve(sa);db,fb=norm.resolve(sb)
        detail.update(SentidoA=da,SentidoB=db,FonteSentidoA=fa,FonteSentidoB=fb)
        if not reason and (da is None or db is None):reason='normatividade pendente: '+('; '.join(x for d,x in [(da,fa),(db,fb)] if d is None))
        if reason:
            counts[reason.split(':')[0]]+=1;audit.append({**detail,'Motivo':reason});continue
        original_interaction=classify(r,da,db)
        ta=(trends or {}).get(ida,{})
        tb=(trends or {}).get(idb,{})
        action,interaction,adverse_reason=divergent_decision(original_interaction,ta,tb,r)
        temporal={}
        for end,trend in [('A',ta),('B',tb)]:
            for field,label in [('direcao_progresso','Direcao'),('inclinacao','Inclinacao'),('r2_tempo','R2'),('n_anos','Anos'),('ano_inicial','Inicio'),('ano_final','Fim')]:temporal[label+end]=trend.get(field)
        detail.update(temporal,Interacao_original=original_interaction,Interacao_final=interaction,Acao_adversa=action,Motivo_adverso=adverse_reason,weight=abs(r))
        # Uma contribuição por par de séries e par dirigido de metas.
        # Múltiplos indicadores da mesma meta permanecem como arestas paralelas.
        projected=set()
        for ta,tb in itertools.product(sa.targets,sb.targets):
            if ta==tb:
                audit.append({**detail,'MetaA':ta,'MetaB':tb,'Motivo':'intrameta: autorrelação de nó excluída'});continue
            for a,b in ((ta,tb),(tb,ta)):
                if (a,b) in projected:continue
                projected.add((a,b))
                reverse=(a,b)==(tb,ta)
                oriented=detail if not reverse else {**detail,'IndicadorA':idb,'IndicadorB':ida,
                    'CodigoA':sb.indicator,'CodigoB':sa.indicator,'SerieAPIA':sb.api,'SerieAPIB':sa.api,
                    'SentidoA':db,'SentidoB':da,'FonteSentidoA':fb,'FonteSentidoB':fa,
                    **{label+end:temporal[label+('B' if end=='A' else 'A')] for label in ('Direcao','Inclinacao','R2','Anos','Inicio','Fim') for end in ('A','B')}}
                keep,rule,sources,why=directions.decide(a,b)
                counts['sentido_'+('mantido' if keep else 'excluido_regra_'+rule)]+=1
                if keep and action in ('excluida','reclassificada'):counts['adversos_'+action]+=1
                final_keep=keep and action!='excluida'
                audit.append({**oriented,'MetaA':a,'MetaB':b,'interaction':interaction, 'Admitida_literatura':keep,
                              'Literatura':sources,'Regra':rule,'Evidencia':directions.evidence(a,b),
                              'Motivo':('excluída: '+adverse_reason) if keep and action=='excluida' else 'mantida' if keep else 'excluída (regra '+rule+'): '+why})
                if final_keep:
                    # Tipo final após filtro temporal; Pearson original intacto e weight = |r|.
                    edges.append({'MetaA':a,'GoalA':int(a.split('.')[0]),'MetaB':b,'GoalB':int(b.split('.')[0]),
                        'interaction':interaction,'weight':abs(r)})
    target_directions={t:(trends or {}).get(sid,{}).get('direcao_progresso','indeterminada') for sid,s in meta.items() for t in s.targets}
    metrics=node_metrics(nodes,edges,target_directions)
    counts['arestas_finais']=len(edges);counts['metas']=len(metrics)
    counts['pares_dirigidos_metas']=len({(e['MetaA'],e['MetaB']) for e in edges})
    counts['pendencias_normatividade']=sum(1 for x in audit if x['Motivo'].startswith('normatividade pendente'))
    return edges,list(metrics.values()),audit,dict(counts)


def process_file(path,dest,norm,directions,alpha):
    w=load_workbook(path,read_only=True,data_only=True)
    try:
        if 'Pearson' not in w.sheetnames:return None
        pearson=list(rows_as_dict(w['Pearson']))
        if pearson and not {'IndicadorA','IndicadorB','Pearson','Sig'}<=set(pearson[0]):
            raise ValueError('Aba Pearson deve conter IndicadorA, IndicadorB, Pearson, Sig.')
        meta=metadata(w)
        trends=workbook_trends(w,meta,norm)
        result=process_rows(pearson,meta,norm,directions,alpha,trends)
    finally:w.close()
    edges,nodes,audit,counts=result
    nodes = sorted(nodes, key=lambda x: target_sort_key(x['Meta']))
    # Ausência de arestas define isolamento. Saldos iguais a zero também podem
    # ocorrer em metas conectadas, por compensação de contribuições.
    connected = {e[end] for e in edges for end in ('MetaA', 'MetaB')}
    targets = [{'MetaODS': n['Meta'], 'Colab': n['colaboracao'], 'Neglect': n['negligencia']}
               for n in nodes if n['Meta'] in connected]
    if len({n['MetaODS'] for n in targets}) != len(targets):
        raise ValueError('Metas duplicadas na tabela de atributos.')
    # A cópia final recebe as duas abas e conserva as abas da entrada.
    final_path = path.with_name(path.stem + '_final.xlsx')
    write_network_sheets(path, final_path, edges, targets)
    audit_book=load_workbook(final_path)
    case_sheet(audit_book,[r for r in audit if r.get('Admitida_literatura') and r.get('Acao_adversa') in ('excluida','reclassificada')])
    if 'Normatividade_series' in audit_book.sheetnames:del audit_book['Normatividade_series']
    sheet=audit_book.create_sheet('Normatividade_series')
    sheet.append(['series_id','Metas','Indicador_real','Serie_API','Descricao','Dimensoes','Sentido','Fundamento','Sentido_base_legada','Diverge_da_base'])
    for sid,s in meta.items():
        sign,source=norm.resolve(s)
        legacy=sorted({v for v,_ in norm.by_indicator.get(s.indicator,[])})
        sheet.append([sid,'; '.join(s.targets),s.indicator,s.api,s.description,s.dimensions,sign,source,'; '.join(str(v) for v in legacy),bool(legacy and sign not in legacy)])
    sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
    for col in ('E','F','H'):sheet.column_dimensions[col].width=65
    audit_book.save(final_path);audit_book.close()
    region = re.sub(r'_correlacoes$', '', path.stem, flags=re.I)
    edge_filename = region + '_rede_cytoscape.csv'
    target_filename = region + '_metas_cytoscape.csv'
    counts['metas_cytoscape'] = len(targets)
    dest.mkdir(parents=True,exist_ok=True)
    # Arquivos em UTF-8 com BOM, vírgula como delimitador e ponto decimal.
    write_csv(dest/edge_filename,EDGE_COLUMNS,edges)
    write_csv(dest/'graus_por_meta.csv',NODE_COLUMNS,nodes)
    write_csv(dest/target_filename,TARGET_COLUMNS,targets)
    # Prefixos evitam colisões quando várias regiões compartilham uma pasta.
    write_csv(path.with_name(edge_filename),EDGE_COLUMNS,edges)
    write_csv(path.with_name(target_filename),TARGET_COLUMNS,targets)
    write_csv(dest/'auditoria_arestas.csv',AUDIT_COLUMNS,audit)
    pending={}
    for r in audit:
        if not r['Motivo'].startswith('normatividade pendente'):continue
        for end in ('A','B'):
            if r.get('Sentido'+end) is None:
                sid=r['Indicador'+end]
                pending[sid]={'series_id':sid,'api_series':r['SerieAPI'+end],'indicador':r['Codigo'+end],
                              'sentido':'','motivo':r['FonteSentido'+end]}
    write_csv(dest/'pendencias_normatividade.csv',['series_id','api_series','indicador','sentido','motivo'],pending.values())
    (dest/'resumo.json').write_text(json.dumps({'arquivo':str(path),'arquivo_final':str(final_path),'alpha':alpha,**counts},ensure_ascii=False,indent=2),encoding='utf-8')
    return counts


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entrada',type=Path,default=ROOT,help='Pasta com *_correlacoes.xlsx ou um XLSX individual.')
    p.add_argument('--saida',type=Path,default=ROOT/'redes_finais')
    p.add_argument('--iges',type=Path,default=default_base('iges_decisao.xlsx'))
    p.add_argument('--jrc',type=Path,default=default_base('jrc_decisao.xlsx'))
    p.add_argument('--normatividade',type=Path,default=default_base('normatividade.xlsx'))
    p.add_argument('--sentidos',type=Path,default=ROOT/'sentidos_series.csv')
    p.add_argument('--alpha',type=float,default=0.1)
    args=p.parse_args(argv)
    if not 0<=args.alpha<=1:p.error('--alpha deve estar entre 0 e 1.')
    for path in (args.iges,args.jrc,args.normatividade):
        if not path.is_file():p.error(f'Arquivo não encontrado: {path}')
    directions,lit_counts=load_directions(args.iges,args.jrc)
    norm=Normativity(args.normatividade,args.sentidos)
    candidates=[args.entrada] if args.entrada.is_file() else sorted(args.entrada.glob('*_correlacoes.xlsx'))
    candidates=[x for x in candidates if not x.name.startswith('~$') and
                x.resolve() not in {args.iges.resolve(),args.jrc.resolve(),args.normatividade.resolve()} and
                args.saida.resolve() not in x.resolve().parents]
    if not candidates:p.error('Nenhuma planilha XLSX encontrada na entrada.')
    args.saida.mkdir(parents=True,exist_ok=True)
    processed=[];failures=[];used={}
    for path in candidates:
        stem=re.sub(r'_correlacoes$','',path.stem,flags=re.I)
        # Não sobrescrever resultados de outra entrada com o mesmo nome.
        destination=args.saida/stem
        try:
            w=load_workbook(path,read_only=True,data_only=True)
            try:has='Pearson' in w.sheetnames
            finally:w.close()
            if not has:continue
            if stem in used:raise ValueError(f'Duas entradas com a mesma região: {used[stem]} e {path}. Deixe apenas uma versão na pasta de entrada.')
            used[stem]=str(path)
            print(f'Processando {path.name}...',flush=True)
            c=process_file(path,destination,norm,directions,args.alpha)
            processed.append({'arquivo':str(path),**c})
            print(f"  {c['arestas_finais']} arestas; {c['metas']} metas; {c['pendencias_normatividade']} pares com normatividade pendente.",flush=True)
            print(f'  Criado: {path.stem}_final.xlsx; {c["metas_cytoscape"]} metas conectadas. CSVs com prefixo da região salvos na mesma pasta.',flush=True)
        except Exception as e:
            failures.append({'arquivo':str(path),'erro':str(e)})
            print('  ERRO:',e,flush=True)
    summary={'processadas':processed,'falhas':failures,'literatura':lit_counts,
             'pares_literatura_IGES_JRC':len(directions),
             'politica_multiplos_indicadores':'arestas paralelas; soma de |r|, sem média',
             'weight':'|r| (módulo do Pearson); interaction pelo sinal de r × sentidos normativos'}
    (args.saida/'resumo_geral.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Concluído: {len(processed)} planilhas. Saída: {args.saida.resolve()}')
    if not processed:print('Nenhuma aba Pearson foi encontrada. Use as cópias produzidas pelo código de Pearson.')
    return 1 if failures or not processed else 0


if __name__=='__main__':
    sys.exit(main())
