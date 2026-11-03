#!/usr/bin/env python3
'Build SDG networks from existing Pearson sheets using IGES/JRC directed evidence. Preserve input workbooks and export final workbooks and region-prefixed CSVs.'
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

from identity import representatives
from series_directionality import resolve_api
from progress import divergent_decision, workbook_trends, case_sheet, ADVERSE_COLUMNS

ROOT = Path(__file__).resolve().parent
# UNSD 2026 supplements and interpretations documented in the README.
# User workbook values take precedence.
ADDITIONAL_DIRECTIONALITY = {'1.1.1': -1, '1.2.1': -1, '1.3.1': 1, '1.4.1': 1, '1.5.1': -1, '1.5.3': 1, '1.a.1': 1, '1.a.2': 1, '10.1.1': 1, '10.2.1': -1, '10.4.1': 1, '10.6.1': 1, '10.7.2': 1, '10.7.3': -1, '10.7.4': -1, '10.a.1': -1, '10.b.1': 1, '10.c.1': -1, '11.1.1': -1, '11.2.1': 1, '11.5.1': -1, '11.6.2': -1, '11.a.1': 1, '11.b.1': 1, '11.b.2': 1, '12.1.1': 1, '12.2.1': -1, '12.2.2': -1, '12.3.1': -1, '12.4.1': 1, '12.4.2': -1, '12.5.1': 1, '12.6.1': 1, '12.a.1': 1, '12.b.1': 1, '12.c.1': -1, '13.1.1': -1, '13.1.2': 1, '13.2.2': -1, '13.a.1': 1, '14.1.1': -1, '14.2.1': 1, '14.3.1': 1, '14.4.1': 1, '14.5.1': 1, '14.6.1': 1, '14.a.1': 1, '14.b.1': 1, '14.c.1': 1, '15.1.1': 1, '15.1.2': 1, '15.2.1': 1, '15.3.1': -1, '15.4.1': 1, '15.4.2': 1, '15.5.1': 1, '15.6.1': 1, '15.8.1': 1, '15.9.1': 1, '15.a.1': 1, '15.b.1': 1, '16.1.1': -1, '16.1.2': -1, '16.10.1': -1, '16.10.2': 1, '16.3.2': -1, '16.5.2': -1, '16.7.1': 1, '16.8.1': 1, '16.9.1': 1, '16.a.1': 1, '17.1.1': 1, '17.1.2': 1, '17.10.1': -1, '17.11.1': -1, '17.12.1': -1, '17.13.1': 1, '17.15.1': 1, '17.17.1': 1, '17.18.1': 1, '17.18.2': 1, '17.18.3': 1, '17.19.1': 1, '17.19.2': 1, '17.2.1': 1, '17.3.1': 1, '17.3.2': 1, '17.4.1': -1, '17.6.1': 1, '17.6.2': 1, '17.7.1': 1, '17.8.1': 1, '17.9.1': 1, '2.1.1': -1, '2.1.2': -1, '2.2.1': -1, '2.2.2': -1, '2.2.3': -1, '2.2.4': 1, '2.3.1': 1, '2.4.1': 1, '2.5.1': 1, '2.5.2': -1, '2.a.1': 1, '2.a.2': 1, '2.b.1': -1, '2.c.1': -1, '3.1.1': -1, '3.2.1': -1, '3.3.1': -1, '3.3.2': -1, '3.3.3': -1, '3.3.4': -1, '3.3.5': -1, '3.4.1': -1, '3.4.2': -1, '3.5.1': 1, '3.5.2': -1, '3.6.1': -1, '3.7.1': 1, '3.7.2': -1, '3.8.1': 1, '3.8.2': -1, '3.9.2': -1, '3.9.3': -1, '3.a.1': -1, '3.b.1': 1, '3.c.1': 1, '3.d.1': 1, '4.1.1': 1, '4.1.2': 1, '4.2.1': 1, '4.2.2': 1, '4.3.1': 1, '4.4.1': 1, '4.5.1': 1, '4.6.1': 1, '4.a.1': 1, '4.b.1': 1, '4.c.1': 1, '5.1.1': 1, '5.2.1': -1, '5.3.1': -1, '5.5.1': 1, '5.5.2': 1, '5.6.1': 1, '5.b.1': 1, '5.c.1': 1, '6.1.1': 1, '6.2.1': 1, '6.3.1': 1, '6.3.2': 1, '6.4.1': 1, '6.4.2': -1, '6.5.1': 1, '6.5.2': 1, '6.6.1': 1, '6.a.1': 1, '7.1.1': 1, '7.1.2': 1, '7.2.1': 1, '7.3.1': -1, '7.a.1': 1, '7.b.1': 1, '8.1.1': 1, '8.10.1': 1, '8.10.2': 1, '8.2.1': 1, '8.3.1': -1, '8.4.1': -1, '8.4.2': -1, '8.5.1': 1, '8.5.2': -1, '8.6.1': -1, '8.7.1': -1, '8.8.1': -1, '8.8.2': -1, '8.9.1': 1, '8.9.2': 1, '8.a.1': 1, '9.1.2': 1, '9.2.1': 1, '9.2.2': 1, '9.3.1': 1, '9.3.2': 1, '9.4.1': -1, '9.5.1': 1, '9.5.2': 1, '9.a.1': 1, '9.b.1': 1, '9.c.1': 1}

