from datetime import date
from engine import calculate

def test_weekdays_and_data():
    w={'hourly':{'time':['2026-10-27T07:00','2026-10-27T08:00','2026-10-27T09:00','2026-10-27T10:00','2026-10-27T11:00'],
       'wind_speed_10m':[2,4,6,8,9],'wind_gusts_10m':[4,7,9,10,11],
       'temperature_2m':[65]*5,'relative_humidity_2m':[65]*5,'cloud_cover':[25]*5,'precipitation_probability':[0]*5}}
    r=calculate(date(2026,10,27),"Port O'Connor",w)
    assert r['score'] is not None
    assert r['coverage_pct'] > 0
    r=calculate(date(2026,10,26),"Port O'Connor",w)
    assert not r['eligible_for_alert']

if __name__=='__main__':
    test_weekdays_and_data()
    print('Checks passed')
