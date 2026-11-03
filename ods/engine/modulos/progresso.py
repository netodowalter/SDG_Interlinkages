"""Tendência temporal local e leitura das arestas; não estima causalidade."""
import math
from collections import defaultdict
from openpyxl import load_workbook
from openpyxl.styles import Alignment,Font,PatternFill
from openpyxl.utils import get_column_letter
from identidade import representatives
from ambicao import ambition_for, SOURCE as AMBITION_SOURCE

def records(sheet):
    it=iter(sheet.values);headers=next(it,())
    return [dict(zip(headers,row)) for row in it if any(v is not None for v in row)]

def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def fit(points,sign):
    points=[(x,y) for x,y in points if finite(x) and finite(y)]
    result=dict(n_anos=len(points),ano_inicial=None,ano_final=None,inclinacao=None,variacao_reta=None,inclinacao_normativa=None,r_tempo=None,r2_tempo=None,direcao_progresso='indeterminada')
    if len(points)<3 or len({x for x,y in points})<3:return result
    xs,ys=zip(*points);xm=sum(xs)/len(xs);ym=sum(ys)/len(ys)
    slope=sum((x-xm)*(y-ym) for x,y in points)/sum((x-xm)**2 for x in xs)
    delta=slope*(max(xs)-min(xs))
    syy=sum((y-ym)**2 for y in ys);sxx=sum((x-xm)**2 for x in xs)
    rt=slope*math.sqrt(sxx/syy) if syy>0 else 0.0
    rt=max(-1.0,min(1.0,rt))
    result.update(r_tempo=rt if syy>0 else None,r2_tempo=rt*rt if syy>0 else None)
    result.update(ano_inicial=min(xs),ano_final=max(xs),inclinacao=slope,variacao_reta=delta)
    if sign not in (-1,1):return result
    normative=slope*sign
    direction='estavel' if abs(delta)<=max(1,max(abs(y) for y in ys))*1e-12 else 'correta' if normative>0 else 'oposta'
    result.update(inclinacao_normativa=normative,direcao_progresso=direction)
    return result

def ambition_band(value):
    if not finite(value) or not 0<=value<=1:return None
    for cutoff,label in [(0.2,'1 — muito baixa [0; 0,2]'),(0.4,'2 — baixa (0,2; 0,4]'),(0.6,'3 — moderada (0,4; 0,6]'),(0.8,'4 — alta (0,6; 0,8]'),(1,'5 — muito alta (0,8; 1]')]:
        if value<=cutoff:return label

def edge_reading(interaction,sender,receiver):
    if sender not in ('correta','oposta') or receiver not in ('correta','oposta'):
        return 'tendencia_estavel_ou_indeterminada','indeterminada'
    same=sender==receiver
    consistent=same if interaction=='synergy' else not same
    if interaction=='synergy':
        label=('sinergia_no_avanco' if sender=='correta' else 'sinergia_no_atraso') if same else 'sinergia_com_tendencias_divergentes'
    else:
        label=('avancos_concomitantes' if sender=='correta' else 'perdas_concomitantes') if same else ('origem_avanca_destino_regride' if sender=='correta' else 'origem_regride_destino_avanca')
    return label,'compativel' if consistent else 'diverge_do_sinal_da_correlacao'

