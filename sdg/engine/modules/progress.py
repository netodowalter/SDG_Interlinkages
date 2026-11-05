'Fit local temporal trends and interpret edges. These classifications do not estimate causality.'
import math
from collections import defaultdict
from openpyxl import load_workbook
from openpyxl.styles import Alignment,Font,PatternFill
from openpyxl.utils import get_column_letter
from identity import representatives
from ambition import ambition_for, SOURCE as AMBITION_SOURCE

def records(sheet):
    it=iter(sheet.values);headers=next(it,())
    return [dict(zip(headers,row)) for row in it if any(v is not None for v in row)]

def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def fit(points,sign):
    points=[(x,y) for x,y in points if finite(x) and finite(y)]
    result=dict(year_count=len(points),start_year=None,end_year=None,slope=None,fitted_change=None,normative_slope=None,time_r=None,time_r2=None,progress_direction='undetermined')
    if len(points)<3 or len({x for x,y in points})<3:return result
    xs,ys=zip(*points);xm=sum(xs)/len(xs);ym=sum(ys)/len(ys)
    slope=sum((x-xm)*(y-ym) for x,y in points)/sum((x-xm)**2 for x in xs)
    delta=slope*(max(xs)-min(xs))
    syy=sum((y-ym)**2 for y in ys);sxx=sum((x-xm)**2 for x in xs)
    rt=slope*math.sqrt(sxx/syy) if syy>0 else 0.0
    rt=max(-1.0,min(1.0,rt))
    result.update(time_r=rt if syy>0 else None,time_r2=rt*rt if syy>0 else None)
    result.update(start_year=min(xs),end_year=max(xs),slope=slope,fitted_change=delta)
    if sign not in (-1,1):return result
    normative=slope*sign
    direction='stable' if abs(delta)<=max(1,max(abs(y) for y in ys))*1e-12 else 'forward' if normative>0 else 'backward'
    result.update(normative_slope=normative,progress_direction=direction)
    return result

def ambition_band(value):
    if not finite(value) or not 0<=value<=1:return None
    for cutoff,label in [(0.2,'1 — very low [0, 0.2]'),(0.4,'2 — low (0.2, 0.4]'),(0.6,'3 — moderate (0.4, 0.6]'),(0.8,'4 — high (0.6, 0.8]'),(1,'5 — very high (0.8, 1]')]:
        if value<=cutoff:return label

def edge_reading(interaction,sender,receiver):
    if sender not in ('forward','backward') or receiver not in ('forward','backward'):
        return 'stable_or_undetermined_trend','undetermined'
    same=sender==receiver
    consistent=same if interaction=='synergy' else not same
    if interaction=='synergy':
        label=('forward_synergy' if sender=='forward' else 'backward_synergy') if same else 'synergy_with_divergent_trends'
    else:
        label=('concurrent_advances' if sender=='forward' else 'concurrent_losses') if same else ('source_advances_target_regresses' if sender=='forward' else 'source_regresses_target_advances')
    return label,'consistent' if consistent else 'diverges_from_correlation_sign'

