from datetime import date,timedelta,datetime
import streamlit as st
import pandas as pd
from engine import REGIONS,WEIGHTS,calculate
from sources import get_weather,get_tides,approximate_illumination

st.set_page_config(page_title='Sweet Spot | Texas Bay Fishing',page_icon='🎣',layout='wide')
st.title('Sweet Spot')
st.caption('Texas bay fishing opportunity index · 10-day morning outlook · sunrise–11 a.m. · V1 prototype')
st.info('Live weather and NOAA tides are requested by the hosted server. Scores are **provisional model estimates**, not validated fish catch predictions. Missing water temperature/salinity is disclosed, and water clarity is not scored.')
with st.sidebar:
    st.header('Settings')
    st.write('Tuesday–Thursday preferred; Friday capped at 8.5. Monday recovery capped at 7. No Saturday or Sunday fishing recommendations.')
    st.caption('Red tide is not a scored factor. Check local official reports independently when conditions warrant. Marine safety forecasts always take priority.')
    st.markdown('[TPWD red tide information](https://tpwd.texas.gov/landwater/water/environconcerns/hab/redtide/status.phtml)')
    st.caption('Weather: Open-Meteo; tides: NOAA CO-OPS. Forecast scores are experimental.')

@st.cache_data(ttl=3600,show_spinner=False)
def load(name):
    region=REGIONS[name];errors=[];weather={};tides=[];links={}
    try:weather,links['weather']=get_weather(region)
    except Exception as exc:errors.append(f'Weather API: {exc}')
    try:tides,links['tides']=get_tides(region,date.today(),date.today()+timedelta(days=9))
    except Exception as exc:errors.append(f'Tides API: {exc}')
    return weather,tides,links,errors

if st.button('Refresh live forecasts'):
    load.clear()
    st.rerun()

results=[]; links_by_region={}; errors_by_region={}
for name in REGIONS:
    w,t,links,errors=load(name);links_by_region[name]=links;errors_by_region[name]=errors
    for offset in range(10):
        d=date.today()+timedelta(days=offset)
        results.append(calculate(d,name,w,t,approximate_illumination(d)))

st.subheader('10-day comparative outlook')
if any(errors_by_region.values()):
    for name,errors in errors_by_region.items():
        for e in errors:st.warning(f'{name}: {e}')
if all(not load(n)[0] for n in REGIONS):
    st.error('Live weather is unavailable. No invented forecast values are displayed. Check network access and refresh.')

rows=[]
for offset in range(10):
    d=date.today()+timedelta(days=offset)
    row={'Day':d.strftime('%a %b %-d')}
    for name in REGIONS:
        r=next(r for r in results if r['location']==name and r['date']==d.isoformat())
        row[name]='—' if r['score'] is None else f"{r['score']:.1f}"+(' *' if r['coverage_pct']<85 else '')
    rows.append(row)
st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
st.caption('* = less than 85% weighted input coverage. Ratings are experimental estimates; missing factors are not fabricated. NOAA station tide predictions are proxies for back-bay movement.')

st.subheader('Select any day for the explanation')
a,b=st.columns([1,1])
with a:chosen_date=st.selectbox('Date',list(dict.fromkeys(r['date'] for r in results)),format_func=lambda s:datetime.strptime(s,'%Y-%m-%d').strftime('%A, %B %d, %Y'))
with b:chosen_location=st.selectbox('Fishing system',list(REGIONS.keys()))
r=next(x for x in results if x['date']==chosen_date and x['location']==chosen_location)
st.metric('Sweet Spot provisional rating','Unavailable' if r['score'] is None else f"{r['score']:.1f} / 10")
st.write(f"**Day:** {r['weekday']} · **Forecast confidence:** {r['confidence']} · **Input coverage:** {r['coverage_pct']}%")
if r['eligible_for_alert']:st.success('Experimental score meets 8.0 threshold with enough weather/tide coverage. Check marine forecasts and consult a guide before booking.')
elif r['weekday'] in ('Saturday','Sunday'):st.warning('Weekend excluded by personal rule.')
elif r['weekday']=='Monday':st.info('Monday recovery day: never alert eligible.')
else:st.info('Does not currently qualify as a Sweet Spot alert; see data coverage and factor explanations.')
for factor,weight in WEIGHTS.items():
    value=r['factors'].get(factor)
    with st.expander(f"{factor} · {weight:.0%} weight · "+(f'{value:.1f}/10' if value is not None else 'NOT VERIFIED'),expanded=(factor in ('Wind & drift','Tide movement'))):
        st.write(r['reasons'].get(factor,'Not available.'))
for f in r['flags']:st.error(f)
st.markdown('**Data sources for this region:**')
for typ,url in links_by_region[chosen_location].items():st.markdown(f'- [{typ.title()} API response]({url})')

st.caption('Model limitations: morning weather is sampled at 7–11 a.m., not dynamic sunrise; tide score uses selected NOAA station, not measured back-bay current. Lunar illumination is approximate without moon altitude. Water temperature, salinity, and front effects are not yet fully sourced. Water clarity is intentionally not scored. This is an engineering prototype, not a production-calibrated forecast.')
st.divider()
st.subheader('Scoring methodology')
st.write('Provisional weighted average over available factors (not an imputed complete score). Input coverage is displayed. Missing tide data or less than 70% total factor coverage blocks automatic alert eligibility. Strong gusts cap the score at 4. Friday capped at 8.5, Monday at 7, weekends excluded. Red tide is not scored; water clarity is not scored.')
st.write('Existing ChatGPT scheduled alerts are separate from this dashboard. This prototype does **not** send its own notifications or sync settings to the ChatGPT automation.')
