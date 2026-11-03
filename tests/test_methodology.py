"""Regression tests: analytical identity, normative signs, and complete offline pipeline."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ods/engine'))
import ods_interlinkages as pipeline
modules=pipeline.load_modules(Path('/tmp'))
coleta,prep,pearson,net,ranking=modules
from identidade import representatives
from normas_series import SIGNS

def row(sid,target,api,indicator,dimensions='{}',unit='%'):
    return dict(series_id=sid,targets=target,api_series=api,indicator_used=indicator,dimensions=dimensions,unit=unit)

class Methodology(unittest.TestCase):
    def test_neglect_adds_only_backward_synergies(self):
        edges=[dict(MetaA=a,MetaB='4.1',interaction=typ,weight=w) for a,typ,w in [('1.1','synergy',-.8),('2.1','synergy',.7),('3.1','trade-off',-.4)]]
        result=net.node_metrics(['1.1','2.1','3.1','4.1'],edges,{'1.1':'oposta','2.1':'correta','3.1':'correta'})
        self.assertAlmostEqual(result['4.1']['negligencia'],1.2)
        self.assertAlmostEqual(result['4.1']['synergy_in_oposta'],.8)
        self.assertAlmostEqual(result['1.1']['colaboracao'],.8)

    def test_identity_not_correlation(self):
        rows=[row('proxy','15.3','AG_LND_FRST','15.1.1'),row('native','15.1','AG_LND_FRST','15.1.1'),row('distinct','2.4','OTHER','2.4.1'),row('dimension','15.2','AG_LND_FRST','15.1.1','{"location":"urban"}'),row('unit','15.4','AG_LND_FRST','15.1.1',unit='km2')]
        mapping,legend=representatives(rows)
        self.assertEqual(mapping['proxy'],'native')
        self.assertEqual(mapping['distinct'],'distinct')
        self.assertEqual(mapping['dimension'],'dimension')
        self.assertEqual(mapping['unit'],'unit')
        self.assertEqual(legend[0]['represents'],['15.1','15.3'])
        self.assertEqual(mapping,representatives(list(reversed(rows)))[0])
    def test_all_configured_api_codes_reviewed(self):
        self.assertEqual({r['api_series'] for r in prep.DEFAULT_CONFIG['rules']},set(SIGNS))
        norm=net.Normativity(pipeline.BASES/'normatividade.xlsx')
        for api,indicator,expected in [('ER_RSK_LST','15.5.1',1),('SH_SAN_DEFECT','6.2.1',-1),('SH_SAN_SAFE','6.2.1',1),('SL_TLF_UEM','8.5.1',-1),('AG_LND_FRST','15.3.1',1),('TX_EXP_GBSVR','17.11.1',1)]:
            self.assertEqual(norm.resolve(net.Series('id',indicator,api,'','{}',('1.1',)))[0],expected)
        self.assertIsNone(norm.resolve(net.Series('id','15.5.1','UNREVIEWED','','{}',('15.5',)))[0])
    def test_legacy_pearson_cannot_reintroduce_alias_nodes(self):
        meta={s.id:s for s in [net.Series('native','15.1.1','AG_LND_FRST','','{}',('15.1',),'%'),net.Series('proxy','15.1.1','AG_LND_FRST','','{}',('15.3',),'%'),net.Series('other','1.1.1','SI_POV_DAY1','','{}',('1.1',),'%')]}
        rows=[dict(IndicadorA=a,IndicadorB=b,Pearson=.9,Sig=.001) for a,b in [('native','proxy'),('native','other'),('proxy','other')]]
        class Directions:
            def decide(self,*args):return True,'','test',''
            def evidence(self,*args):return ''
        edges,nodes,audit,counts=net.process_rows(rows,meta,net.Normativity(pipeline.BASES/'normatividade.xlsx'),Directions())
        self.assertEqual(len(edges),2)
        self.assertNotIn('15.3',{n['Meta'] for n in nodes})
        self.assertEqual({e['interaction'] for e in edges},{'trade-off'})
    def test_trends_and_ambition_boundaries(self):
        from progresso import fit,ambition_band,edge_reading,highlight_groups
        self.assertEqual(fit([(2000,3),(2002,2),(2005,.5)],-1)['direcao_progresso'],'correta')
        self.assertEqual(fit([(2000,3),(2002,2),(2005,.5)],1)['direcao_progresso'],'oposta')
        self.assertEqual(fit([(2000,3),(2002,3),(2005,3)],1)['direcao_progresso'],'estavel')
        self.assertEqual(fit([(2000,3),(2002,2)],1)['direcao_progresso'],'indeterminada')
        self.assertTrue(ambition_band(.6).startswith('3'))
        self.assertTrue(ambition_band(.60001).startswith('4'))
        self.assertIsNone(ambition_band(None));self.assertIsNone(ambition_band(1.1))
        self.assertEqual(edge_reading('trade-off','oposta','oposta'),('perdas_concomitantes','diverge_do_sinal_da_correlacao'))
        self.assertEqual(edge_reading('trade-off','correta','oposta')[0],'origem_avanca_destino_regride')
        self.assertEqual(edge_reading('synergy','oposta','oposta')[0],'sinergia_no_atraso')
        metrics={str(i)+'.1':dict(Colab=20-i,Neglect=20-i) for i in range(1,9)}
        details={t:[t,'name','indicator','description',.8,'correta','4'] for t in metrics}
        details['1.1'][4]=.6
        details['2.1'][5]='oposta'
        details['3.1'][4]=None
        groups={g['id']:g['rows'] for g in highlight_groups(metrics,details)}
        self.assertEqual([r[1] for r in groups['colaboradoras_autonomas']],['4.1','5.1','6.1'])
        self.assertFalse(groups['colaboradoras_contextuais'])
        self.assertFalse(groups['negligenciadas_baixa_ambicao'])
        self.assertFalse(groups['negligenciadas_difusoras'])
    def test_four_highlight_groups(self):
        from progresso import highlight_groups
        metrics={'1.1':dict(Colab=1,Neglect=0),'2.1':dict(Colab=1.5,Neglect=0),'3.1':dict(Colab=0,Neglect=2),'4.1':dict(Colab=0,Neglect=.5)}
        details={t:[t,'name','indicator','description',amb,direction,'band'] for t,amb,direction in [('1.1',.8,'correta'),('2.1',.6,'correta'),('3.1',.5,'oposta'),('4.1',.9,'oposta')]}
        edges=[dict(MetaA='4.1',MetaB='2.1',interaction='trade-off',weight=1),dict(MetaA='4.1',MetaB='3.1',interaction='synergy',weight=1)]
        self.assertEqual([[r[1] for r in g['rows']] for g in highlight_groups(metrics,details,edges)],[['1.1'],['2.1'],['3.1'],['4.1']])
        for value in details.values():value[4]=.6
        groups=highlight_groups(metrics,details,edges)
        self.assertFalse(groups[0]['rows']);self.assertFalse(groups[2]['rows'])
        self.assertEqual([r[1] for r in groups[1]['rows']],['2.1'])
        self.assertEqual([r[1] for r in groups[3]['rows']],['4.1'])
    def test_adverse_policy_and_boundaries(self):
        from progresso import divergent_decision,fit
        def f(direction,r2):return dict(direcao_progresso=direction,r2_tempo=r2)
        a=f('correta',.15);b=f('oposta',.35)
        self.assertEqual(divergent_decision('synergy',f('correta',.099),b,.99)[0],'excluida')
        self.assertEqual(divergent_decision('synergy',a,b,.399)[0],'excluida')
        self.assertEqual(divergent_decision('synergy',a,b,-.4)[:2],('reclassificada','trade-off'))
        self.assertEqual(divergent_decision('synergy',f('correta',.2),b,.3)[0],'reclassificada')
        self.assertEqual(divergent_decision('synergy',f('correta',.1),b,.5)[0],'reclassificada')
        self.assertEqual(divergent_decision('trade-off',a,f('correta',.35),.41)[:2],('reclassificada','synergy'))
        self.assertEqual(divergent_decision('synergy',f('oposta',.001),f('oposta',.002),.5)[0],'mantida')
        self.assertEqual(divergent_decision('trade-off',f('oposta',.001),f('correta',.002),-.5)[0],'mantida')
        self.assertAlmostEqual(fit(list(zip(range(1,6),[4.8,1.9,1,2.1,5.2])),1)['r2_tempo'],.0070921985815602965)
    def test_adverse_precedes_node_metrics(self):
        meta={s.id:s for s in [net.Series('a','6.2.1','SH_SAN_SAFE','','{}',('6.2',)),net.Series('b','15.5.1','ER_RSK_LST','','{}',('15.5',))]}
        rows=[dict(IndicadorA='a',IndicadorB='b',Pearson=.41,Sig=.01)]
        class Directions:
            def decide(self,*args):return True,'','test',''
            def evidence(self,*args):return ''
        trends={'a':dict(direcao_progresso='correta',r2_tempo=.15),'b':dict(direcao_progresso='oposta',r2_tempo=.35)}
        norm=net.Normativity(pipeline.BASES/'normatividade.xlsx')
        edges,nodes,audit,counts=net.process_rows(rows,meta,norm,Directions(),trends=trends)
        self.assertEqual({e['interaction'] for e in edges},{'trade-off'})
        self.assertEqual(len(edges),2)
        for n in nodes:
            self.assertAlmostEqual(n['colaboracao'],-.41);self.assertAlmostEqual(n['negligencia'],.41)
        self.assertTrue(all(r['Pearson']==.41 and r['Acao_adversa']=='reclassificada' for r in audit))
        self.assertEqual(audit[1]['R2A'],.35)
        trends['a']['r2_tempo']=.09
        edges,nodes,audit,counts=net.process_rows(rows,meta,norm,Directions(),trends=trends)
        self.assertFalse(edges);self.assertEqual(counts['adversos_excluida'],2)

    def test_complete_user_ambitions(self):
        from ambicao import AMBITIONS,ambition_for
        self.assertEqual(len(AMBITIONS),169)
        self.assertEqual(ambition_for('11.1'),.750)
        for target in ('5.4','9.b','11.c','12.b','12.c','17.15'):self.assertEqual(ambition_for(target),0)
        self.assertEqual(ambition_for('8.7'),1)
        metrics={'11.1':dict(Colab=5,Neglect=3),'9.b':dict(Colab=2,Neglect=1)}
        details,_=ranking.prepare_details(metrics,{}, {'11.1':['11.1.1'],'9.b':['9.b.1']},{('11.1','11.1.1'):['test'],('9.b','9.b.1'):['test']},{'11.1':'test','9.b':'test'},{})
        self.assertEqual(details['11.1'][4],.750)
        self.assertEqual(details['9.b'][4],0)
        self.assertTrue(details['9.b'][6].startswith('1'))
    def test_offline_pipeline(self):
        records=json.loads((ROOT/'tests/browser/qa-data.json').read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            temp=Path(temporary);csv_path=temp/'input.csv'
            flat=[coleta.achatar(r) for r in records]
            columns=list(dict.fromkeys(k for r in flat for k in r))
            with csv_path.open('w',encoding='utf-8-sig',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=columns);writer.writeheader();writer.writerows(flat)
            work=temp/'work';work.mkdir()
            output=pipeline.run_pipeline(modules,work,dict(codigo=76,nome='Synthetic QA'),csv_path,temp/'output')
            wb=load_workbook(next(output.glob('*_full.xlsx')),read_only=True,data_only=True)
            try:
                data=lambda name:list(ranking.rows(wb[name]))
                self.assertIn('Normatividade_series',wb.sheetnames)
                self.assertNotIn('Target_metadata',wb.sheetnames)
                from ambicao import AMBITIONS
                self.assertEqual({r['MetaODS']:r['ambicao_meta'] for r in data('Ambicao_metas')},AMBITIONS)
                for sheet in wb:
                    headers=set(next(sheet.values,()))
                    self.assertFalse({'prog_Pace','prog_Direction','prog_Distance','progress_pace','progress_direction','progress_distance'}&headers)
                for name in ('MaisColaboradoras','MaisNegligenciadas'):
                    for row in data(name):self.assertEqual(row['ambicao_meta'],AMBITIONS[row['MetaODS']])
                self.assertIn('Tendencia_local',wb.sheetnames)
                self.assertIn('Leitura_arestas',wb.sheetnames)
                self.assertIn('Destaques',wb.sheetnames)
                self.assertIn('Casos adversos',wb.sheetnames)
                inter=load_workbook(next(output.glob('*_interlinkages.xlsx')),read_only=True,data_only=True)
                try:self.assertEqual(list(wb['Casos adversos'].values),list(inter['Casos adversos'].values))
                finally:inter.close()
                trends={r['MetaODS']:r for r in data('Tendencia_local')}
                self.assertEqual(trends['1.1']['direcao_progresso'],'oposta')
                metric_rows={r['MetaODS']:r for r in data('metas_cytoscape')}
                for r in data('Saldos_por_tendencia'):
                    self.assertAlmostEqual(sum(r['Colab_destino_'+d] for d in ('correta','oposta','estavel','indeterminada')),metric_rows[r['MetaODS']]['Colab'])
                    self.assertAlmostEqual(sum(r['Neglect_origem_'+d] for d in ('correta','oposta','estavel','indeterminada')),metric_rows[r['MetaODS']]['Neglect'])
                for name in ('MaisColaboradoras','MaisNegligenciadas'):
                    self.assertTrue({'direcao_progresso','ambicao_meta','ambicao_faixa'}<=set(next(wb[name].values)))
                aliases=data('Representacao_metas');self.assertTrue(aliases)
                for a in aliases:
                    represented=set(a['Metas_representadas'].split('; '))
                    nodes={str(n['MetaODS']) for n in data('metas_cytoscape')}
                    self.assertFalse((represented-{a['Meta_representante']})&nodes)
                selected=data('Series');mapping,_=representatives(selected)
                for r in data('Pearson'):
                    self.assertEqual(mapping[r['IndicadorA']],r['IndicadorA'])
                    self.assertEqual(mapping[r['IndicadorB']],r['IndicadorB'])
                self.assertFalse(data('Pendencias_normatividade'))
                for r in data('Normatividade_series'):
                    if r['Serie_API']:self.assertEqual(r['Sentido'],SIGNS[r['Serie_API']])
                # Formula caches survive the entire pipeline, including new audit sheets.
                regional=wb[wb.sheetnames[0]]
                self.assertTrue(any(isinstance(v,(int,float)) for row in regional.iter_rows(min_row=2,values_only=True) for v in row[2:]))
                print('Consolidation legend:',[(r['Meta_representante'],r['Metas_representadas']) for r in aliases])
            finally:wb.close()

if __name__=='__main__':unittest.main()
