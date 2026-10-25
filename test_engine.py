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


def test_missing_factors_neutral_and_qualification_gates():
    from engine import calculate
    from datetime import date
    hours = [f'2026-10-27T{i:02d}:00' for i in range(7,12)]
    weather = {'hourly': {'time':hours,
        'wind_speed_10m':[2,4,6,9,12],
        'wind_gusts_10m':[4,6,9,13,17],
        'wind_direction_10m':[120]*5,
        'temperature_2m':[72]*5,
        'relative_humidity_2m':[60]*5,
        'cloud_cover':[30]*5,
        'precipitation_probability':[5]*5}}
    r=calculate(date(2026,10,27), "Port O'Connor", weather)
    assert r['coverage_pct'] < 80
    assert r['score'] <= 7.9
    assert not r['eligible_for_alert']


def test_gusts_reduce_wind_score():
    from engine import score_weather
    from datetime import date
    hour=[f'2026-10-27T{i:02d}:00' for i in range(7,12)]
    base={'hourly':{'time':hour,'wind_speed_10m':[2,4,6,9,12],
        'wind_direction_10m':[130]*5,'wind_gusts_10m':[5,7,9,12,14]}}
    harsher={'hourly':dict(base['hourly'],wind_gusts_10m=[20,23,25,27,29])}
    a=score_weather(base,date(2026,10,27))[0]['Wind & drift']
    b=score_weather(harsher,date(2026,10,27))[0]['Wind & drift']
    assert b<a