def analyze_workbook(path,norm):
    # Read formula caches before reopening with formulas for preservation.
    wb=load_workbook(path,read_only=True,data_only=True)
    try:
        sr=records(wb['Series']);canonical,_=representatives(sr)
        chosen=[r for r in sr if canonical.get(r['series_id'])==r['series_id']]
        regional=[s for s in wb if next(s.values,())[:2]==('year','region') and not s.title.endswith('_original')]
        if len(regional)!=1:raise ValueError('Tendência: esperada uma aba regional.')
        main=regional[0];data=records(main)
        original=records(wb[main.title+'_original']) if main.title+'_original' in wb.sheetnames else []
        norms={r['series_id']:r for r in records(wb['Normatividade_series'])}
        trends={}
        for r in chosen:
            sid=r['series_id'];target=str(r['targets']);sign=norms.get(sid,{}).get('Sentido')
            values=fit([(v.get('year'),v.get(sid)) for v in data],sign)
            raw=fit([(v.get('year'),v.get(sid)) for v in original],sign)
            ambition=ambition_for(target)
            trends[target]=dict(MetaODS=target,series_id=sid,Serie_API=r.get('api_series'),Sentido=sign,**values,
                inclinacao_original=raw['inclinacao'],direcao_original=raw['direcao_progresso'],n_anos_originais=raw['n_anos'],
                ambicao_meta=ambition,ambicao_faixa=ambition_band(ambition),fonte_ambicao=AMBITION_SOURCE,
                metodo='OLS nos anos da série 2000–2025 usada no Pearson, após CAGR; inclinação original informada para comparação. Direção não é magnitude nem avaliação completa de progresso.')
        edges=records(wb['rede_cytoscape'])
        pairs={(str(e['MetaA']),str(e['MetaB'])) for e in edges}
        breakdown=defaultdict(lambda:defaultdict(float));edge_details=[]
        for e in edges:
            a,b=str(e['MetaA']),str(e['MetaB']);da=trends.get(a,{}).get('direcao_progresso','indeterminada');db=trends.get(b,{}).get('direcao_progresso','indeterminada')
            label,consistent=edge_reading(e['interaction'],da,db);w=abs(float(e['weight']));typ='synergy' if e['interaction']=='synergy' else 'tradeoff'
            breakdown[a][typ+'_out_destino_'+db]+=w;breakdown[b][typ+'_in_origem_'+da]+=w
            edge_details.append(dict(**e,direcao_origem=da,direcao_destino=db,direcionalidade='bilateral' if (b,a) in pairs else 'unilateral',leitura_tendencia=label,compatibilidade=consistent))
        decomposed=[]
        for t,sums in breakdown.items():
            row=dict(MetaODS=t,direcao_progresso=trends.get(t,{}).get('direcao_progresso','indeterminada'))
            for direction in ('correta','oposta','estavel','indeterminada'):
                for typ in ('synergy','tradeoff'):
                    for suffix in ('out_destino_','in_origem_'):row[typ+'_'+suffix+direction]=sums[typ+'_'+suffix+direction]
                row['Colab_destino_'+direction]=row['synergy_out_destino_'+direction]-row['tradeoff_out_destino_'+direction]
                row['Neglect_origem_'+direction]=row['tradeoff_in_origem_'+direction]+(row['synergy_in_origem_'+direction] if direction=='oposta' else 0)
            decomposed.append(row)
    finally:wb.close()
    out=load_workbook(path)
    try:
        for name,items in [('Tendencia_local',list(trends.values())),('Leitura_arestas',edge_details),('Saldos_por_tendencia',decomposed)]:
            if name in out.sheetnames:del out[name]
            sheet=out.create_sheet(name)
            if items:
                headers=list(dict.fromkeys(k for r in items for k in r));sheet.append(headers)
                for r in items:sheet.append([r.get(k) for k in headers])
            sheet.freeze_panes='B2';sheet.auto_filter.ref=sheet.dimensions
            sheet.sheet_view.showGridLines=False
            for i in range(1,sheet.max_column+1):sheet.column_dimensions[get_column_letter(i)].width=26
            for cell in sheet[1]:
                cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='17365D');cell.alignment=Alignment(wrap_text=True)
            sheet.row_dimensions[1].height=42
            for row in sheet.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment=Alignment(vertical='top',wrap_text=True)
                    if isinstance(cell.value,float):cell.number_format='0.########'
        out.save(path)
    finally:out.close()
    return trends