def analyze_workbook(path,norm):
    # Read formula caches before reopening with formulas for preservation.
    wb=load_workbook(path,read_only=True,data_only=True)
    try:
        sr=records(wb['Series']);canonical,_=representatives(sr)
        chosen=[r for r in sr if canonical.get(r['series_id'])==r['series_id']]
        regional=[s for s in wb if next(s.values,())[:2]==('year','region') and not s.title.endswith('_original')]
        if len(regional)!=1:raise ValueError('Trend: exactly one regional sheet is required.')
        main=regional[0];data=records(main)
        original=records(wb[main.title+'_original']) if main.title+'_original' in wb.sheetnames else []
        norms={r['series_id']:r for r in records(wb['Series_directionality'])}
        trends={}
        for r in chosen:
            sid=r['series_id'];target=str(r['targets']);sign=norms.get(sid,{}).get('DesiredDirection')
            values=fit([(v.get('year'),v.get(sid)) for v in data],sign)
            raw=fit([(v.get('year'),v.get(sid)) for v in original],sign)
            ambition=ambition_for(target)
            trends[target]=dict(TargetCode=target,series_id=sid,API_series=r.get('api_series'),DesiredDirection=sign,**values,
                original_slope=raw['slope'],original_direction=raw['progress_direction'],original_year_count=raw['year_count'],
                target_ambition=ambition,ambition_band=ambition_band(ambition),ambition_source=AMBITION_SOURCE,
                method='OLS over the 2000–2025 series used for Pearson after CAGR filling; original slope included for comparison. Direction does not measure magnitude or constitute a complete progress assessment.')
        edges=records(wb['cytoscape_edges'])
        pairs={(str(e['TargetA']),str(e['TargetB'])) for e in edges}
        breakdown=defaultdict(lambda:defaultdict(float));edge_details=[]
        for e in edges:
            a,b=str(e['TargetA']),str(e['TargetB']);da=trends.get(a,{}).get('progress_direction','undetermined');db=trends.get(b,{}).get('progress_direction','undetermined')
            label,consistent=edge_reading(e['interaction'],da,db);w=abs(float(e['weight']));typ='synergy' if e['interaction']=='synergy' else 'tradeoff'
            breakdown[a][typ+'_out_destination_'+db]+=w;breakdown[b][typ+'_in_source_'+da]+=w
            edge_details.append(dict(**e,source_direction=da,target_direction=db,directionality='bilateral' if (b,a) in pairs else 'unilateral',trend_reading=label,consistency=consistent))
        decomposed=[]
        for t,sums in breakdown.items():
            row=dict(TargetCode=t,progress_direction=trends.get(t,{}).get('progress_direction','undetermined'))
            for direction in ('forward','backward','stable','undetermined'):
                for typ in ('synergy','tradeoff'):
                    for suffix in ('out_destination_','in_source_'):row[typ+'_'+suffix+direction]=sums[typ+'_'+suffix+direction]
                row['Colab_destination_'+direction]=row['synergy_out_destination_'+direction]-row['tradeoff_out_destination_'+direction]
                row['Neglect_source_'+direction]=row['tradeoff_in_source_'+direction]+(row['synergy_in_source_'+direction] if direction=='backward' else 0)
            decomposed.append(row)
    finally:wb.close()
    out=load_workbook(path)
    try:
        for name,items in [('Local_trends',list(trends.values())),('Edge_interpretation',edge_details),('Balances_by_direction',decomposed)]:
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

def interface_nodes(metrics,details,edges=(),pond=False):
    '''Colab, Neglect and interface measures per connected target (see roles.py).
    pond=True divides each measure by the target's share of sent or received links (NT Dinte 77, eq. 1).'''
    from roles import interface_measures,link_shares,ponderate
    direction={t:details[t][5] for t in metrics}
    arcs=[(str(e['TargetA']),str(e['TargetB']),e['interaction'],e['weight']) for e in edges]
    measures=interface_measures(direction,arcs)
    nodes={t:dict(direction=direction[t],colab=metrics[t]['Colab'],neglect=metrics[t]['Neglect'],**measures[t]) for t in metrics}
    if pond:
        shares=link_shares(metrics,arcs)
        nodes={t:ponderate(n,shares[t]) for t,n in nodes.items()}
    return nodes

def _target_order(t):
    goal,suffix=t.split('.',1)
    return (int(goal),not suffix.isdigit(),int(suffix) if suffix.isdigit() else suffix)

def top_ten(nodes,field,direction,n=None,keep=None):
    'Top n (default ten) positive values within a performance direction, after keep(); exact ties at the last place included.'
    n=n or 10
    ordered=sorted((t for t,x in nodes.items() if x['direction']==direction and finite(x[field]) and x[field]>0 and (keep is None or keep(t))),
                   key=lambda t:(-nodes[t][field],_target_order(t)))
    if not ordered:return set()
    cutoff=nodes[ordered[min(n-1,len(ordered)-1)]][field]
    return {t for t in ordered if nodes[t][field]>=cutoff}

