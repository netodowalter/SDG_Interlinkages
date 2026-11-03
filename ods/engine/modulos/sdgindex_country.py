"""Rede nacional do SDGIndex a partir dos escores já fornecidos, sem coleta externa.
Correlação dos escores anuais; direção exploratória condicional; tipos são
classificados conceitualmente pelas tendências de longo prazo, mantendo os coeficientes. Não usa o r regional como r nacional.
"""
import json, math
from pathlib import Path
from itertools import combinations
from collections import defaultdict
import numpy as np
from scipy import stats
from openpyxl import load_workbook
from progresso import fit,highlight_groups,dependence_diagnostics,ambition_band,divergent_decision
from redes import node_metrics

def records(sheet):
 it=iter(sheet.values);h=next(it,());return [dict(zip(h,r)) for r in it]

def association(x,y):
 n=len(x)
 if n<8 or min(np.std(x),np.std(y))<1e-12:return None,None,n
 r=float(np.clip(np.corrcoef(x,y)[0,1],-1,1))
 p=float(2*stats.t.sf(abs(r)*math.sqrt((n-2)/max(1e-15,1-r*r)),n-2))
 return r,p,n

def contemporaneous(x,y,method):
 ok=np.isfinite(x)&np.isfinite(y);a,b=x[ok],y[ok]
 if method=='spearman':a,b=stats.rankdata(a),stats.rankdata(b)
 return association(a,b)

def conditional(x,z,y,method):
 ok=np.isfinite(x)&np.isfinite(z)&np.isfinite(y);a,b,c=x[ok],z[ok],y[ok];n=len(a)
 if n<8 or min(np.std(a),np.std(b),np.std(c))<1e-12:return None,None,n
 if method=='spearman':a,b,c=[stats.rankdata(v) for v in (a,b,c)]
 control=np.column_stack((np.ones(n),b));rx=a-control@np.linalg.lstsq(control,a,rcond=None)[0];ry=c-control@np.linalg.lstsq(control,c,rcond=None)[0]
 if min(np.std(rx),np.std(ry))<1e-12:return None,None,n
 r=float(np.clip(np.corrcoef(rx,ry)[0,1],-1,1));p=float(2*stats.t.sf(abs(r)*math.sqrt((n-3)/max(1e-15,1-r*r)),n-3));return r,p,n

def bh(rows):
 valid=sorted((i for i,r in enumerate(rows) if r['p'] is not None),key=lambda i:rows[i]['p']);m=len(valid);q=1.
 for rank,i in reversed(list(enumerate(valid,1))):
  q=min(q,rows[i]['p']*m/rank);rows[i]['q_BH']=q

def sheet(w,name,items):
 if name in w.sheetnames:del w[name]
 s=w.create_sheet(name);headers=list(dict.fromkeys(k for r in items for k in r));s.append(headers or ['Sem registros'])
 for row in items:s.append([row.get(k) for k in headers])
 s.freeze_panes='B2';s.auto_filter.ref=s.dimensions
 return s