def highlight_groups(metrics,details,edges=()):
    from ranking import ranked_rows
    def direction(t):return details[t][5]
    received=defaultdict(float);sent=defaultdict(float)
    for e in edges:
        a,b=str(e['MetaA']),str(e['MetaB']);w=abs(float(e['weight']))
        if a not in details or b not in details:continue
        if e['interaction']=='trade-off' and direction(a)=='oposta' and direction(b)=='correta':received[b]+=w
        if e['interaction']=='synergy' and direction(a)=='oposta':sent[a]+=w
    def top(items,score):
        ordered=sorted((t for t in items if score(t)>0),key=lambda t:(-score(t),(int(t.split('.')[0]),not t.split('.')[1].isdigit(),int(t.split('.')[1]) if t.split('.')[1].isdigit() else t.split('.')[1])))
        if not ordered:return set()
        cutoff=score(ordered[min(4,len(ordered)-1)])
        return {t for t in ordered if score(t)>=cutoff}
    good=[t for t in metrics if direction(t)=='correta'];bad=[t for t in metrics if direction(t)=='oposta']
    cg=top(good,lambda t:metrics[t]['Colab']);ng=top(bad,lambda t:metrics[t]['Neglect'])
    receivers=top(good,lambda t:received[t]);senders=top(bad,lambda t:sent[t])
    sets=[cg-receivers,cg&receivers,ng-senders,ng&senders]
    definitions=[('colaboradoras_autonomas','a · Colaboradoras — ambição > 0,6, fora do top receptor','Colab'),
                 ('colaboradoras_contextuais','b · Colaboradoras — top receptor de trade-offs do retrocesso','Colab'),
                 ('negligenciadas_baixa_ambicao','c · Negligenciadas — ambição < 0,6, fora do top emissor','Neglect'),
                 ('negligenciadas_difusoras','d · Negligenciadas — top emissor de sinergias do retrocesso','Neglect')]
    groups=[]
    for i,((slug,title,metric),selected) in enumerate(zip(definitions,sets)):
        if i in (0,2):selected={t for t in selected if finite(details[t][4]) and (details[t][4]>.6 if i==0 else details[t][4]<.6)}
        rows=[r for r in ranked_rows(metrics,details,metric) if r[1] in selected]
        groups.append(dict(id=slug,title=title,metric=metric,rows=rows,base='top 5 por direção antes dos filtros; empates no quinto incluídos'))
    return groups

def workbook_edges(path):
    wb=load_workbook(path,read_only=True,data_only=True)
    try:return records(wb['rede_cytoscape'])
    finally:wb.close()


ADVERSE_COLUMNS=['MetaA','MetaB','IndicadorA','IndicadorB','SerieAPIA','SerieAPIB',
 'Pearson','Sig','SentidoA','SentidoB','DirecaoA','DirecaoB','InclinacaoA','InclinacaoB',
 'R2A','R2B','AnosA','AnosB','InicioA','FimA','InicioB','FimB',
 'Interacao_original','Interacao_final','Acao_adversa','Motivo_adverso','weight',
 'Literatura','Regra','Evidencia']

def divergent_decision(interaction,fa,fb,pearson):
    """Limites estritos; R é R² temporal, e Pearson usa módulo."""
    da,db=fa.get('direcao_progresso'),fb.get('direcao_progresso')
    if da not in ('correta','oposta') or db not in ('correta','oposta'):
        return 'mantida',interaction,'tendência estável ou indeterminada; regra de divergência não aplicada'
    divergent=(da!=db) if interaction=='synergy' else (da==db)
    if not divergent:return 'mantida',interaction,'sentidos compatíveis'
    ra,rb=fa.get('r2_tempo'),fb.get('r2_tempo')
    if not finite(ra) or not finite(rb):
        raise ValueError('Par divergente sem R² temporal válido.')
    if min(ra,rb)<0.1:
        return 'excluida',None,'critério 1: algum R² temporal < 0,1'
    if min(ra,rb)<0.2 and abs(pearson)<0.4:
        return 'excluida',None,'critério 2: algum R² temporal < 0,2 e |Pearson| < 0,4'
    return 'reclassificada',('trade-off' if interaction=='synergy' else 'synergy'),'divergente sobrevivente: inversão do tipo conforme os sentidos temporais normativos'