def highlight_groups(metrics,details,edges=(),pond=False):
    from ranking import ranked_rows
    from roles import ROLES,select_roles
    nodes=interface_nodes(metrics,details,edges,pond)
    # Semantic ambitiousness characterises each selected target in its row; it does not filter roles.
    selected=select_roles(lambda field,direction,n=None,keep=None:top_ten(nodes,field,direction,n,keep),{t:n['forward_ratio'] for t,n in nodes.items()})
    scored={t:dict(metrics[t],**{label:nodes[t][field] for _,_,field,label,_ in ROLES}) for t in metrics}
    groups=[]
    for slug,title,field,label,_ in ROLES:
        rows=[r for r in ranked_rows(scored,details,label) if r[1] in selected[slug]]
        groups.append(dict(id=slug,title=title,metric=label,rows=rows,base='three highest values of the role score; roles selected independently; ties at third place included'))
    return groups

def interface_rows(metrics,details,edges=(),pond=False):
    'One row per connected target: interface measures, ranks and assigned role.'
    nodes=interface_nodes(metrics,details,edges,pond)
    role={}
    for g in highlight_groups(metrics,details,edges,pond):
        for r in g['rows']:role[r[1]]=role[r[1]]+'; '+g['title'] if r[1] in role else g['title']
    fields=('colab','neglect','tradeoff_received_from_backward','forward_synergy_sent','forward_ratio','tradeoff_sent_to_backward',
            'tradeoff_received_from_forward','synergy_received_from_backward','synergy_sent_to_backward','backward_synergy_sent','bridge_flow','relay_flow')
    rows=[]
    for t in sorted(nodes,key=_target_order):
        n=nodes[t];rows.append(dict(TargetCode=t,progress_direction=n['direction'],role=role.get(t,''),**{f:n[f] for f in fields},
            **({k:n[k] for k in ('links_out','links_in','share_out','share_in','relative_out','relative_in')} if pond else {})))
    return rows

def weighting_rows(metrics,details,edges=()):
    '''Compare original and link-share weighted rankings (NT Dinte 77). A large shift suggests that a
    position may reflect how many links the literature records for a target rather than their strength.'''
    from roles import link_shares
    weighted=interface_nodes(metrics,details,edges,True)
    def ranks(values):
        ordered=sorted(values,key=lambda t:(-values[t],_target_order(t)));out={};previous=None
        for position,t in enumerate(ordered,1):
            if previous is None or values[t]!=previous[1]:previous=(position,values[t])
            out[t]=previous[0]
        return out
    cr,nr=ranks({t:metrics[t]['Colab'] for t in metrics}),ranks({t:metrics[t]['Neglect'] for t in metrics})
    cw,nw=ranks({t:weighted[t]['colab'] for t in metrics}),ranks({t:weighted[t]['neglect'] for t in metrics})
    rows=[]
    for t in sorted(metrics,key=_target_order):
        w=weighted[t]
        rows.append(dict(TargetCode=t,progress_direction=details[t][5],links_out=w['links_out'],links_in=w['links_in'],
            share_out=w['share_out'],share_in=w['share_in'],relative_out=w['relative_out'],relative_in=w['relative_in'],Colab=metrics[t]['Colab'],Colab_pond=w['colab'],
            Colab_rank=cr[t],Colab_pond_rank=cw[t],Colab_rank_shift=cr[t]-cw[t],
            Neglect=metrics[t]['Neglect'],Neglect_pond=w['neglect'],Neglect_rank=nr[t],Neglect_pond_rank=nw[t],
            Neglect_rank_shift=nr[t]-nw[t],
            top10_Colab_and_top10_Neglect_pond=cr[t]<=10 and nw[t]<=10))
    return rows

def workbook_edges(path):
    wb=load_workbook(path,read_only=True,data_only=True)
    try:return records(wb['cytoscape_edges'])
    finally:wb.close()


ADVERSE_COLUMNS=['TargetA','TargetB','IndicatorA','IndicatorB','API_series_A','API_series_B',
 'Pearson','Sig','DesiredDirectionA','DesiredDirectionB','ProgressDirectionA','ProgressDirectionB','SlopeA','SlopeB',
 'R2A','R2B','YearsA','YearsB','StartA','EndA','StartB','EndB',
 'Original_interaction','Final_interaction','Adverse_action','Adverse_reason','weight',
 'Literature','Rule','Evidence']

