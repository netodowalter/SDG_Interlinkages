"""Regression coverage for official terminology and earlier workbook inputs."""
import json
import unittest
from pathlib import Path

from openpyxl import Workbook
from sdg.compat import normalize_source_workbook

ROOT = Path(__file__).resolve().parents[1]


class EnglishMigration(unittest.TestCase):
    def test_complete_official_target_catalogue(self):
        catalog = json.loads((ROOT / 'data/un_sdg_catalogue.json').read_text(encoding='utf-8'))
        ambition = json.loads((ROOT / 'sdg/engine/bases/target_ambition.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['goals']), 17)
        self.assertEqual(set(catalog['targets']), set(ambition['values']))
        self.assertEqual(len(catalog['targets']), 169)
        self.assertTrue(catalog['indicators']['15.5.1'].startswith('Red List Index'))
        self.assertIn('unstats.un.org', catalog['source'])

    def test_legacy_headers_preserve_observations(self):
        book = Workbook()
        sheet = book.active
        sheet.title = 'Observacoes_componentes'
        sheet.append(['indicador', 'ano', 'score_indicador', 'descricao'])
        sheet.append(['n_sdg1_wpc', 2014, 73.125, 'Poverty headcount ratio'])
        normalize_source_workbook(book)
        self.assertEqual(next(book.active.values), ('indicator', 'year', 'indicator_score', 'description'))
        self.assertEqual(list(book.active.values)[1], ('n_sdg1_wpc', 2014, 73.125, 'Poverty headcount ratio'))
        self.assertIn('Component_observations', book.sheetnames)
        book.close()