def default_base(name):
    direct = ROOT / name
    return direct if direct.exists() else ROOT / 'bases' / name
EDGE_COLUMNS = ['TargetA','GoalA','TargetB','GoalB','interaction','weight']
NODE_COLUMNS = ['Target','Goal','synergy_out','synergy_in','synergy_out_minus_in',
                'tradeoff_out','tradeoff_in','tradeoff_out_minus_in','collaboration','neglect','synergy_in_backward']
TARGET_COLUMNS = ['TargetCode','Colab','Neglect']
AUDIT_COLUMNS = ['IndicatorA','IndicatorB','CodeA','CodeB','API_series_A','API_series_B',
                 'TargetA','TargetB','Pearson','Sig','DesiredDirectionA','DesiredDirectionB','interaction',
                 'Literature','Rule','Evidence','DirectionalitySourceA','DirectionalitySourceB','Reason']
AUDIT_COLUMNS += [k for k in ADVERSE_COLUMNS if k not in AUDIT_COLUMNS] + ['Literature_supported']
# Numeric columns in auxiliary CSVs become numbers in XLSX.
NUMERIC_COLUMNS = {'Pearson','Sig','DesiredDirectionA','DesiredDirectionB','weight','GoalA','GoalB','Goal','desired_direction',
                   *NODE_COLUMNS[2:], 'R2A','R2B','SlopeA','SlopeB','YearsA','YearsB','StartA','EndA','StartB','EndB'}


def text(x):
    return '' if x is None else str(x).strip()


def normalize(x):
    return ''.join(c for c in unicodedata.normalize('NFKD', text(x).lower())
                   if not unicodedata.combining(c))


def code(x):
    # SDG codes are textual identifiers; never round 8.10 to 8.1.
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
        for c in re.findall('(?<![\\d.])(?:1[0-7]|[1-9])\\.(?:\\d+|[a-z])(?![\\w.])',text(val)):
            if c not in found:found.append(c)
    return tuple(found)


def indicator_code(x):
    # Support bare codes and identifiers such as EU_001_1.1.1.
    m=re.search('(?<!\\d)((?:1[0-7]|[1-9])\\.(?:\\d+|[a-z])\\.\\d+)(?!\\d)',text(x))
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
        out=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore',lineterminator="""
""")
        out.writeheader()
        out.writerows(rows)


def target_sort_key(value):
    goal, suffix = value.split('.', 1)
    return (int(goal), 0, int(suffix)) if suffix.isdigit() else (int(goal), 1, suffix)


def write_network_sheets(path, final_path, edges, targets):
    'Preserve other sheets and formulas; write the final copy atomically through a temporary file in the same folder.'
    workbook = load_workbook(path, data_only=False, keep_links=True)
    temporary = None
    try:
        for name, columns, rows in [
            ('cytoscape_edges', EDGE_COLUMNS, edges),
            ('cytoscape_nodes', TARGET_COLUMNS, targets),
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
                    if cells[0].value in ('TargetA', 'TargetB', 'TargetCode'):
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
    # In source rules, 'one side unclear' corresponds to JRC 'single side unclear'.
    label=' '.join(normalize(x).split())
    return {'one side unclear':SINGLE_UNCLEAR,'single sides clear':SINGLE_CLEAR}.get(label,label)


class Literature:
    """Directed IGES/JRC evidence and per-direction retention rules.
