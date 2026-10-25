"""External data adapters for Putey's Bay Fishing Outlook."""
import requests
from datetime import date
from math import cos, pi

SESSION = requests.Session()
SESSION.headers['User-Agent'] = 'PuteysBayFishingOutlook/1.5 (personal non-commercial fishing planner)'


def get_weather(region):
    params = {
        'latitude': region['lat'],
        'longitude': region['lon'],
        'forecast_days': 10,
        'timezone': 'America/Chicago',
        'temperature_unit': 'fahrenheit',
        'wind_speed_unit': 'mph',
        'hourly': ','.join([
            'temperature_2m', 'relative_humidity_2m', 'cloud_cover', 'precipitation',
            'precipitation_probability', 'wind_speed_10m', 'wind_gusts_10m'
        ]),
        'daily': ','.join([
            'temperature_2m_max', 'temperature_2m_min', 'sunrise', 'sunset'
        ]),
    }
    r = SESSION.get('https://api.open-meteo.com/v1/forecast', params=params, timeout=20)
    r.raise_for_status()
    return r.json(), r.url


def get_marine(region):
    params = {
        'latitude': region['lat'],
        'longitude': region['lon'],
        'forecast_days': 10,
        'timezone': 'America/Chicago',
        'temperature_unit': 'fahrenheit',
        'hourly': 'sea_surface_temperature',
    }
    r = SESSION.get('https://marine-api.open-meteo.com/v1/marine', params=params, timeout=20)
    r.raise_for_status()
    return r.json(), r.url


def get_tides(region, begin, end):
    params = {
        'begin_date': begin.strftime('%Y%m%d'),
        'end_date': end.strftime('%Y%m%d'),
        'station': region['station'],
        'product': 'predictions',
        'datum': 'MLLW',
        'time_zone': 'lst_ldt',
        'units': 'english',
        'interval': 'h',
        'format': 'json',
        'application': 'PuteysBayFishingOutlook',
    }
    r = SESSION.get('https://api.tidesandcurrents.noaa.gov/api/prod/datagetter', params=params, timeout=20)
    r.raise_for_status()
    payload = r.json()
    if 'error' in payload:
        raise ValueError(str(payload['error']))
    return payload.get('predictions', []), r.url


def approximate_illumination(day):
    age = ((day - date(2000, 1, 6)).days % 29.530588853)
    return (1 - cos(2 * pi * age / 29.530588853)) / 2


def moon_phase_name(day):
    age = ((day - date(2000, 1, 6)).days % 29.530588853)
    phases = [
        (1.84566, 'Waxing Crescent'),
        (5.53699, 'First Quarter'),
        (9.22831, 'Waxing Gibbous'),
        (12.91963, 'Full Moon'),
        (16.61096, 'Waning Gibbous'),
        (20.30228, 'Last Quarter'),
        (23.99361, 'Waning Crescent'),
        (27.68493, 'New Moon'),
        (29.53059, 'Waxing Crescent'),
    ]
    if age < 1.0:
        return 'New Moon'
    for threshold, name in phases:
        if age < threshold:
            return name
    return 'New Moon'
