'Regression tests: analytical identity, normative signs, and complete offline pipeline.'
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sdg/engine'))
import sdg_interlinkages as pipeline
modules=pipeline.load_modules(Path('/tmp'))
collection,prep,pearson,net,ranking=modules
from identity import representatives
from series_directionality import SIGNS

def row(sid,target,api,indicator,dimensions='{}',unit='%'):
    return dict(series_id=sid,targets=target,api_series=api,indicator_used=indicator,dimensions=dimensions,unit=unit)

class Methodology(unittest.TestCase):
    def test_neglect_adds_only_backward_synergies(self):
        edges=[dict(TargetA=a,TargetB='4.1',interaction=typ,weight=w) for a,typ,w in [('1.1','synergy',-.8),('2.1','synergy',.7),('3.1','trade-off',-.4)]]
        result=net.node_metrics(['1.1','2.1','3.1','4.1'],edges,{'1.1':'backward','2.1':'forward','3.1':'forward'})
        self.assertAlmostEqual(result['4.1']['neglect'],1.2)
        self.assertAlmostEqual(result['4.1']['synergy_in_backward'],.8)
        self.assertAlmostEqual(result['1.1']['collaboration'],.8)

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
        norm=net.Normativity(pipeline.BASES/'indicator_directionality.xlsx')
        for api,indicator,expected in [('ER_RSK_LST','15.5.1',1),('SH_SAN_DEFECT','6.2.1',-1),('SH_SAN_SAFE','6.2.1',1),('SL_TLF_UEM','8.5.1',-1),('AG_LND_FRST','15.3.1',1),('TX_EXP_GBSVR','17.11.1',1)]:
            self.assertEqual(norm.resolve(net.Series('id',indicator,api,'','{}',('1.1',)))[0],expected)
        self.assertIsNone(norm.resolve(net.Series('id','15.5.1','UNREVIEWED','','{}',('15.5',)))[0])
    def test_legacy_pearson_cannot_reintroduce_alias_nodes(self):
        target={s.id:s for s in [net.Series('native','15.1.1','AG_LND_FRST','','{}',('15.1',),'%'),net.Series('proxy','15.1.1','AG_LND_FRST','','{}',('15.3',),'%'),net.Series('other','1.1.1','SI_POV_DAY1','','{}',('1.1',),'%')]}
        rows=[dict(IndicatorA=a,IndicatorB=b,Pearson=.9,Sig=.001) for a,b in [('native','proxy'),('native','other'),('proxy','other')]]
        class Directions:
            def decide(self,*args):return True,'','test',''
            def evidence(self,*args):return ''
        edges,nodes,audit,counts=net.process_rows(rows,target,net.Normativity(pipeline.BASES/'indicator_directionality.xlsx'),Directions())
        self.assertEqual(len(edges),2)
        self.assertNotIn('15.3',{n['Target'] for n in nodes})
        self.assertEqual({e['interaction'] for e in edges},{'trade-off'})
    def test_trends_and_ambition_boundaries(self):
        from progress import fit,ambition_band,edge_reading,highlight_groups
        self.assertEqual(fit([(2000,3),(2002,2),(2005,.5)],-1)['progress_direction'],'forward')
        self.assertEqual(fit([(2000,3),(2002,2),(2005,.5)],1)['progress_direction'],'backward')
        self.assertEqual(fit([(2000,3),(2002,3),(2005,3)],1)['progress_direction'],'stable')
        self.assertEqual(fit([(2000,3),(2002,2)],1)['progress_direction'],'undetermined')
        self.assertTrue(ambition_band(.6).startswith('3'))
        self.assertTrue(ambition_band(.60001).startswith('4'))
        self.assertIsNone(ambition_band(None));self.assertIsNone(ambition_band(1.1))
        self.assertEqual(edge_reading('trade-off','backward','backward'),('concurrent_losses','diverges_from_correlation_sign'))
        self.assertEqual(edge_reading('trade-off','forward','backward')[0],'source_advances_target_regresses')
        self.assertEqual(edge_reading('synergy','backward','backward')[0],'backward_synergy')
        metrics={str(i)+'.1':dict(Colab=20-i,Neglect=20-i) for i in range(1,9)}
        details={t:[t,'name','indicator','description',.8,'forward','4'] for t in metrics}
        details['1.1'][4]=.6
        details['2.1'][5]='backward'
        details['3.1'][4]=None
        groups={g['id']:g['rows'] for g in highlight_groups(metrics,details)}
        # Ambition no longer filters contributors; 2.1 is deteriorating and stays out.
        # Three per role; low or missing ambition does not exclude.
        self.assertEqual([r[1] for r in groups['contributors']],['1.1','3.1','4.1'])
        self.assertFalse(groups['dependent_contributors'])
        self.assertEqual([r[1] for r in groups['exposed']],['2.1'])
        self.assertFalse(groups['transmission_bridges'])
    def test_six_highlight_groups(self):
        from progress import highlight_groups
        metrics={'1.1':dict(Colab=1,Neglect=0),'2.1':dict(Colab=1.5,Neglect=0),'3.1':dict(Colab=0,Neglect=2),'4.1':dict(Colab=0,Neglect=.5)}
        details={t:[t,'name','indicator','description',amb,direction,'band'] for t,amb,direction in [('1.1',.8,'forward'),('2.1',.6,'forward'),('3.1',.5,'backward'),('4.1',.9,'backward')]}
        edges=[dict(TargetA='4.1',TargetB='2.1',interaction='trade-off',weight=1),dict(TargetA='4.1',TargetB='3.1',interaction='synergy',weight=1)]
        # 2.1 gains from 4.1's deterioration and passes no synergy forward: I-3, and also a contributor
        # (roles are independent). 4.1 sends synergy to 3.1 but receives nothing from improving
        # targets: neither bridge nor relay; it is a top synergy sender, so not exposed.
        self.assertEqual([[r[1] for r in g['rows']] for g in highlight_groups(metrics,details,edges)],[['2.1','1.1'],[],['2.1'],['3.1'],[],[]])
        for value in details.values():value[4]=.6
        groups=highlight_groups(metrics,details,edges)
        # Ambition characterises; membership is unchanged.
        self.assertEqual([r[1] for r in groups[0]['rows']],['2.1','1.1']);self.assertEqual([r[1] for r in groups[3]['rows']],['3.1'])
        self.assertEqual([r[1] for r in groups[2]['rows']],['2.1'])
        self.assertFalse(groups[4]['rows']);self.assertFalse(groups[5]['rows'])
    def test_adverse_policy_and_boundaries(self):
        from progress import divergent_decision,fit
        def f(direction,r2):return dict(progress_direction=direction,time_r2=r2)
        a=f('forward',.15);b=f('backward',.35)
        self.assertEqual(divergent_decision('synergy',f('forward',.099),b,.99)[0],'excluded')
        self.assertEqual(divergent_decision('synergy',a,b,.399)[0],'excluded')
        self.assertEqual(divergent_decision('synergy',a,b,-.4)[:2],('reclassified','trade-off'))
        self.assertEqual(divergent_decision('synergy',f('forward',.2),b,.3)[0],'reclassified')
        self.assertEqual(divergent_decision('synergy',f('forward',.1),b,.5)[0],'reclassified')
        self.assertEqual(divergent_decision('trade-off',a,f('forward',.35),.41)[:2],('reclassified','synergy'))
        self.assertEqual(divergent_decision('synergy',f('backward',.001),f('backward',.002),.5)[0],'retained')
        self.assertEqual(divergent_decision('trade-off',f('backward',.001),f('forward',.002),-.5)[0],'retained')
        self.assertAlmostEqual(fit(list(zip(range(1,6),[4.8,1.9,1,2.1,5.2])),1)['time_r2'],.0070921985815602965)
    def test_adverse_precedes_node_metrics(self):
        target={s.id:s for s in [net.Series('a','6.2.1','SH_SAN_SAFE','','{}',('6.2',)),net.Series('b','15.5.1','ER_RSK_LST','','{}',('15.5',))]}
        rows=[dict(IndicatorA='a',IndicatorB='b',Pearson=.41,Sig=.01)]
        class Directions:
            def decide(self,*args):return True,'','test',''
            def evidence(self,*args):return ''
        trends={'a':dict(progress_direction='forward',time_r2=.15),'b':dict(progress_direction='backward',time_r2=.35)}
        norm=net.Normativity(pipeline.BASES/'indicator_directionality.xlsx')
        edges,nodes,audit,counts=net.process_rows(rows,target,norm,Directions(),trends=trends)
        self.assertEqual({e['interaction'] for e in edges},{'trade-off'})
        self.assertEqual(len(edges),2)
        for n in nodes:
            self.assertAlmostEqual(n['collaboration'],-.41);self.assertAlmostEqual(n['neglect'],.41)
        self.assertTrue(all(r['Pearson']==.41 and r['Adverse_action']=='reclassified' for r in audit))
        self.assertEqual(audit[1]['R2A'],.35)
        trends['a']['time_r2']=.09
        edges,nodes,audit,counts=net.process_rows(rows,target,norm,Directions(),trends=trends)
        self.assertFalse(edges);self.assertEqual(counts['adverse_excluded'],2)

    def test_complete_user_ambitions(self):
        from ambition import AMBITIONS,ambition_for
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
        records=json.loads((ROOT/'tests/browser/qa-data.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as temporary:
            temp=Path(temporary);csv_path=temp/'input.csv'
            flat=[collection.flatten(r) for r in records]
            columns=list(dict.fromkeys(k for r in flat for k in r))
            with csv_path.open('w',encoding='utf-8-sig',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=columns);writer.writeheader();writer.writerows(flat)
            work=temp/'work';work.mkdir()
            output=pipeline.run_pipeline(modules,work,dict(code=76,name='Synthetic QA'),csv_path,temp/'output')
            wb=load_workbook(next(output.glob('*_full.xlsx')),read_only=True,data_only=True)
            try:
                data=lambda name:list(ranking.rows(wb[name]))
                self.assertIn('Series_directionality',wb.sheetnames)
                self.assertNotIn('Target_metadata',wb.sheetnames)
                from ambition import AMBITIONS
                self.assertEqual({r['TargetCode']:r['target_ambition'] for r in data('Target_ambition')},AMBITIONS)
                for sheet in wb:
                    headers=set(next(sheet.values,()))
                    self.assertFalse({'prog_Pace','prog_Direction','prog_Distance','progress_pace','progress_distance'}&headers)
                for name in ('TopCollaborators','TopNeglected'):
                    for row in data(name):self.assertEqual(row['target_ambition'],AMBITIONS[row['TargetCode']])
                self.assertIn('Local_trends',wb.sheetnames)
                self.assertIn('Edge_interpretation',wb.sheetnames)
                self.assertIn('Highlights',wb.sheetnames)
                self.assertIn('Adverse cases',wb.sheetnames)
                inter=load_workbook(next(output.glob('*_interlinkages.xlsx')),read_only=True,data_only=True)
                try:self.assertEqual(list(wb['Adverse cases'].values),list(inter['Adverse cases'].values))
                finally:inter.close()
                # The link-share weighted version is always produced, with its own workbook.
                pond=load_workbook(next(output.glob('*_interlinkages_pond.xlsx')),read_only=True,data_only=True)
                try:
                    self.assertTrue({'Weighting_method','Weighting','Highlights','Interface_measures','TopCollaborators'}<=set(pond.sheetnames))
                    weighting=list(ranking.rows(pond['Weighting']))
                    self.assertTrue(weighting)
                    for r in weighting:
                        if r['share_out']:self.assertAlmostEqual(r['Colab_pond'],r['Colab']/(r['share_out']*len(weighting)))
                        if r['share_in']:self.assertAlmostEqual(r['Neglect_pond'],r['Neglect']/(r['share_in']*len(weighting)))
                    self.assertAlmostEqual(sum(r['share_out'] for r in weighting),1)
                    self.assertAlmostEqual(sum(r['share_in'] for r in weighting),1)
                finally:pond.close()
                trends={r['TargetCode']:r for r in data('Local_trends')}
                self.assertEqual(trends['1.1']['progress_direction'],'backward')
                metric_rows={r['TargetCode']:r for r in data('cytoscape_nodes')}
                for r in data('Balances_by_direction'):
                    self.assertAlmostEqual(sum(r['Colab_destination_'+d] for d in ('forward','backward','stable','undetermined')),metric_rows[r['TargetCode']]['Colab'])
                    self.assertAlmostEqual(sum(r['Neglect_source_'+d] for d in ('forward','backward','stable','undetermined')),metric_rows[r['TargetCode']]['Neglect'])
                for name in ('TopCollaborators','TopNeglected'):
                    self.assertTrue({'progress_direction','target_ambition','ambition_band'}<=set(next(wb[name].values)))
                aliases=data('Target_representation');self.assertTrue(aliases)
                for a in aliases:
                    represented=set(a['Represented_targets'].split('; '))
                    nodes={str(n['TargetCode']) for n in data('cytoscape_nodes')}
                    self.assertFalse((represented-{a['Representative_target']})&nodes)
                selected=data('Series');mapping,_=representatives(selected)
                for r in data('Pearson'):
                    self.assertEqual(mapping[r['IndicatorA']],r['IndicatorA'])
                    self.assertEqual(mapping[r['IndicatorB']],r['IndicatorB'])
                self.assertFalse(data('Unresolved_directionality'))
                for r in data('Series_directionality'):
                    if r['API_series']:self.assertEqual(r['DesiredDirection'],SIGNS[r['API_series']])
                # Formula caches survive the entire pipeline, including new audit sheets.
                regional=wb[wb.sheetnames[0]]
                self.assertTrue(any(isinstance(v,(int,float)) for row in regional.iter_rows(min_row=2,values_only=True) for v in row[2:]))
                print('Consolidation legend:',[(r['Representative_target'],r['Represented_targets']) for r in aliases])
            finally:wb.close()

if __name__=='__main__':unittest.main()
