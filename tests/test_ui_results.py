"""Real workbooks must expose the context measure appropriate to each dataset."""
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from sdg.ui_results import results, table_headers


class ResultTables(unittest.TestCase):
    def workbook(self, folder, version):
        book = Workbook()
        book.remove(book.active)
        for sheet, metric in [('TopCollaborators', 'Colab'), ('TopNeglected', 'Neglect')]:
            tab = book.create_sheet(sheet)
            if version == 'IGES_JRC':
                tab.append(['Ranking', 'TargetCode', metric, 'progress_direction', 'IndicatorCode', 'target_ambition'])
                tab.append([1, '11.1', 2.5, 'forward', '11.1.1', .75])
                tab.append([2, '9.b', 1.5, 'forward', '9.b.1', 0])
            else:
                tab.append(['Target', 'Indicator', 'Value', 'Direction', 'years_to_target', 'years_to_zero'])
                tab.append(['11.1', 'score_a', 2.5, 'forward', 1.23456, None])
                tab.append(['9.b', 'score_b', 1.5, 'backward', None, 0])
        tab = book.create_sheet('Highlights')
        if version == 'IGES_JRC':
            tab.append(['Group', 'TargetCode', 'Score', 'target_ambition'])
            tab.append(['a', '11.1', 2.5, .75])
            tab.append(['b', '9.b', 1.5, 0])
        else:
            tab.append(['Group', 'Indicator', 'Score', 'Years'])
            tab.append(['a', '11.1::score_a', 2.5, 1.23456])
            tab.append(['d', '9.b::score_b', 1.5, 0])
        book.save(folder / 'test_interlinkages.xlsx')
        book.close()

    def test_iges_ambitiousness_in_both_tables_including_zero(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.workbook(folder, 'IGES_JRC')
            ranked, groups, *_ = results(folder, 'IGES_JRC')
            headers, group_headers = table_headers('IGES_JRC')
            self.assertEqual(headers[-1], 'Ambitiousness')
            self.assertEqual(group_headers[-1], 'Ambitiousness')
            self.assertFalse(any('Years' in h for h in headers + group_headers))
            self.assertEqual([r[-1] for r in ranked], ['0.750', '0.000'] * 2)
            self.assertEqual([r[-1] for r in groups], ['0.750', '0.000'])
            self.assertTrue(all(len(r[:6] + r[7:]) == len(headers) for r in ranked))
            self.assertEqual(ranked[0][6], '11.1.1')

    def test_sdgindex_years_remain_separate_and_three_decimal_places(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.workbook(folder, 'SDGIndex')
            ranked, groups, *_ = results(folder, 'SDGIndex')
            headers, group_headers = table_headers('SDGIndex')
            self.assertEqual(headers[-2:], ['Years to target', 'Years to zero'])
            self.assertEqual(group_headers[-1], 'Years')
            self.assertEqual(ranked[0][-2:], ['1.235', ''])
            self.assertEqual(ranked[1][-2:], ['', '0.000'])
            self.assertEqual([r[-1] for r in groups], ['1.235', '0.000'])
            self.assertTrue(all(len(r[:6] + r[7:]) == len(headers) for r in ranked))
            self.assertEqual(ranked[0][6], 'score_a')
