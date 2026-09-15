"""Nearby opportunity scan against the public Dakota County parcel source.

Only allowlisted non-owner fields are returned. Customer-facing messages
never include internal URLs or configuration values. building_age is derived
from year_built only; it is never presented as roof age.
"""
import json
from datetime import datetime, timezone
from urllib import parse as urlparse
from urllib import request as urlrequest

SOURCE_LAYER = 'https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mngeo/plan_parcels_open/FeatureServer/1'
COUNTY = 'Dakota'
RADIUS_KM_MAX = 3.0
DEFAULT_RADIUS_KM = 1.0
DEFAULT_MIN_AGE = 35
RESULT_LIMIT = 20
OVERFETCH = 3
OUT_FIELDS = 'county_pin,co_name,year_built,emv_total,useclass1,acres_poly'
ALLOWLIST = ('parcel_id', 'county', 'year_built', 'building_age',
             'estimated_market_value', 'use_class', 'area_acres', 'source_url')

UNAVAILABLE_MESSAGE = (
    'Nearby property data is temporarily unavailable. '
    'Please try again in a few minutes, or adjust the search radius or minimum building age. '
    'If the problem continues, contact support.'
)
INVALID_LOCATION_MESSAGE = (
    'Enter a valid latitude and longitude to search for nearby properties.'
)


def _unavailable(reason):
    return {'available': False, 'reason': reason, 'properties': []}


def _fetch_json(url, timeout=15):
    with urlrequest.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def _to_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value, default):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _build_query(latitude, longitude, radius_km, fetch_count):
    params = {
        'f': 'json',
        'where': "UPPER(co_name)='" + COUNTY.upper() + "'",
        'geometry': '{},{}'.format(longitude, latitude),
        'geometryType': 'esriGeometryPoint',
        'inSR': '4326',
        'spatialRel': 'esriSpatialRelIntersects',
        'distance': '{}'.format(radius_km),
        'units': 'esriSRUnit_Kilometer',
        'outFields': OUT_FIELDS,
        'returnGeometry': 'false',
        'orderByFields': 'objectid',
        'resultRecordCount': str(fetch_count),
    }
    return SOURCE_LAYER + '/query?' + urlparse.urlencode(params)


def _normalise(attributes, current_year, source_url):
    parcel_id = attributes.get('county_pin')
    if not parcel_id:
        return None
    year_built = attributes.get('year_built')
    if not isinstance(year_built, int) or year_built <= 0 or year_built > current_year:
        year_built = None
    building_age = (current_year - year_built) if year_built else None
    return {
        'parcel_id': str(parcel_id),
        'county': attributes.get('co_name'),
        'year_built': year_built,
        'building_age': building_age,
        'estimated_market_value': attributes.get('emv_total'),
        'use_class': attributes.get('useclass1'),
        'area_acres': attributes.get('acres_poly'),
        'source_url': source_url,
    }


def _persist(records, source_url):
    try:
        from store import save_property
    except Exception:
        return
    for record in records:
        try:
            save_property(record['parcel_id'], record, source_url)
        except Exception:
            continue


def scan_nearby(latitude, longitude, radius_km, minimum_age, limit):
    lat = _to_float(latitude, None)
    lon = _to_float(longitude, None)
    if lat is None or lon is None or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return _unavailable(INVALID_LOCATION_MESSAGE)

    radius = _to_float(radius_km, DEFAULT_RADIUS_KM)
    if radius <= 0:
        radius = DEFAULT_RADIUS_KM
    radius = min(radius, RADIUS_KM_MAX)

    min_age = _to_int(minimum_age, DEFAULT_MIN_AGE)
    if min_age < 0:
        min_age = 0
    limit = _to_int(limit, RESULT_LIMIT)
    limit = max(1, min(limit, RESULT_LIMIT))

    url = _build_query(lat, lon, radius, min(limit * OVERFETCH, 100))
    try:
        payload = _fetch_json(url)
    except Exception:
        return _unavailable(UNAVAILABLE_MESSAGE)
    if not isinstance(payload, dict) or payload.get('error'):
        return _unavailable(UNAVAILABLE_MESSAGE)

    current_year = datetime.now(timezone.utc).year
    properties = []
    for feature in payload.get('features') or []:
        record = _normalise((feature or {}).get('attributes') or {}, current_year, url)
        if record is None:
            continue
        if record['building_age'] is None or record['building_age'] < min_age:
            continue
        properties.append(record)
        if len(properties) >= limit:
            break

    _persist(properties, url)
    return {
        'available': True,
        'reason': None,
        'radius_km': radius,
        'minimum_age': min_age,
        'properties': properties,
    }
