"""Sweet Spot V1.4: polished Streamlit UI; unchanged underlying model and APIs."""
from datetime import date, timedelta, datetime
import html
import streamlit as st
from engine import REGIONS, WEIGHTS, calculate
from sources import get_weather, get_tides, approximate_illumination

st.set_page_config(page_title="Sweet Spot | Texas Bay Outlook", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root {--sea:#075a60;--ink:#173943;--mist:#eaf4f2;--sand:#faf8f1}
.stApp {background: #f8faf8;color:#173943} .block-container {max-width:1320px;padding-top:1.4rem;padding-bottom:5rem}
h1,h2,h3 {font-family:'DM Sans',sans-serif!important;letter-spacing:-.035em;color:#173943} p,div,span,button {font-family:'DM Sans',sans-serif}
#MainMenu,footer {visibility:hidden}
.hero {background:linear-gradient(120deg,#0b4c54 0%,#0c7071 68%,#2c9487 100%);border-radius:23px;padding:36px 39px;color:white;margin-bottom:25px;box-shadow:0 14px 36px #075a601e}
.hero .eyebrow {color:#b4e8d9;font-size:12px;font-weight:700;letter-spacing:.2em}.hero h1{color:white!important;font-size:3.3rem;line-height:1.14;margin:6px 0 9px;font-family:'Playfair Display',Georgia,serif!important;letter-spacing:-.02em}.hero p{color:#e3f5f0;font-size:1rem;max-width:700px;margin:0}
.sectionhead{font-size:1.4rem;font-weight:700;color:#173943;margin:25px 0 7px}.muted{color:#69818a;font-size:.88rem}.sectionbar{margin:10px 0 7px;color:#59767b;font-size:.79rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase}
.summary{background:#fff;border:1px solid #e2ebea;border-radius:17px;padding:18px 20px;min-height:118px;box-shadow:0 4px 20px #0e424209}.summary .tiny{font-size:12px;letter-spacing:.07em;font-weight:700;color:#789095;text-transform:uppercase}.summary .large{font-size:1.65rem;font-weight:800;color:#075a60;margin:9px 0 0}.summary .small{font-size:.81rem;color:#59767b}
.details{padding:20px 23px;background:white;border:1px solid #e2ebea;border-radius:17px;margin:10px 0 18px}.details .place{font-size:1.5rem;font-weight:800;color:#153f43}.details .date{font-size:.88rem;color:#678087}.details .score{font-size:3.2rem;font-weight:800;color:#116e5b;line-height:1.15}.details .sub{font-size:13px;color:#648078}
.scorelabel{font-size:.76rem;color:#59767b;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
div[data-testid="stButton"] button {border:1px solid #dce9e5;background:#fff;color:#245057;border-radius:12px;font-weight:700;min-height:39px;box-shadow:none}
div[data-testid="stButton"] button:hover {border-color:#1b7a6c;color:#096c63;background:#eaf4f2}
div[data-testid="stTabs"] button {font-weight:700;font-size:1rem}
[data-testid="stExpander"] {background:#fff;border:1px solid #e4ebea;border-radius:12px;overflow:hidden}
[data-testid="stAlert"] {border-radius:12px}
footer{display:none}
@media(max-width:700px){.hero{padding:23px 20px}.hero h1{font-size:2.4rem}.block-container{padding:1rem}.summary{min-height:96px;padding:14px}.summary .large{font-size:1.25rem}}
</style>''', unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def load(name):
    region = REGIONS[name]; errors=[]; weather={}; tides=[]; links={}
    try: weather,links['weather']=get_weather(region)
    except Exception as exc: errors.append('Weather service: '+str(exc))
    try: tides,links['tides']=get_tides(region,date.today(),date.today()+timedelta(days=9))
    except Exception as exc: errors.append('NOAA tides: '+str(exc))
    return weather,tides,links,errors

st.markdown('''<div class="hero"><div class="eyebrow">THE TEXAS BAY FISHING INDEX</div><h1>Sweet Spot</h1><p>Find your kind of fishing morning. A personalized, 10-day coastal outlook for calm sunrises, moving tides and comfortable days on the bays.</p></div>''',unsafe_allow_html=True)
a,b=st.columns([4,1],vertical_alignment='center')
with a: st.markdown(f'<div class="muted">Forecast issued {date.today():%B %d, %Y} &nbsp; · &nbsp; Sunrise–11 a.m. Central &nbsp; · &nbsp; Live weather + NOAA tide predictions</div>',unsafe_allow_html=True)
with b:
    if st.button('↻ Refresh forecasts',use_container_width=True):
        load.clear();st.rerun()

results=[]; data_links={}; failures={}
with st.spinner('Retrieving coastal conditions…'):
    for name in REGIONS:
        weather,tides,links,errors=load(name);data_links[name]=links;failures[name]=errors
        for i in range(10):
            day=date.today()+timedelta(days=i)
            results.append(calculate(day,name,weather,tides,approximate_illumination(day)))
lookup={(r['date'],r['location']):r for r in results}
upcoming=[r for r in results if r['eligible_for_alert']]
upcoming.sort(key=lambda r:r['score'],reverse=True)
eligible_days=[r for r in results if r['weekday'] in ('Tuesday','Wednesday','Thursday','Friday') and r['score'] is not None]
top=upcoming[0] if upcoming else (max(eligible_days,key=lambda r:r['score']) if eligible_days else None)
regions_ranked=sorted(((name,max((r['score'] for r in results if r['location']==name and r['weekday'] in ('Tuesday','Wednesday','Thursday','Friday') and r['score'] is not None),default=0)) for name in REGIONS),key=lambda x:x[1],reverse=True)
cols=st.columns(3)
with cols[0]:
    headline=f"{top['score']:.1f} / 10" if top else '—'
    sub=(datetime.fromisoformat(top['date']).strftime('%a, %b %d')+' · '+top['location']) if top else 'No scored eligible mornings'
    st.markdown(f'<div class="summary"><div class="tiny">Best upcoming opportunity</div><div class="large">{html.escape(headline)}</div><div class="small">{html.escape(sub)}</div></div>',unsafe_allow_html=True)
with cols[1]:
    st.markdown(f'<div class="summary"><div class="tiny">Strongest bay system</div><div class="large" style="font-size:1.35rem">{html.escape(regions_ranked[0][0])}</div><div class="small">Highest eligible weekday forecast</div></div>',unsafe_allow_html=True)
with cols[2]:
    st.markdown(f'<div class="summary"><div class="tiny">Sweet Spot candidates</div><div class="large">{len(upcoming)}</div><div class="small">8.0+ with minimum input coverage</div></div>',unsafe_allow_html=True)

if any(failures.values()):
    with st.expander('Some data services need attention',expanded=True):
        for name,issues in failures.items():
            for issue in issues:st.warning(f'{name}: {issue}')
st.markdown('<div class="sectionhead">Your 10-day outlook</div><div class="muted">Select any score to open its full explanation below. Gray days are excluded by your personal fishing schedule.</div>',unsafe_allow_html=True)
if 'selected' not in st.session_state:st.session_state.selected=(results[0]['date'],list(REGIONS)[0])

# Native Streamlit buttons ensure selections work without browser scripts.
headers=st.columns([1.15,1.55,1.55,1.55],gap='small')
for col,label in zip(headers,['DAY',"PORT O’CONNOR",'PORT ARANSAS','SOUTH PADRE']):
    with col:st.markdown(f'<div class="scorelabel">{label}</div>',unsafe_allow_html=True)
for offset in range(10):
    dt=date.today()+timedelta(days=offset);dtstr=dt.isoformat();weekend=dt.weekday()>=5
    cols=st.columns([1.15,1.55,1.55,1.55],gap='small',vertical_alignment='center')
    with cols[0]:
        st.markdown(f'<div style="font-weight:750;color:{"#a4acaa" if weekend else "#173943"}">{dt:%a} <span style="font-weight:500">{dt:%b %d}</span></div>',unsafe_allow_html=True)
    for col,name in zip(cols[1:],REGIONS):
        r=lookup[(dtstr,name)];score=r['score'];star=' *' if r['coverage_pct']<85 else ''
        label='Excluded' if weekend else ('No data' if score is None else f"{score:.1f}{star}  {'★' if score>=8 and r['eligible_for_alert'] else '·'}")
        with col:
            if st.button(label,key=f'cell_{dtstr}_{name}',use_container_width=True,type='primary' if st.session_state.selected==(dtstr,name) and not weekend else 'secondary'):
                st.session_state.selected=(dtstr,name)

st.caption('★ Qualified Sweet Spot (subject to marine safety). * Under 85% weighted input coverage. Weekend scores are intentionally hidden; Monday is a recovery day.')
name_tabs=st.tabs(list(REGIONS))
for tab,name in zip(name_tabs,REGIONS):
    with tab:
        region=REGIONS[name]
        st.markdown(f'**{name}** · {region["zones"]}')
        these=[r for r in results if r['location']==name and r['weekday'] in ('Tuesday','Wednesday','Thursday','Friday') and r['score'] is not None]
        if these:
            best=max(these,key=lambda r:r['score'])
            st.markdown(f'Best eligible weekday: **{datetime.fromisoformat(best["date"]):%A, %b %d}** · **{best["score"]:.1f}/10** · {best["confidence"]} confidence')
        else:st.write('No rated eligible mornings available.')

chosen_date,chosen_location=st.session_state.selected
r=lookup[(chosen_date,chosen_location)];dt=datetime.fromisoformat(chosen_date)
st.markdown('<div class="sectionhead">Inside the forecast</div>',unsafe_allow_html=True)
score_str=f"{r['score']:.1f} / 10" if r['score'] is not None else 'Unavailable'
st.markdown(f'<div class="details"><div class="date">{dt:%A, %B %d, %Y} · {html.escape(r["confidence"])} confidence</div><div class="place">{html.escape(chosen_location)}</div><div class="score">{score_str}</div><div class="sub">{r["coverage_pct"]}% of weighted model inputs available · provisional forecast</div></div>',unsafe_allow_html=True)
if r['weekday'] in ('Saturday','Sunday'):st.info('Weekend excluded: this day is not eligible for a fishing recommendation.')
elif r['weekday']=='Monday':st.info('Monday recovery day. Rating capped at 7.0; no alerts.')
elif r['eligible_for_alert']:st.success('Sweet Spot candidate. Review conditions, forecast confidence, and marine safety information before calling a guide.')
else:st.info('Below Sweet Spot alert criteria or insufficient data coverage. This is still a useful morning comparison.')

available=sorted(((k,v) for k,v in r['factors'].items() if v is not None),key=lambda x:x[1],reverse=True)
if available:
    strengths=[k for k,v in available if v>=8]
    weaknesses=[k for k,v in available if v<6]
    st.write(('**In its favor:** '+', '.join(strengths)+'. ') if strengths else '**In its favor:** No high-scoring measured factor yet. ')
    st.write(('**Holding it back:** '+', '.join(weaknesses)+'.') if weaknesses else '**Holding it back:** No individually low-scoring verified factors; review missing inputs and weekday rules.')
st.markdown('<div class="sectionbar">Environmental breakdown</div>',unsafe_allow_html=True)
for factor,weight in WEIGHTS.items():
    value=r['factors'].get(factor)
    label=f'{factor} · {round(weight*100)}% weight · '+(f'{value:.1f}/10' if value is not None else 'not verified')
    with st.expander(label,expanded=factor in ('Wind & drift','Tide movement')):
        if value is not None:st.progress(min(100,max(0,int(value*10))))
        st.write(r['reasons'].get(factor,'No supporting data available.'))
for flag in r['flags']:st.warning(flag)
with st.expander('Data sources and model limitations'):
    for source,url in data_links[chosen_location].items():st.markdown(f'[{source.title()} data request]({url})')
    st.write('Morning weather uses 7–11 a.m. rather than exact sunrise. NOAA station tide movement is a proxy for back-bay circulation, not current velocity. The moonlight score is an experimental phase/cloud proxy without moon elevation. Salinity and water temperature are not yet fully integrated; missing factors remain unscored. Water clarity and red tide are not scored. Ratings are not validated catch predictions.')
st.divider()
st.caption('Sweet Spot V1.4 · Live weather and NOAA predicted tides when available. Ratings use available-factor normalization. Existing ChatGPT alerts are separate from this website. Never substitute this model for marine hazard bulletins.')