def workbook_trends(workbook,meta,norm):
    regional=[s for s in workbook if next(s.values,())[:2]==('year','region') and not s.title.endswith('_original')]
    if len(regional)!=1:raise ValueError('Filtro temporal: esperada uma aba regional com valores calculados.')
    values=records(regional[0]);result={}
    for sid,s in meta.items():
        sign,_=norm.resolve(s)
        points=[(r.get('year'),r.get(sid)) for r in values]
        result[sid]=fit(points,sign)
    # Um cache Excel ausente não pode desativar silenciosamente o filtro.
    if meta and not any(f['n_anos']>=3 for f in result.values()):
        raise ValueError('Filtro temporal sem valores numéricos: recalcule o XLSX ou restaure os caches das séries.')
    return result

def case_sheet(workbook,items):
    if 'Casos adversos' in workbook.sheetnames:del workbook['Casos adversos']
    sheet=workbook.create_sheet('Casos adversos');sheet.append(ADVERSE_COLUMNS)
    for item in items:sheet.append([item.get(k) for k in ADVERSE_COLUMNS])
    sheet.freeze_panes='C2';sheet.auto_filter.ref=sheet.dimensions;sheet.sheet_view.showGridLines=False
    for i,k in enumerate(ADVERSE_COLUMNS,1):
        sheet.column_dimensions[get_column_letter(i)].width=60 if k in ('Motivo_adverso','Evidencia') else 24
    sheet.row_dimensions[1].height=38
    for cell in sheet[1]:
        cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='17365D');cell.alignment=Alignment(wrap_text=True)
    for row in sheet.iter_rows(min_row=2):
        sheet.row_dimensions[row[0].row].height=42
        for cell in row:
            cell.alignment=Alignment(vertical='top',wrap_text=True)
            if isinstance(cell.value,float):cell.number_format='0.########'
    return sheet

def read_cases(path):
    wb=load_workbook(path,read_only=True,data_only=True)
    try:return records(wb['Casos adversos']) if 'Casos adversos' in wb.sheetnames else []
    finally:wb.close()


def dependence_diagnostics(metrics, details, edges):
    """Diagnóstico contínuo; top 5 é destaque, não teste de independência."""
    values = {t:dict(MetaODS=t, Colab=metrics[t]['Colab'], synergy_out=0.0,
        synergy_out_correct=0.0, tradeoff_from_opposite=0.0,
        received_unique_direction=0.0, received_bidirectional=0.0,
        received_unspecified=0.0) for t in metrics if details[t][5]=='correta'}
    for e in edges:
        a,b=str(e['MetaA']),str(e['MetaB']); w=abs(float(e['weight']))
        if e['interaction']=='synergy' and a in values:
            values[a]['synergy_out']+=w
            if b in values:values[a]['synergy_out_correct']+=w
        if e['interaction']=='trade-off' and b in values and a in details and details[a][5]=='oposta':
            v=values[b];v['tradeoff_from_opposite']+=w
            orientation=e.get('orientacao')
            field='received_unique_direction' if orientation=='unidirecional' else 'received_bidirectional' if orientation=='bidirecional' else 'received_unspecified'
            v[field]+=w
    def ranks(key):
        pool=sorted((v for v in values.values() if v[key]>0),key=lambda v:-v[key]);out={}
        for i,v in enumerate(pool):
            rank=i+1 if i==0 or v[key]!=pool[i-1][key] else out[pool[i-1]['MetaODS']]
            out[v['MetaODS']]=rank
        return out
    cr,rr=ranks('Colab'),ranks('tradeoff_from_opposite')
    for t,v in values.items():
        v.update(colab_rank=cr.get(t),receiver_rank=rr.get(t),
            strict_highlight=bool(cr.get(t,999)<=5 and rr.get(t,999)<=5),
            exploratory_candidate=v['tradeoff_from_opposite']>0 and v['synergy_out']>0)
    return sorted(values.values(),key=lambda v:(-v['tradeoff_from_opposite'],v['MetaODS']))