def divergent_decision(interaction,fa,fb,pearson):
    'Strict bounds; R refers to time R² and the association coefficient is used in absolute value.'
    da,db=fa.get('progress_direction'),fb.get('progress_direction')
    if da not in ('forward','backward') or db not in ('forward','backward'):
        return 'retained',interaction,'stable or undetermined trend; divergence rule not applied'
    divergent=(da!=db) if interaction=='synergy' else (da==db)
    if not divergent:return 'retained',interaction,'consistent directions'
    ra,rb=fa.get('time_r2'),fb.get('time_r2')
    if not finite(ra) or not finite(rb):
        raise ValueError('Divergent pair without valid time R².')
    if min(ra,rb)<0.1:
        return 'excluded',None,'criterion 1: either time R² < 0.1'
    if min(ra,rb)<0.2 and abs(pearson)<0.4:
        return 'excluded',None,'criterion 2: either time R² < 0.2 and |coefficient| < 0.4'
    return 'reclassified',('trade-off' if interaction=='synergy' else 'synergy'),'surviving divergent pair: interaction type reversed according to normative temporal directions'

def workbook_trends(workbook,target,norm):
    regional=[s for s in workbook if next(s.values,())[:2]==('year','region') and not s.title.endswith('_original')]
    if len(regional)!=1:raise ValueError('Temporal filter requires one regional sheet with calculated values.')
    values=records(regional[0]);result={}
    for sid,s in target.items():
        sign,_=norm.resolve(s)
        points=[(r.get('year'),r.get(sid)) for r in values]
        result[sid]=fit(points,sign)
    # Missing Excel caches must never silently disable the filter.
    if target and not any(f['year_count']>=3 for f in result.values()):
        raise ValueError('Temporal filter has no numeric values: recalculate the XLSX or restore the series caches.')
    return result

def case_sheet(workbook,items):
    if 'Adverse cases' in workbook.sheetnames:del workbook['Adverse cases']
    sheet=workbook.create_sheet('Adverse cases');sheet.append(ADVERSE_COLUMNS)
    for item in items:sheet.append([item.get(k) for k in ADVERSE_COLUMNS])
    sheet.freeze_panes='C2';sheet.auto_filter.ref=sheet.dimensions;sheet.sheet_view.showGridLines=False
    for i,k in enumerate(ADVERSE_COLUMNS,1):
        sheet.column_dimensions[get_column_letter(i)].width=60 if k in ('Adverse_reason','Evidence') else 24
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
    try:return records(wb['Adverse cases']) if 'Adverse cases' in wb.sheetnames else []
    finally:wb.close()


def dependence_diagnostics(metrics, details, edges):
    'Continuous diagnostic; top ten is a highlight criterion, not an independence test.'
    values = {t:dict(TargetCode=t, Colab=metrics[t]['Colab'], synergy_out=0.0,
        synergy_out_correct=0.0, tradeoff_from_opposite=0.0,
        received_unique_direction=0.0, received_bidirectional=0.0,
        received_unspecified=0.0) for t in metrics if details[t][5]=='forward'}
    for e in edges:
        a,b=str(e['TargetA']),str(e['TargetB']); w=abs(float(e['weight']))
        if e['interaction']=='synergy' and a in values:
            values[a]['synergy_out']+=w
            if b in values:values[a]['synergy_out_correct']+=w
        if e['interaction']=='trade-off' and b in values and a in details and details[a][5]=='backward':
            v=values[b];v['tradeoff_from_opposite']+=w
            orientation=e.get('orientation')
            field='received_unique_direction' if orientation=='unidirectional' else 'received_bidirectional' if orientation=='bidirectional' else 'received_unspecified'
            v[field]+=w
    def ranks(key):
        pool=sorted((v for v in values.values() if v[key]>0),key=lambda v:-v[key]);out={}
        for i,v in enumerate(pool):
            rank=i+1 if i==0 or v[key]!=pool[i-1][key] else out[pool[i-1]['TargetCode']]
            out[v['TargetCode']]=rank
        return out
    cr,rr=ranks('Colab'),ranks('tradeoff_from_opposite')
    for t,v in values.items():
        v.update(colab_rank=cr.get(t),receiver_rank=rr.get(t),
            strict_highlight=bool(cr.get(t,999)<=10 and rr.get(t,999)<=10),
            exploratory_candidate=v['tradeoff_from_opposite']>0 and v['synergy_out']>0)
    return sorted(values.values(),key=lambda v:(-v['tradeoff_from_opposite'],v['TargetCode']))