Reject A→B for case 0.0 (pair absent in both sources), case 0.1 (present
only in IGES with reverse one-side-clear, or only in JRC with reverse
single-side-clear/unclear), cases 1.1/1.2 (IGES reverse one-side-clear
and JRC reverse single-side-clear/unclear), or case 2 (IGES reverse
one-side-clear with JRC unclear). JRC single-side-clear or double-sides-clear
for A→B always retains A→B. Evaluate each direction independently."""
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
            return False,'0.0',sources,'absent from both IGES and JRC'
        if self.jrc.get((a,b)) in (SINGLE_CLEAR,DOUBLE_CLEAR):
            # Clear JRC evidence for A→B always retains that direction.
            return True,'retained',sources,'retained'
        if in_iges and not in_jrc and iges_opp:
            return False,'0.1',sources,"IGES only, 'one side clear' in the reverse direction"
        if in_jrc and not in_iges and jrc_opp in (SINGLE_CLEAR,SINGLE_UNCLEAR):
            return False,'0.1',sources,f"JRC only, '{jrc_opp}' in the reverse direction"
        if iges_opp and jrc_opp==SINGLE_CLEAR:
            return False,'1.1',sources,"IGES 'one side clear' and JRC 'single side clear' in the reverse direction"
        if iges_opp and jrc_opp==SINGLE_UNCLEAR:
            return False,'1.2',sources,"IGES 'one side clear' and JRC 'single side unclear' in the reverse direction"
        if iges_opp and jrc_unclear:
            return False,'2',sources,"IGES 'one side clear' in the reverse direction and JRC 'unclear'"
        return True,'retained',sources,'retained'

    def evidence(self,a,b):
        def lab(table,key,extra=False):
            row=table.get(key)
            if row is None:return '—'
            if not extra:return row
            return row['label']+(' ['+row['one_side']+']' if row['one_side'] else '')
        return (f'IGES A→B: {lab(self.iges,(a,b),True)}; IGES B→A: {lab(self.iges,(b,a),True)}; '
                f'JRC A→B: {lab(self.jrc,(a,b))}; JRC B→A: {lab(self.jrc,(b,a))}')


def load_directions(iges,jrc):
    'Read directed IGES/JRC evidence. Ignore IGES rows whose decision differs from retain.'
    lit=Literature()
    counts=Counter()
    for path,source,field,ca,cb in [(iges,'IGES','Literature','Edge.TargetA','Edge.TargetB'),
                                   (jrc,'JRC','Edge.DirectionFinal','TargetA','TargetB')]:
        for r in sheet_rows(path):
            if field not in r or ca not in r or cb not in r:
                raise ValueError(f'{path.name}: expected columns missing ({field}, {ca}, {cb}).')
            a,b=code(r[ca]),code(r[cb]);label=literature_label(r[field])
            if not a or not b:continue
            if source=='IGES' and normalize(r.get('IGES_decision')) not in ('','retain'):
                counts[source+':decisao_excluded']+=1;continue
            if not target_codes(a) or not target_codes(b):
                raise ValueError(f'Invalid target in {path.name}: {a}, {b}')
            table=lit.iges if source=='IGES' else lit.jrc
            if (a,b) in table:
                raise ValueError(f'{path.name}: duplicate row {a}→{b}.')
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
            i=code(r.get('SDG.Indicator.Code'));s=numeric(r.get('Series.DesiredDirection'))
            if i and s in (-1,1):self.by_indicator[i].append((int(s),r))
        self.rules=[]
        if overrides and overrides.exists():
            with overrides.open(encoding='utf-8-sig',newline='') as f:
                for n,r in enumerate(csv.DictReader(f),2):
                    if not any(text(v) for v in r.values()):continue
                    s=numeric(r.get('desired_direction'))
                    if s not in (-1,1):raise ValueError(f'{overrides.name}, linha {n}: desired direction must be +1 or -1.')
                    if not any(text(r.get(k)) for k in ('series_id','api_series','indicator','description_regex','dimensions_regex')):
                        raise ValueError(f'{overrides.name}, linha {n}: rule has no selector.')
                    for k in ('description_regex','dimensions_regex'):
                        if text(r.get(k)):re.compile(r[k],re.I)
                    self.rules.append((r,int(s)))

    def resolve(self,s):
        # Explicit rules take precedence; selectors on one rule are combined with AND.
        matches=[]
        for r,d in self.rules:
            if any(text(r.get(k)) and text(r[k])!=val for k,val in
                   [('series_id',s.id),('api_series',s.api),('indicator',s.indicator)]):continue
            if any(text(r.get(k)) and not re.search(r[k],val,re.I) for k,val in
                   [('description_regex',s.description),('dimensions_regex',s.dimensions)]):continue
            matches.append(d)
        if matches:
            if len(set(matches))!=1:return None,'conflicting specific rules'
            return matches[0],'series_directions.csv'
        if s.api:
            return resolve_api(s.api)
        i=s.indicator;desc=normalize(s.description+' '+s.api)
        # Resolve heterogeneous measures by series rather than target direction.
        if i=='6.2.1':
            if any(x in desc for x in ('open defecation','open_defecation')):return -1,'series: open defecation (UNSD)'
            if any(x in desc for x in ('sanitation','handwashing','sanitation')):return 1,'series: sanitation/hygiene (UNSD)'
            return None,'6.2.1: unidentified sanitation/hygiene series'
        if i=='12.4.2':
            if any(x in desc for x in ('collected','collection','recycled','recycling','treated','collection','treated')):
                return 1,'series: waste collection/treatment'
            if any(x in desc for x in ('generated','generation','generated','generation')):
                return -1,'series: waste generation'
            return None,'12.4.2: distinguish generation from collection/treatment'
        if i=='10.5.1':
            if any(x in desc for x in ('non-performing','nonperforming','non performing')):
                return -1,'series: non-performing loans (UNSD)'
            if any(x in desc for x in ('regulatory tier','capital to risk','return on assets')):
                return 1,'series: regulatory capital/return on assets (UNSD)'
            return None,'10.5.1: unidentified financial measure'
        if i in ('5.4.1','16.6.1'):
            return None,i+': requires a specific rule in series_directions.csv'
        # Known proxies that invert the official series direction.
        if i=='15.3.1' and ('forest area' in desc or 'area florestal' in desc):
            return 1,'proxy: forest area rather than proportion of degraded land'
        if i=='14.4.1' and any(x in desc for x in ('total fisheries production','total fish production')):
            return None,'14.4.1: fisheries production does not measure sustainability; define a proxy rule'
        if i=='2.4.1' and ('fertilizer' in desc or 'fertilizer' in desc):
            return None,'2.4.1: fertilizer use does not measure the sustainability score'
        values=self.by_indicator.get(i,[])
        if not values and i in ADDITIONAL_DIRECTIONALITY:
            return ADDITIONAL_DIRECTIONALITY[i],'indicator-specific directionality supplement (UNSD/documented interpretation)'
        signs={a for a,_ in values}
        if len(signs)==1:
            return next(iter(signs)),'indicator_directionality.xlsx: indicator '+i
        if not signs:return None,'indicator without a defined desired direction:'+(i or s.id)
        return None,'indicator with multiple desired directions; define a rule for series '+s.id


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


def identity(id,target,rawtargets):
    if id in target:
        s=target[id]
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
    sums={n:{'synergy_out':0.0,'synergy_in':0.0,'tradeoff_out':0.0,'tradeoff_in':0.0,'synergy_in_backward':0.0} for n in nodes}
    for e in edges:
        typ='synergy' if e['interaction']=='synergy' else 'tradeoff'
        for n in (e['TargetA'],e['TargetB']):
            sums.setdefault(n,{'synergy_out':0.0,'synergy_in':0.0,'tradeoff_out':0.0,'tradeoff_in':0.0,'synergy_in_backward':0.0})
        w=abs(e['weight'])
        sums[e['TargetA']][typ+'_out']+=w;sums[e['TargetB']][typ+'_in']+=w
        if typ=='synergy' and target_directions.get(e['TargetA'])=='backward':sums[e['TargetB']]['synergy_in_backward']+=w
    rows={}
    for n,v in sums.items():
        rows[n]={'Target':n,'Goal':int(n.split('.')[0]),**v,
            'synergy_out_minus_in':v['synergy_out']-v['synergy_in'],
            'tradeoff_out_minus_in':v['tradeoff_out']-v['tradeoff_in'],
            'collaboration':v['synergy_out']-v['tradeoff_out'],
            'neglect':v['tradeoff_in']+v['synergy_in_backward']}
    return rows


def process_rows(rows,target,norm,directions,alpha=0.1,trends=None):
    identity_rows=[dict(series_id=s.id,targets='; '.join(s.targets),indicator_used=s.indicator,api_series=s.api,dimensions=s.dimensions,unit=s.unit) for s in target.values()]
    canonical, legend = representatives(identity_rows)
    single_targets={item['canonical_series_id']:item['representative'] for item in legend}
    target={sid:replace(s,targets=(single_targets[sid],)) if sid in single_targets else s for sid,s in target.items()}
    edges=[];audit=[];nodes={t for s in target.values() if canonical.get(s.id,s.id)==s.id for t in s.targets};seen={};counts=Counter()
    for rownum,row in enumerate(rows,2):
        counts['pearson_rows']+=1
        ida,idb=text(row.get('IndicatorA')),text(row.get('IndicatorB'))
        if not ida or not idb:raise ValueError(f'Pearson, linha {rownum}: identifiers missing.')
        sa=identity(ida,target,row.get('TargetA'));sb=identity(idb,target,row.get('TargetB'))
        # Keep nodes omitted by consolidation excluded.
        for item in (sa,sb):
            if canonical.get(item.id,item.id)==item.id:nodes.update(item.targets)
        r,p=numeric(row.get('Pearson')),numeric(row.get('Sig'))
        detail={'IndicatorA':ida,'IndicatorB':idb,'CodeA':sa.indicator,'CodeB':sb.indicator,
                'API_series_A':sa.api,'API_series_B':sb.api,'Pearson':r,'Sig':p}
        reason=''
        if r is None or p is None or not -1<=r<=1 or not 0<=p<=1:reason='invalid r or p'
        elif canonical.get(ida,ida)!=ida or canonical.get(idb,idb)!=idb:reason='duplicate measure excluded: use only the representative'
        elif ida==idb:reason='same series'
        else:
            key=tuple(sorted((ida,idb)))
            if key in seen:
                if not (math.isclose(r,seen[key][0],abs_tol=1e-10) and math.isclose(p,seen[key][1],abs_tol=1e-10)):
                    raise ValueError(f'Conflicting duplicate Pearson: {ida}, {idb}.')
                reason='duplicate series pair (including reverse)'
            else:seen[key]=(r,p)
        if not reason and p>alpha:reason='p > '+str(alpha)
        if not reason and r==0:reason='zero correlation'
        if not reason and (not sa.targets or not sb.targets):reason='unidentified target'
        da,fa=norm.resolve(sa);db,fb=norm.resolve(sb)
        detail.update(DesiredDirectionA=da,DesiredDirectionB=db,DirectionalitySourceA=fa,DirectionalitySourceB=fb)
        if not reason and (da is None or db is None):reason='unresolved directionality: '+('; '.join(x for d,x in [(da,fa),(db,fb)] if d is None))
        if reason:
            counts[reason.split(':')[0]]+=1;audit.append({**detail,'Reason':reason});continue
        original_interaction=classify(r,da,db)
        ta=(trends or {}).get(ida,{})
        tb=(trends or {}).get(idb,{})
        action,interaction,adverse_reason=divergent_decision(original_interaction,ta,tb,r)
        temporal={}
        for end,trend in [('A',ta),('B',tb)]:
            for field,label in [('progress_direction','Direction'),('slope','Inclinacao'),('time_r2','R2'),('year_count','Years'),('start_year','Start'),('end_year','End')]:temporal[label+end]=trend.get(field)
        detail.update(temporal,Original_interaction=original_interaction,Final_interaction=interaction,Adverse_action=action,Adverse_reason=adverse_reason,weight=abs(r))
        # One contribution per series pair and directed target pair.
        # Multiple indicators within one target remain parallel edges.
        projected=set()
        for ta,tb in itertools.product(sa.targets,sb.targets):
            if ta==tb:
                audit.append({**detail,'TargetA':ta,'TargetB':tb,'Reason':'within-target: node self-correlation excluded'});continue
            for a,b in ((ta,tb),(tb,ta)):
                if (a,b) in projected:continue
                projected.add((a,b))
                reverse=(a,b)==(tb,ta)
                oriented=detail if not reverse else {**detail,'IndicatorA':idb,'IndicatorB':ida,
                    'CodeA':sb.indicator,'CodeB':sa.indicator,'API_series_A':sb.api,'API_series_B':sa.api,
                    'DesiredDirectionA':db,'DesiredDirectionB':da,'DirectionalitySourceA':fb,'DirectionalitySourceB':fa,
                    **{label+end:temporal[label+('B' if end=='A' else 'A')] for label in ('Direction','Inclinacao','R2','Years','Start','End') for end in ('A','B')}}
                keep,rule,sources,why=directions.decide(a,b)
                counts['desired_direction_'+('retained' if keep else 'excluded_rule_'+rule)]+=1
                if keep and action in ('excluded','reclassified'):counts['adverse_'+action]+=1
                final_keep=keep and action!='excluded'
                audit.append({**oriented,'TargetA':a,'TargetB':b,'interaction':interaction, 'Literature_supported':keep,
                              'Literature':sources,'Rule':rule,'Evidence':directions.evidence(a,b),
                              'Reason':('excluded: '+adverse_reason) if keep and action=='excluded' else 'retained' if keep else 'excluded (rule '+rule+'): '+why})
                if final_keep:
                    # Final type after temporal filtering; preserve Pearson and weight = |r|.
                    edges.append({'TargetA':a,'GoalA':int(a.split('.')[0]),'TargetB':b,'GoalB':int(b.split('.')[0]),
                        'interaction':interaction,'weight':abs(r)})
    target_directions={t:(trends or {}).get(sid,{}).get('progress_direction','undetermined') for sid,s in target.items() for t in s.targets}
    metrics=node_metrics(nodes,edges,target_directions)
    counts['final_edges']=len(edges);counts['targets']=len(metrics)
    counts['directed_target_pairs']=len({(e['TargetA'],e['TargetB']) for e in edges})
    counts['unresolved_directionality']=sum(1 for x in audit if x['Reason'].startswith('unresolved directionality'))
    return edges,list(metrics.values()),audit,dict(counts)


def process_file(path,dest,norm,directions,alpha):
    w=load_workbook(path,read_only=True,data_only=True)
    try:
        if 'Pearson' not in w.sheetnames:return None
        pearson=list(rows_as_dict(w['Pearson']))
        if pearson and not {'IndicatorA','IndicatorB','Pearson','Sig'}<=set(pearson[0]):
            raise ValueError('Pearson sheet must contain IndicatorA, IndicatorB, Pearson and Sig.')
        target=metadata(w)
        trends=workbook_trends(w,target,norm)
        result=process_rows(pearson,target,norm,directions,alpha,trends)
    finally:w.close()
    edges,nodes,audit,counts=result
    nodes = sorted(nodes, key=lambda x: target_sort_key(x['Target']))
    # No edges implies isolation. Zero balances can also occur
    # in connected targets when contributions offset one another.
    connected = {e[end] for e in edges for end in ('TargetA', 'TargetB')}
    targets = [{'TargetCode': n['Target'], 'Colab': n['collaboration'], 'Neglect': n['neglect']}
               for n in nodes if n['Target'] in connected]
    if len({n['TargetCode'] for n in targets}) != len(targets):
        raise ValueError('Duplicate targets in the attribute table.')
    # The final copy receives both sheets and preserves source sheets.
    final_path = path.with_name(path.stem + '_final.xlsx')
    write_network_sheets(path, final_path, edges, targets)
    audit_book=load_workbook(final_path)
    case_sheet(audit_book,[r for r in audit if r.get('Literature_supported') and r.get('Adverse_action') in ('excluded','reclassified')])
    if 'Series_directionality' in audit_book.sheetnames:del audit_book['Series_directionality']
    sheet=audit_book.create_sheet('Series_directionality')
    sheet.append(['series_id','Targets','Actual_indicator','API_series','Description','Dimensions','DesiredDirection','Rationale','Legacy_base_direction','Differs_from_base'])
    for sid,s in target.items():
        sign,source=norm.resolve(s)
        legacy=sorted({v for v,_ in norm.by_indicator.get(s.indicator,[])})
        sheet.append([sid,'; '.join(s.targets),s.indicator,s.api,s.description,s.dimensions,sign,source,'; '.join(str(v) for v in legacy),bool(legacy and sign not in legacy)])
    sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
    for col in ('E','F','H'):sheet.column_dimensions[col].width=65
    audit_book.save(final_path);audit_book.close()
    region = re.sub('_correlations$', '', path.stem, flags=re.I)
    edge_filename = region + '_rede_cytoscape.csv'
    target_filename = region + '_targets_cytoscape.csv'
    counts['cytoscape_nodes'] = len(targets)
    dest.mkdir(parents=True,exist_ok=True)
    # UTF-8 with BOM, comma delimiter and decimal point.
    write_csv(dest/edge_filename,EDGE_COLUMNS,edges)
    write_csv(dest/'target_degrees.csv',NODE_COLUMNS,nodes)
    write_csv(dest/target_filename,TARGET_COLUMNS,targets)
    # Prefixes avoid collisions when regions share an output folder.
    write_csv(path.with_name(edge_filename),EDGE_COLUMNS,edges)
    write_csv(path.with_name(target_filename),TARGET_COLUMNS,targets)
    write_csv(dest/'edge_audit.csv',AUDIT_COLUMNS,audit)
    pending={}
    for r in audit:
        if not r['Reason'].startswith('unresolved directionality'):continue
        for end in ('A','B'):
            if r.get('DesiredDirection'+end) is None:
                sid=r['Indicator'+end]
                pending[sid]={'series_id':sid,'api_series':r['API_series'+end],'indicator':r['Code'+end],
                              'desired_direction':'','reason':r['DirectionalitySource'+end]}
    write_csv(dest/'unresolved_directionality.csv',['series_id','api_series','indicator','desired_direction','reason'],pending.values())
    (dest/'summary.json').write_text(json.dumps({'file':str(path),'file_final':str(final_path),'alpha':alpha,**counts},ensure_ascii=False,indent=2),encoding='utf-8')
    return counts


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT,help='Folder with *_correlations.xlsx or a single XLSX file.')
    p.add_argument('--output',type=Path,default=ROOT/'final_networks')
    p.add_argument('--iges',type=Path,default=default_base('iges_decisions.xlsx'))
    p.add_argument('--jrc',type=Path,default=default_base('jrc_decisions.xlsx'))
    p.add_argument('--indicator_directionality',type=Path,default=default_base('indicator_directionality.xlsx'))
    p.add_argument('--directions',type=Path,default=ROOT/'series_directions.csv')
    p.add_argument('--alpha',type=float,default=0.1)
    args=p.parse_args(argv)
    if not 0<=args.alpha<=1:p.error('--alpha deve estar entre 0 e 1.')
    for path in (args.iges,args.jrc,args.indicator_directionality):
        if not path.is_file():p.error(f'File not found: {path}')
    directions,lit_counts=load_directions(args.iges,args.jrc)
    norm=Normativity(args.indicator_directionality,args.directions)
    candidates=[args.input] if args.input.is_file() else sorted(args.input.glob('*_correlations.xlsx'))
    candidates=[x for x in candidates if not x.name.startswith('~$') and
                x.resolve() not in {args.iges.resolve(),args.jrc.resolve(),args.indicator_directionality.resolve()} and
                args.output.resolve() not in x.resolve().parents]
    if not candidates:p.error('No XLSX workbook found in the input.')
    args.output.mkdir(parents=True,exist_ok=True)
    processed=[];failures=[];used={}
    for path in candidates:
        stem=re.sub('_correlations$','',path.stem,flags=re.I)
        # Preserve existing results from another input with the same name.
        destination=args.output/stem
        try:
            w=load_workbook(path,read_only=True,data_only=True)
            try:has='Pearson' in w.sheetnames
            finally:w.close()
            if not has:continue
            if stem in used:raise ValueError(f'Two inputs have the same region: {used[stem]} e {path}. Keep only one version in the input folder.')
            used[stem]=str(path)
            print(f'Processing {path.name}...',flush=True)
            c=process_file(path,destination,norm,directions,args.alpha)
            processed.append({'file':str(path),**c})
            print(f"  {c['final_edges']} edges; {c['targets']} targets; {c['unresolved_directionality']} pairs with unresolved directionality.",flush=True)
            print(f"  Created: {path.stem}_final.xlsx; {c['cytoscape_nodes']} connected targets. Region-prefixed CSV files saved in the same folder.",flush=True)
        except Exception as e:
            failures.append({'file':str(path),'error':str(e)})
            print('  ERROR:',e,flush=True)
    summary={'processed':processed,'failures':failures,'literature':lit_counts,
             'IGES_JRC_literature_pairs':len(directions),
             'multiple_indicators_policy':'parallel edges; sum of |r| without averaging',
             'weight':'|r| (absolute Pearson coefficient); interaction from the sign of r multiplied by desired directions'}
    (args.output/'overall_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Completed: {len(processed)} workbooks. Output: {args.output.resolve()}')
    if not processed:print('No Pearson sheet found. Use the copies produced by the Pearson code.')
    return 1 if failures or not processed else 0


if __name__=='__main__':
    sys.exit(main())
