"""External data adapters. Failed requests are clearly reported, never replaced with invented data."""
import requests
from datetime import date, timedelta
from math import cos, pi

SESSION=requests.Session()
SESSION.headers['User-Agent']='SweetSpotV1/0.1 (personal non-commercial fishing planner)'

def get_weather(region):
    params={'latitude':region['lat'],'longitude':region['lon'],'forecast_days':10,'timezone':'America/Chicago',
            'temperature_unit':'fahrenheit','wind_speed_unit':'mph',
            'hourly':','.join(['temperature_2m','relative_humidity_2m','cloud_cover','precipitation','precipitation_probability','wind_speed_10m','wind_gusts_10m'])}
    r=SESSION.get('https://api.open-meteo.com/v1/forecast',params=params,timeout=18);r.raise_for_status()
    return r.json(),r.url

def get_tides(region,begin,end):
    params={'begin_date':begin.strftime('%Y%m%d'),'end_date':end.strftime('%Y%m%d'),'station':region['station'],
            'product':'predictions','datum':'MLLW','time_zone':'lst_ldt','units':'english','interval':'h','format':'json','application':'SweetSpot'}
    r=SESSION.get('https://api.tidesandcurrents.noaa.gov/api/prod/datagetter',params=params,timeout=18);r.raise_for_status()
    payload=r.json()
    if 'error' in payload:raise ValueError(str(payload['error']))
    return payload.get('predictions',[]),r.url

def approximate_illumination(day):
    # Approximate lunar fraction from synodic cycle. Moonrise/set NOT represented.
    age=((day-date(2000,1,6)).days % 29.530588853)
    return (1-cos(2*pi*age/29.530588853))/2

RED_TIDE_URL='https://tpwd.texas.gov/landwater/water/environconcerns/hab/redtide/status.phtml'
NOAA_HAB_URL='https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/gulf-coast/'
