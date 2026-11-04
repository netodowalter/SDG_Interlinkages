"""Catalogued aggregate codes must be selectable without becoming countries."""
import unittest
from sdg.service import list_areas, read_json, DATA


class ComparisonRegions(unittest.TestCase):
    def test_official_codes_and_country_scope(self):
        regions = list_areas('IGES_JRC', 'region')
        countries = list_areas('IGES_JRC', 'country')
        expected = {'198': 'OECD member states', '910': 'High income economies (WB)',
                    '911': 'Low income economies (WB)', '912': 'Lower middle income economies (WB)',
                    '914': 'Upper middle income economies (WB)'}
        self.assertEqual({code:regions[code] for code in expected}, expected)
        self.assertTrue(all(code not in countries for code in expected))
        self.assertIn('1', regions)
        self.assertIn('76', countries)
        self.assertFalse(any('BRICS' in name for name in regions.values()))

    def test_catalog_records_availability_and_comparison_identity(self):
        groups = read_json(DATA / 'iges_comparison_regions.json')['groups']
        self.assertEqual({g['sdgindex_region'] for g in groups}, {'OECD','HIC','LIC','LMIC','UMIC'})
        self.assertTrue(all(g['availability'] == 'catalog_only' and g['api_name'] for g in groups))
