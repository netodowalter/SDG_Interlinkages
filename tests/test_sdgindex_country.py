"""National reconstruction from national scores; evidence and sign preservation."""
import json,sys,tempfile,unittest,math
from pathlib import Path
from openpyxl import load_workbook,Workbook
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ods/engine/modulos'))
from sdgindex_country import analyze,contemporaneous,conditional
from progresso import divergent_decision,fit
import numpy as np
class NationalSDGIndex(unittest.TestCase):
 def test_statistics_match_scipy(self):
  x=np.array([3,4,1,9,2,7,6,2,8.,5]);y=np.array([1,8,4,2,3,9,6,2,4.,7])
  for method,fn in [('pearson',stats.pearsonr),('spearman',stats.spearmanr)]:
   r,p,n=contemporaneous(x,y,method);expected=fn(x,y)
   self.assertAlmostEqual(r,expected.statistic);self.assertAlmostEqual(p,expected.pvalue)
 def test_brazil_national_evidence_and_export(self):
  source_path=ROOT/'data/SDGIndex/countries/BRA_Brazil.xlsx'
  with tempfile.TemporaryDirectory() as temp:
   for method in ['pearson','spearman']:
    out=Path(temp)/(method+'.xlsx');data=analyze(source_path,ROOT/'data/SDGIndex/mapping.json',method,'BRA','Brazil',out)
    self.assertGreater(data['edges'],0);self.assertEqual(data['classification'],'progress-direction-v1')
    w=load_workbook(out,read_only=True,data_only=True)
    def records(name):
     it=iter(w[name].values);h=next(it);return [dict(zip(h,r)) for r in it]
    try:
     national=records('Relacoes_scores');lookup={(r['indicator_source'],r['indicator_target']):r for r in national}
     mapping={r['indicator']:r for r in json.loads((ROOT/'data/SDGIndex/mapping.json').read_text(encoding="utf-8"))}
     for pair in national:
      a,b=mapping[pair['indicator_source']],mapping[pair['indicator_target']]
      self.assertNotEqual(a['goal'],b['goal']);self.assertNotEqual(a['target'],b['target'])
     scores={}
     for r in records('Observacoes_componentes'):
      if 2000<=r['ano']<=2025 and r['score_indicador'] is not None:scores.setdefault(r['indicador'],{})[r['ano']]=r['score_indicador']
     fn=stats.pearsonr if method=='pearson' else stats.spearmanr
     for pair in national[::max(1,len(national)//30)]:
      a,b=scores[pair['indicator_source']],scores[pair['indicator_target']];years=sorted(a.keys()&b.keys());v=fn([a[y] for y in years],[b[y] for y in years])
      self.assertAlmostEqual(pair['r'],v.statistic);self.assertAlmostEqual(pair['p'],v.pvalue)
     trends={r['indicator']:r for r in records('Tendencia_local')}
     self.assertGreater(data['excludedWithinGoal'],0)
     cases=records('Casos adversos')
     self.assertEqual(data['adverse']['excluded'],sum(r['Acao_adversa']=='excluida' for r in cases))
     self.assertEqual(data['adverse']['reclassified'],sum(r['Acao_adversa']=='reclassificada' for r in cases))
     byid={n['id']:n['indicator'] for n in data['network']['nodes']}
     for edge in data['network']['edges']:
      a,b=byid[edge['source']],byid[edge['target']];pair=lookup.get((a,b)) or lookup[(b,a)]
      original='synergy' if pair['r']>0 else 'trade-off'
      action,kind,_=divergent_decision(original,trends[a],trends[b],pair['r'])
      self.assertNotEqual(action,'excluida');self.assertEqual(edge['interaction'],kind)
      self.assertEqual(edge['interaction_original'],original);self.assertAlmostEqual(edge['coefficient'],pair['r'])
      self.assertAlmostEqual(edge['weight'],abs(pair['r']));self.assertLess(pair['p'],.1)
     for pair in national:
      a,b=pair['indicator_source'],pair['indicator_target']
      if pair['p']>=.1 or pair['r']==0:continue
      original='synergy' if pair['r']>0 else 'trade-off'
      action,kind,_=divergent_decision(original,trends[a],trends[b],pair['r'])
      self.assertEqual(pair['classification_action'],action);self.assertEqual(pair['interaction_final'],kind)
      if action=='excluida':self.assertFalse(any({byid[e['source']],byid[e['target']]}=={a,b} for e in data['network']['edges']))
     self.assertIn('Diagnostico_dependencia',w.sheetnames)
    finally:w.close()

 def test_classification_precedes_metrics(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);mapping=root/'mapping.json';mapping.write_text(json.dumps([dict(indicator='n_sdg1_x',target='1.1',goal=1,ambition=.8),dict(indicator='n_sdg2_y',target='2.1',goal=2,ambition=.8)]))
   t=np.arange(26,dtype=float);t=(t-t.mean())/t.std();u=t*t;u=(u-u.mean())/u.std()
   for r2,action in [(.16,'reclassificada'),(.05,'excluida')]:
    x=50+5*(np.sqrt(r2)*t+np.sqrt(1-r2)*u);y=50+5*(-np.sqrt(r2)*t+np.sqrt(1-r2)*u)
    source=root/'source.xlsx';w=Workbook();w.active.title='Observacoes_componentes';w.active.append(['indicador','ano','score_indicador','descricao'])
    for code,values in [('n_sdg1_x',x),('n_sdg2_y',y)]:
     for year,value in enumerate(values,2000):w.active.append([code,year,float(value),code])
    w.save(source);w.close();data=analyze(source,mapping,'pearson','test','Test',root/'full.xlsx')
    if action=='reclassificada':
     self.assertEqual(data['adverse']['reclassified'],2)
     for e in data['network']['edges']:
      self.assertAlmostEqual(e['coefficient'],.68);self.assertEqual(e['interaction_original'],'synergy');self.assertEqual(e['interaction'],'trade-off')
     for n in data['network']['nodes']:self.assertAlmostEqual(n['colab'],-.68)
    else:
     self.assertEqual(data['adverse']['excluded'],2);self.assertEqual(data['edges'],0);self.assertFalse(data['network']['nodes'])
