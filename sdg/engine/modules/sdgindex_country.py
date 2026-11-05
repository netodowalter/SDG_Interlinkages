'Reconstruct SDGIndex networks from supplied annual scores. Use local conditional lag evidence for exploratory orientation and classify interaction types by long-term progress directions while preserving coefficients.'
import json, math
from pathlib import Path
from itertools import combinations
from collections import defaultdict
import numpy as np
from scipy import stats
from openpyxl import load_workbook
from progress import fit,dependence_diagnostics,divergent_decision
from networks import node_metrics
from performance_ranking import performance_time, highlight_groups, format_years, RANK_KEYS

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
 s=w.create_sheet(name);headers=list(dict.fromkeys(k for r in items for k in r));s.append(headers or ['No records'])
 for row in items:s.append([row.get(k) for k in headers])
 s.freeze_panes='B2';s.auto_filter.ref=s.dimensions
 return s

def analyze(path,mapping_path,method,country,title,output,scope='country',*,start=2000,end=2025,basis='levels',selection='p',top_n=None):
 """Sensitivity options (defaults reproduce the main specification):
 start/end: window for associations and trends; basis: 'levels' or 'changes' (first differences of
 scores for associations and orientation tests; progress directions still from levels);
 selection: 'p' (p<0.10) or 'q' (BH q<0.10); top_n: ranking cut-off for roles.
 output=None skips the workbook."""
 if method not in ('pearson','spearman'):raise ValueError('Invalid method')
 if basis not in ('levels','changes') or selection not in ('p','q'):raise ValueError('Invalid sensitivity option')
 from sdg.compat import normalize_source_workbook
 w=normalize_source_workbook(load_workbook(path))
 # Old delta-based outputs remain source evidence, never active analysis.
 for old,new in [('Temporal_relationships','Source_changes'),('Regional_tests_in_country','Source_regional_tests')]:
  if old in w.sheetnames:w[old].title=new
 obs=records(w['Component_observations']);mapping={r['indicator']:r for r in json.loads(Path(mapping_path).read_text(encoding='utf-8'))}
 years=defaultdict(dict);descriptions={}
 for row in obs:
  code=row['indicator'];year=row['year']
  if code in mapping and start<=year<=end:
   years[code][year]=row['indicator_score'];descriptions[code]=row['description']
 codes=sorted(years);series={c:np.array([years[c].get(y) if years[c].get(y) is not None else np.nan for y in range(start,end+1)],dtype=float) for c in codes};trends={c:fit(list(years[c].items()),1) for c in codes};pairs=[]
 excluded=[]
 for i,(a,b) in enumerate(combinations(codes,2)):
  if i%500==0:print(f'Scores: examining pair {i+1} of {len(codes)*(len(codes)-1)//2}…',flush=True)
  ma,mb=mapping[a],mapping[b]
  if ma['goal']==mb['goal'] or ma['target']==mb['target']:
   excluded.append(dict(IndicatorA=a,IndicatorB=b,TargetA=ma['target'],TargetB=mb['target'],Reason='same target' if ma['target']==mb['target'] else 'same SDG'));continue
  x,y=series[a],series[b]
  if basis=='changes':x,y=np.diff(x),np.diff(y)
  r,p,n=contemporaneous(x,y,method)
  if r is None:continue
  rab,pab,nab=contemporaneous(x[:-1],y[1:],method);rba,pba,nba=contemporaneous(y[:-1],x[1:],method)
  cab,pcab,_=conditional(x[:-1],y[:-1],y[1:],method);cba,pcba,_=conditional(y[:-1],x[:-1],x[1:],method)
  ab=pab is not None and pcab is not None and pab<.1 and pcab<.1 and rab!=0
  ba=pba is not None and pcba is not None and pba<.1 and pcba<.1 and rba!=0
  direction='both' if ab and ba else 'A_to_B' if ab else 'B_to_A' if ba else 'undetermined'
  pairs.append(dict(indicator_source=a,indicator_target=b,r=r,p=p,n=n,q_BH=None,r_lag_AB=rab,p_lag_AB=pab,r_cond_AB=cab,p_cond_AB=pcab,n_AB=nab,r_lag_BA=rba,p_lag_BA=pba,r_cond_BA=cba,p_cond_BA=pcba,n_BA=nba,direction=direction))
 bh(pairs);edges=[];cases=[];changes=[];original_edges=0
 ids={c:mapping[c]['target']+'::'+c.split('_',2)[2] for c in codes}
 for pair in pairs:
  if (pair['p'] if selection=='p' else pair['q_BH'])>=.1 or pair['r']==0:continue
  a,b=pair['indicator_source'],pair['indicator_target'];dr=pair['direction'];arcs=[(a,b)] if dr=='A_to_B' else [(b,a)] if dr=='B_to_A' else [(a,b),(b,a)]
  original='synergy' if pair['r']>0 else 'trade-off'
  action,kind,reason=divergent_decision(original,trends[a],trends[b],pair['r'])
  pair.update(interaction_original=original,interaction_final=kind,classification_action=action,classification_reason=reason)
  original_edges+=len(arcs)
  for source,target in arcs:
   fa,fb=trends[source],trends[target]
   if action!='retained':
    cases.append(dict(IndicatorA=source,TargetA=mapping[source]['target'],IndicatorB=target,TargetB=mapping[target]['target'],Original_interaction=original,Final_interaction=kind,Adverse_action=action,Adverse_reason=reason,Coefficient=pair['r'],Method=method,R2A=fa['time_r2'],R2B=fb['time_r2'],ProgressDirectionA=fa['progress_direction'],ProgressDirectionB=fb['progress_direction'],SlopeA=fa['slope'],SlopeB=fb['slope'],weight=abs(pair['r'])))
   if action=='excluded':continue
   if action=='reclassified':
    changes.append(dict(source=ids[source],target=ids[target],original=original,final=kind,pearson=pair['r'],r2_source=fa['time_r2'],r2_target=fb['time_r2'],reason=reason))
   edges.append(dict(source=ids[source],target=ids[target],interaction_original=original,interaction=kind,coefficient=pair['r'],classification_action=action,weight=abs(pair['r']),orientation='unidirectional' if len(arcs)==1 else 'bidirectional',directionEvidence=dr,p=pair['p'],q=pair['q_BH']))
 connected={e[k] for e in edges for k in ('source','target')};nodes=[]
 for c in codes:
  if ids[c] not in connected:continue
  m=mapping[c];nodes.append(dict(id=ids[c],target=m['target'],indicator=c,description=descriptions[c],direction=trends[c]['progress_direction'],**performance_time(list(years[c].items()),trends[c])))
 pyedges=[dict(TargetA=e['source'],TargetB=e['target'],interaction=e['interaction'],weight=e['weight'],orientation=e['orientation']) for e in edges];metrics0=node_metrics([n['id'] for n in nodes],pyedges,{n['id']:n['direction'] for n in nodes});metrics={};details={}
 for node in nodes:
  v=metrics0[node['id']];node.update(colab=v['collaboration'],neglect=v['neglect']);metrics[node['id']]=dict(Colab=node['colab'],Neglect=node['neglect']);details[node['id']]=[node['id'],node['description'],node['indicator'],node['description'],None,node['direction'],None]
 highlights=highlight_groups(nodes,edges,top_n=top_n)
 if output is None:return dict(nodes=nodes,edges=edges,highlights=highlights,pairs=pairs,trends=trends,codes=codes,ids=ids,series=series,excluded=excluded,cases=cases)
 diagnostics=dependence_diagnostics(metrics,details,pyedges)
 for diagnostic in diagnostics:
  n=next(n for n in nodes if n['id']==diagnostic['TargetCode']);diagnostic.update(colab_rank=n['colab_rank'],receiver_rank=n['improvement_receiver_rank'],strict_highlight=bool(n['colab_rank'] and n['colab_rank']<=10 and n['improvement_receiver_rank'] and n['improvement_receiver_rank']<=10))
 sheet(w,'Excluded_within_SDG_pairs',excluded);sheet(w,'Score_relationships',pairs);sheet(w,'Score_network',edges);sheet(w,'Recomputed_attributes',nodes);sheet(w,'Dependence_diagnostics',diagnostics);sheet(w,'Adverse cases',cases);sheet(w,'Local_trends',[dict(indicator=c,**t) for c,t in trends.items()]);sheet(w,'Targets_indicators',[{k:v for k,v in mapping[c].items() if k != 'ambition'} for c in codes]);sheet(w,'Highlights',[dict(Group=g['title'],Indicator=r[1],Score=r[2],Years=r[6],**{k:n[k] for k in RANK_KEYS}) for g in highlights for r in g['rows'] for n in nodes if n['id']==r[1]]);sheet(w,'App_method',[dict(Field=k,Definition=v) for k,v in [('Unit','Country' if scope=='country' else 'Region or aggregate') ,('Correlation basis','Annual normalized scores for 2000–2025, using levels. All pairs within the same SDG or target are excluded before tests and degree calculations.'),('Selection','p<0.10, nonzero coefficient, at least 8 pairs; BH q-values for valid cross-SDG pairs support sensitivity analysis.'),('Direction','Scores A(t−1) and B(t), controlling for B(t−1). Both lagged and conditional p-values must be <0.10 in each direction; other pairs receive two arcs. This does not establish causality.'),('Types','The coefficient sign defines the original statistical association. Progress directions define the final interaction. For discordant pairs, exclude if either time R²<0.1, or if either time R²<0.2 and |coefficient|<0.4. Reclassify other discordant pairs. Preserve the coefficient and absolute weight. This is conceptual classification, not a test of spurious correlation.'),('Neglect','Incoming trade-offs plus incoming synergies from sources in deterioration.'),('Performance times','Latest finite annual score and 2000–2025 linear slope: years_to_target=max(0,100-score)/slope for forward indicators; years_to_zero=max(0,score)/abs(slope) for backward indicators. Stable or undetermined trends have no finite time. Conditional extrapolations, not forecasts. Display: three decimal places.'),('Highlights','Six roles within each performance direction, listing the top 3 positive values of each role measure without exclusions or backfilling. Improving (i in I): Improvement sender = trade-off sent from i in I to D; Improvement receiver = trade-off received by i in I from D; Improvement relay = synergy degree of i within I. Deteriorating (k in D): Deterioration sender = trade-off sent from k in D to I; Deterioration receiver = trade-off received by k in D from I; Deterioration relay = synergy degree of k within D. Roles are selected independently, so an indicator may hold more than one. Years to target or to zero characterise every selected indicator; they do not filter roles. Ties resolved by node ID. Semantic ambition is not used.'),('Limitations','Supplied normalized series may include carried values; nominal p-values do not adjust for autocorrelation.')]])
 for name,key in [('Target_time_ranking','target_time_rank'),('Zero_time_ranking','zero_time_rank')]:
  sheet(w,name,sorted((n for n in nodes if n[key] is not None),key=lambda n:n[key]))
 # Remove obsolete semantic-ambition columns retained in source evidence sheets.
 for tab in w:
  for col in range(tab.max_column,0,-1):
   if tab.cell(1,col).value in ('ambition','target_ambition','ambition_band','ambition_source'):
    tab.delete_cols(col)
 format_years(w)
 w.save(output);w.close()
 return dict(region=country,title=title,method=method,basis='scores',classification='progress-direction-v1',scope=scope,pairCount=len(pairs),excludedWithinGoal=len(excluded),network=dict(dataset='SDGIndex',nodes=nodes,edges=edges,aliases=[],changes=changes),highlights=highlights,diagnostics=diagnostics,count=len(nodes),edges=len(edges),originalEdges=original_edges,adverse=dict(excluded=sum(c['Adverse_action']=='excluded' for c in cases),reclassified=len(changes)),trendDivergences=len(cases),name=Path(output).name)