def analyze(path,mapping_path,method,country,title,output,scope="country"):
 if method not in ('pearson','spearman'):raise ValueError('Método inválido')
 w=load_workbook(path)
 # Old delta-based outputs remain source evidence, never active analysis.
 for old,new in [('Relacoes_temporais','Fonte_variacoes'),('Testes_regionais_no_pais','Fonte_testes_regionais')]:
  if old in w.sheetnames:w[old].title=new
 obs=records(w['Observacoes_componentes']);mapping={r['indicator']:r for r in json.loads(Path(mapping_path).read_text(encoding='utf-8'))}
 years=defaultdict(dict);descriptions={}
 for row in obs:
  code=row['indicador'];year=row['ano']
  if code in mapping and 2000<=year<=2025:
   years[code][year]=row['score_indicador'];descriptions[code]=row['descricao']
 codes=sorted(years);series={c:np.array([years[c].get(y) if years[c].get(y) is not None else np.nan for y in range(2000,2026)],dtype=float) for c in codes};trends={c:fit(list(years[c].items()),1) for c in codes};pairs=[]
 excluded=[]
 for i,(a,b) in enumerate(combinations(codes,2)):
  if i%500==0:print(f'Escores: examinando par {i+1} de {len(codes)*(len(codes)-1)//2}…',flush=True)
  ma,mb=mapping[a],mapping[b]
  if ma['goal']==mb['goal'] or ma['target']==mb['target']:
   excluded.append(dict(IndicadorA=a,IndicadorB=b,MetaA=ma['target'],MetaB=mb['target'],Motivo='mesma meta' if ma['target']==mb['target'] else 'mesmo ODS'));continue
  x,y=series[a],series[b];r,p,n=contemporaneous(x,y,method)
  if r is None:continue
  rab,pab,nab=contemporaneous(x[:-1],y[1:],method);rba,pba,nba=contemporaneous(y[:-1],x[1:],method)
  cab,pcab,_=conditional(x[:-1],y[:-1],y[1:],method);cba,pcba,_=conditional(y[:-1],x[:-1],x[1:],method)
  ab=pab is not None and pcab is not None and pab<.1 and pcab<.1 and rab!=0
  ba=pba is not None and pcba is not None and pba<.1 and pcba<.1 and rba!=0
  direction='ambas' if ab and ba else 'A_para_B' if ab else 'B_para_A' if ba else 'indeterminada'
  pairs.append(dict(indicator_source=a,indicator_target=b,r=r,p=p,n=n,q_BH=None,r_lag_AB=rab,p_lag_AB=pab,r_cond_AB=cab,p_cond_AB=pcab,n_AB=nab,r_lag_BA=rba,p_lag_BA=pba,r_cond_BA=cba,p_cond_BA=pcba,n_BA=nba,direction=direction))
 bh(pairs);edges=[];cases=[];changes=[];original_edges=0
 ids={c:mapping[c]['target']+'::'+c.split('_',2)[2] for c in codes}
 for pair in pairs:
  if pair['p']>=.1 or pair['r']==0:continue
  a,b=pair['indicator_source'],pair['indicator_target'];dr=pair['direction'];arcs=[(a,b)] if dr=='A_para_B' else [(b,a)] if dr=='B_para_A' else [(a,b),(b,a)]
  original='synergy' if pair['r']>0 else 'trade-off'
  action,kind,reason=divergent_decision(original,trends[a],trends[b],pair['r'])
  pair.update(interaction_original=original,interaction_final=kind,classification_action=action,classification_reason=reason)
  original_edges+=len(arcs)
  for source,target in arcs:
   fa,fb=trends[source],trends[target]
   if action!='mantida':
    cases.append(dict(IndicadorA=source,MetaA=mapping[source]['target'],IndicadorB=target,MetaB=mapping[target]['target'],Interacao_original=original,Interacao_final=kind,Acao_adversa=action,Motivo_adverso=reason,Coeficiente=pair['r'],Metodo=method,R2A=fa['r2_tempo'],R2B=fb['r2_tempo'],DirecaoA=fa['direcao_progresso'],DirecaoB=fb['direcao_progresso'],InclinacaoA=fa['inclinacao'],InclinacaoB=fb['inclinacao'],weight=abs(pair['r'])))
   if action=='excluida':continue
   if action=='reclassificada':
    changes.append(dict(source=ids[source],target=ids[target],original=original,final=kind,pearson=pair['r'],r2_source=fa['r2_tempo'],r2_target=fb['r2_tempo'],reason=reason))
   edges.append(dict(source=ids[source],target=ids[target],interaction_original=original,interaction=kind,coefficient=pair['r'],classification_action=action,weight=abs(pair['r']),orientation='unidirecional' if len(arcs)==1 else 'bidirecional',directionEvidence=dr,p=pair['p'],q=pair['q_BH']))
 connected={e[k] for e in edges for k in ('source','target')};nodes=[]
 for c in codes:
  if ids[c] not in connected:continue
  m=mapping[c];nodes.append(dict(id=ids[c],target=m['target'],indicator=c,description=descriptions[c],ambition=m['ambition'],direction=trends[c]['direcao_progresso']))
 pyedges=[dict(MetaA=e['source'],MetaB=e['target'],interaction=e['interaction'],weight=e['weight'],orientacao=e['orientation']) for e in edges];metrics0=node_metrics([n['id'] for n in nodes],pyedges,{n['id']:n['direction'] for n in nodes});metrics={};details={}
 for node in nodes:
  v=metrics0[node['id']];node.update(colab=v['colaboracao'],neglect=v['negligencia']);metrics[node['id']]=dict(Colab=node['colab'],Neglect=node['neglect']);details[node['id']]=[node['id'],node['description'],node['indicator'],node['description'],node['ambition'],node['direction'],ambition_band(node['ambition'])]
 highlights=highlight_groups(metrics,details,pyedges);diagnostics=dependence_diagnostics(metrics,details,pyedges)
 sheet(w,'Pares_excluidos_intra_ODS',excluded);sheet(w,'Relacoes_scores',pairs);sheet(w,'Rede_scores',edges);sheet(w,'Atributos_recalculados',nodes);sheet(w,'Diagnostico_dependencia',diagnostics);sheet(w,'Casos adversos',cases);sheet(w,'Tendencia_local',[dict(indicator=c,**t) for c,t in trends.items()]);sheet(w,'Metas_indicadores',[mapping[c] for c in codes]);sheet(w,'Destaques',[dict(Grupo=g['title'],Indicador=r[1],Escore=r[2]) for g in highlights for r in g['rows']]);sheet(w,'Metodo_app',[dict(Campo=k,Definicao=v) for k,v in [('Unidade','País' if scope=='country' else 'Região ou agregado') ,('Base da correlação','Escores normalizados anuais 2000–2025, sem diferenças anuais. Exclusão de todos os pares do mesmo ODS ou da mesma meta antes dos testes e dos graus.'),('Seleção','p<0,10, coeficiente não nulo, mínimo 8 pares; q_BH dos pares inter-ODS válidos para sensibilidade.'),('Direção','Escores A(t−1) e B(t), controlando B(t−1). p_lag e p_condicional <0,10 em cada sentido; demais pares têm dois arcos. Não demonstra causalidade.'),('Tipos','Associação estatística original pelo sinal do coeficiente; interação final classificada pelos sentidos do progresso. Nos discordantes: excluir se algum R²<0,1; ou algum R²<0,2 e |coeficiente|<0,4. Demais discordantes mudam de tipo. Coeficiente e peso em módulo preservados. Classificação conceitual, não teste de espuriedade.'),('Neglect','Trade-offs recebidos + sinergias recebidas de origens em retrocesso.'),('Limites','Séries normalizadas fornecidas podem conter valores carregados; p nominal não corrige autocorrelação.')]])
 w.save(output);w.close()
 return dict(region=country,title=title,method=method,basis='scores',classification='progress-direction-v1',scope=scope,pairCount=len(pairs),excludedWithinGoal=len(excluded),network=dict(dataset='SDGIndex',nodes=nodes,edges=edges,aliases=[],changes=changes),highlights=highlights,diagnostics=diagnostics,count=len(nodes),edges=len(edges),originalEdges=original_edges,adverse=dict(excluded=sum(c['Acao_adversa']=='excluida' for c in cases),reclassified=len(changes)),trendDivergences=len(cases),name=Path(output).name)
