import json
import unittest
from unittest import mock

import provider

SAMPLE_FEATURE = {'attributes': {'objectid': 13, 'county_pin': '368390010271', 'co_name': 'Dakota', 'year_built': 1932, 'emv_total': 238800, 'useclass1': 'Residential', 'acres_poly': 0.1548515}}
NEW_FEATURE = {'attributes': {'objectid': 226, 'county_pin': '1049100101210', 'co_name': 'Dakota', 'year_built': 2025, 'emv_total': 237600, 'useclass1': 'Exempt', 'acres_poly': 0.0258042}}
UNKNOWN_AGE_FEATURE = {'attributes': {'objectid': 42, 'county_pin': '361990101110', 'co_name': 'Dakota', 'year_built': 0, 'emv_total': 57400, 'useclass1': 'Residential', 'acres_poly': 0.27239037}}


class NearbyScanContract(unittest.TestCase):
    def _run(self, payload=None, side_effect=None, **overrides):
        args = {'latitude': 44.8884308, 'longitude': -93.0510375, 'radius_km': 1.0, 'minimum_age': 35, 'limit': 20}
        args.update(overrides)
        with mock.patch.object(provider, '_fetch_json', return_value=payload, side_effect=side_effect) as fetch:
            result = provider.scan_nearby(**args)
        return result, fetch

    def test_returns_allowlisted_fields_only(self):
        result, _ = self._run(payload={'features': [SAMPLE_FEATURE]})
        self.assertTrue(result['available'])
        self.assertEqual(len(result['properties']), 1)
        record = result['properties'][0]
        self.assertEqual(set(record), set(provider.ALLOWLIST))
        self.assertEqual(record['parcel_id'], '368390010271')
        self.assertIsNone(result['reason'])

    def test_radius_is_clamped_to_requirement_max(self):
        result, fetch = self._run(payload={'features': [SAMPLE_FEATURE]}, radius_km=50)
        called_url = fetch.call_args[0][0]
        self.assertIn('distance=3.0', called_url)
        self.assertEqual(result['radius_km'], provider.RADIUS_KM_MAX)

    def test_result_limit_is_clamped(self):
        result, _ = self._run(payload={'features': [SAMPLE_FEATURE]}, limit=500)
        self.assertLessEqual(len(result['properties']), provider.RESULT_LIMIT)

    def test_minimum_age_filters_recent_and_unknown_buildings(self):
        result, _ = self._run(payload={'features': [SAMPLE_FEATURE, NEW_FEATURE, UNKNOWN_AGE_FEATURE]})
        ids = [p['parcel_id'] for p in result['properties']]
        self.assertEqual(ids, ['368390010271'])

    def test_building_age_is_never_presented_as_roof_age(self):
        result, _ = self._run(payload={'features': [SAMPLE_FEATURE]})
        record = result['properties'][0]
        self.assertNotIn('roof', json.dumps(record).lower())

    def test_provider_error_returns_guidance_without_internal_details(self):
        result, _ = self._run(side_effect=OSError('connection refused'))
        self.assertFalse(result['available'])
        self.assertEqual(result['properties'], [])
        self.assertNotIn('http', result['reason'])
        self.assertNotIn('gisdata', result['reason'])

    def test_source_error_payload_returns_guidance(self):
        result, _ = self._run(payload={'error': {'code': 500}})
        self.assertFalse(result['available'])
        self.assertNotIn('http', result['reason'])

    def test_invalid_coordinates_get_actionable_message(self):
        result, _ = self._run(payload={'features': []}, latitude='not-a-number')
        self.assertFalse(result['available'])
        self.assertIn('latitude', result['reason'])


if __name__ == '__main__':
    unittest.main()
