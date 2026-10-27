"""Putey's Bay Fishing Outlook V1.5 with daily conditions panel."""
from datetime import date, timedelta, datetime
import html
import base64
import json
from pathlib import Path
import streamlit as st
from engine import REGIONS, WEIGHTS, calculate
from sources import get_weather, get_tides, get_marine, approximate_illumination, moon_phase_name

APP_VERSION = "2.5 FAVORITES + SPONSOR"
BUILD_ID = "2026-10-25-v25"

st.set_page_config(page_title="Putey's Bay Fishing Outlook", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")
ASSETS = Path(__file__).parent / "assets"


st.markdown(
    '''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');
:root {--sea:#0a5a5f;--sea2:#0a7a78;--ink:#173943;--mist:#eaf4f2;--sand:#faf8f1;--panel:#ffffff;--line:#e2ebea;--muted:#6c848b;--gold:#c7a85d}
html, body, [class*="css"]  {font-family:'DM Sans',sans-serif;}
.stApp {background:#f8faf8;color:var(--ink)}
.block-container {max-width:1320px;padding-top:1.25rem;padding-bottom:5rem}
h1,h2,h3 {letter-spacing:-.035em;color:var(--ink)}
#MainMenu, footer {visibility:hidden}
.hero {background:linear-gradient(120deg,#0b4c54 0%,#0c7071 68%,#2c9487 100%);border-radius:24px;padding:38px 40px;color:white;margin-bottom:24px;box-shadow:0 14px 36px #075a601e}
.hero .eyebrow {color:#b4e8d9;font-size:12px;font-weight:800;letter-spacing:.2em;text-transform:uppercase}
.hero h1 {color:white!important;font-size:3.2rem;line-height:1.1;margin:10px 0 10px;font-family:'Playfair Display',Georgia,serif!important;letter-spacing:-.02em}
.hero p {color:#e3f5f0;font-size:1rem;max-width:760px;margin:0}
.sectionhead{font-size:1.45rem;font-weight:800;color:var(--ink);margin:25px 0 7px}
.muted{color:var(--muted);font-size:.88rem}
.sectionbar{margin:16px 0 8px;color:#59767b;font-size:.79rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase}
.summary{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px 20px;min-height:118px;box-shadow:0 4px 20px #0e424209}
.summary .tiny{font-size:12px;letter-spacing:.07em;font-weight:800;color:#789095;text-transform:uppercase}
.summary .large{font-size:1.65rem;font-weight:800;color:var(--sea);margin:9px 0 0}
.summary .small{font-size:.82rem;color:#59767b}
.details{padding:22px 24px;background:#fff;border:1px solid var(--line);border-radius:18px;margin:10px 0 12px}
.details .place{font-size:1.6rem;font-weight:800;color:#153f43}.details .date{font-size:.9rem;color:#678087}.details .score{font-size:3.3rem;font-weight:800;color:#116e5b;line-height:1.05}.details .sub{font-size:13px;color:#648078}
.scorelabel{font-size:.76rem;color:#59767b;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.metric-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 16px;min-height:110px;box-shadow:0 4px 16px rgba(10,73,82,.05)}
.metric-card .label{font-size:.73rem;font-weight:800;letter-spacing:.10em;color:#6c848b;text-transform:uppercase;margin-bottom:6px}
.metric-card .value{font-size:1.5rem;font-weight:800;color:#163c43;line-height:1.2}
.metric-card .sub{font-size:.82rem;color:#667e84;margin-top:4px}
.moonchip{display:inline-flex;align-items:center;gap:.45rem;background:#f4f7f7;border:1px solid var(--line);padding:.35rem .6rem;border-radius:999px;font-size:.85rem;font-weight:700;color:#36545b}
.moonicon{font-size:1.2rem}
.quicknote{background:#edf5ff;border:1px solid #dce7f4;color:#365b75;padding:12px 14px;border-radius:12px;font-size:.94rem}
div[data-testid="stButton"] button {border:1px solid #dce9e5;background:#fff;color:#245057;border-radius:12px;font-weight:700;min-height:39px;box-shadow:none}
div[data-testid="stButton"] button:hover {border-color:#1b7a6c;color:#096c63;background:#eaf4f2}
div[data-testid="stTabs"] button {font-weight:700;font-size:1rem}
[data-testid="stExpander"] {background:#fff;border:1px solid #e4ebea;border-radius:12px;overflow:hidden}
[data-testid="stAlert"] {border-radius:12px}
.smallbadge{display:inline-block;padding:.24rem .55rem;border-radius:999px;background:#eef6f5;border:1px solid #dbe9e7;color:#2f5c62;font-size:.82rem;font-weight:700}
footer{display:none}
/* Responsive forecast: desktop comparisons stay intact; phone gets a dedicated single-region view. */
.st-key-mobile_scoreboard {display:none}
@media(max-width:700px){
 .st-key-desktop_scoreboard{display:none!important}
 .st-key-mobile_scoreboard{display:block!important}
 .block-container{padding:0.65rem 0.8rem 3rem!important;max-width:100vw!important}
 .hero{padding:25px 20px!important;min-height:270px!important;border-radius:15px!important;background-position:65% 52%!important}
 .hero h1{font-size:clamp(1.65rem,7.5vw,2.2rem)!important;max-width:260px!important;line-height:1.08!important}
 .hero p{font-size:.85rem!important;max-width:225px!important}
 .hero .eyebrow{font-size:.62rem!important;max-width:240px}
 .summary{min-height:88px;padding:12px 14px;margin-bottom:2px}
 .summary .large{font-size:1.25rem!important}
 .summary .tiny{font-size:.65rem}
 .sectionhead{font-size:1.2rem}
 .metric-card{min-height:80px;padding:12px}
 .metric-card .value{font-size:1.18rem}
 .details{padding:16px}
 .details .place{font-size:1.28rem}
 .details .score{font-size:2.5rem}
 .st-key-mobile_scoreboard [data-testid="stSelectbox"]{width:100%}
 .st-key-mobile_scoreboard [data-testid="stButton"] button{min-height:51px!important;text-align:left!important;justify-content:flex-start!important;padding:11px 14px!important;font-size:1rem!important;border-radius:10px!important}
 .st-key-mobile_scoreboard [data-testid="stButton"] button p{text-align:left!important;width:100%!important;font-weight:750!important}
}
</style>''',
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load(name):
    region = REGIONS[name]
    errors = []
    weather, tides, marine = {}, [], {}
    links = {}
    try:
        weather, links['weather'] = get_weather(region)
    except Exception as exc:
        errors.append('Weather service: ' + str(exc))
    try:
        tides, links['tides'] = get_tides(region, date.today(), date.today() + timedelta(days=9))
    except Exception as exc:
        errors.append('NOAA tides: ' + str(exc))
    try:
        marine, links['marine'] = get_marine(region)
    except Exception as exc:
        errors.append('Marine water temperature: ' + str(exc))
    return weather, tides, marine, links, errors


def find_daily_index(weather, day):
    daily = weather.get('daily', {}) if weather else {}
    times = daily.get('time', [])
    day_str = day.isoformat()
    for i, t in enumerate(times):
        if t == day_str:
            return i
    return None


def fmt_time(value):
    if not value:
        return '—'
    try:
        return datetime.fromisoformat(value).strftime('%-I:%M %p')
    except Exception:
        try:
            return datetime.fromisoformat(value.replace('Z', '')).strftime('%-I:%M %p')
        except Exception:
            return '—'


def daily_air(weather, day):
    idx = find_daily_index(weather, day)
    daily = weather.get('daily', {}) if weather else {}
    if idx is None:
        return None, None, None, None
    hi = daily.get('temperature_2m_max', [None])[idx]
    lo = daily.get('temperature_2m_min', [None])[idx]
    sunrise = daily.get('sunrise', [None])[idx]
    sunset = daily.get('sunset', [None])[idx]
    return hi, lo, sunrise, sunset


def water_temp_for_day(marine, day):
    hourly = marine.get('hourly', {}) if marine else {}
    times = hourly.get('time', [])
    temps = hourly.get('sea_surface_temperature', [])
    vals = []
    for t, temp in zip(times, temps):
        if t[:10] == day.isoformat() and 7 <= int(t[11:13]) <= 11 and temp is not None:
            vals.append(float(temp))
    if vals:
        return round(sum(vals) / len(vals), 1)
    for t, temp in zip(times, temps):
        if t[:10] == day.isoformat() and temp is not None:
            return round(float(temp), 1)
    return None


def moon_icon(name):
    return {
        'New Moon': '🌑', 'Waxing Crescent': '🌒', 'First Quarter': '🌓', 'Waxing Gibbous': '🌔',
        'Full Moon': '🌕', 'Waning Gibbous': '🌖', 'Last Quarter': '🌗', 'Waning Crescent': '🌘',
    }.get(name, '🌙')


# The illustrated banner is an authored asset (including its title lettering).
# A second option uses the family's original photo, with real HTML heading text.
st.markdown(f'<div style="font-size:14px;font-weight:800;letter-spacing:.07em;color:#156e70;padding:8px 0">PUTEY’S BAY FISHING OUTLOOK • V{APP_VERSION} • BUILD {BUILD_ID}</div>', unsafe_allow_html=True)

# Genuine unaltered photograph supplied by the family, with only a subtle text-legibility overlay.
photo = base64.b64encode((ASSETS / 'hero_personal.jpg').read_bytes()).decode('ascii')
st.markdown(
    """<div class="hero" style="min-height:285px;background:linear-gradient(90deg,rgba(2,27,40,.66),rgba(4,39,51,.24) 48%,rgba(4,39,51,.02)), url(data:image/jpeg;base64,"""
    + photo
    + """) center 51%/cover;"><h1>Putey's Bay Fishing Outlook</h1></div>""",
    unsafe_allow_html=True,
)


left, right = st.columns([4, 1], vertical_alignment='center')
with left:
    st.markdown(
        f'<div class="muted">Forecast issued {date.today():%B %d, %Y} &nbsp; · &nbsp; Sunrise–11 a.m. Central &nbsp; · &nbsp; Live weather + NOAA tide predictions</div>',
        unsafe_allow_html=True,
    )
with right:
    if st.button('↻ Refresh forecasts', use_container_width=True):
        load.clear()
        st.rerun()

results = []
data_links = {}
failures = {}
raw_sources = {}
with st.spinner('Retrieving coastal conditions…'):
    for name in REGIONS:
        weather, tides, marine, links, errors = load(name)
        data_links[name] = links
        failures[name] = errors
        raw_sources[name] = {'weather': weather, 'tides': tides, 'marine': marine}
        for i in range(10):
            day = date.today() + timedelta(days=i)
            wt = water_temp_for_day(marine, day)
            results.append(calculate(day, name, weather, tides, approximate_illumination(day), wt))

lookup = {(r['date'], r['location']): r for r in results}
upcoming = [r for r in results if r['eligible_for_alert']]
upcoming.sort(key=lambda r: r['score'], reverse=True)
eligible_days = [r for r in results if r['weekday'] in ('Tuesday', 'Wednesday', 'Thursday', 'Friday') and r['score'] is not None]
top = upcoming[0] if upcoming else (max(eligible_days, key=lambda r: r['score']) if eligible_days else None)
regions_ranked = sorted(
    (
        (name, max((r['score'] for r in results if r['location'] == name and r['weekday'] in ('Tuesday', 'Wednesday', 'Thursday', 'Friday') and r['score'] is not None), default=0))
        for name in REGIONS
    ),
    key=lambda x: x[1],
    reverse=True,
)

cols = st.columns(3)
with cols[0]:
    headline = f"{top['score']:.1f} / 10" if top else '—'
    sub = (datetime.fromisoformat(top['date']).strftime('%a, %b %d') + ' · ' + top['location']) if top else 'No scored eligible mornings'
    st.markdown(f'<div class="summary"><div class="tiny">Best upcoming opportunity</div><div class="large">{html.escape(headline)}</div><div class="small">{html.escape(sub)}</div></div>', unsafe_allow_html=True)
with cols[1]:
    st.markdown(f'<div class="summary"><div class="tiny">Strongest bay system</div><div class="large" style="font-size:1.35rem">{html.escape(regions_ranked[0][0])}</div><div class="small">Highest eligible weekday forecast</div></div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown(f'<div class="summary"><div class="tiny">Sweet Spot candidates</div><div class="large">{len(upcoming)}</div><div class="small">8.0+ with minimum input coverage</div></div>', unsafe_allow_html=True)

if any(failures.values()):
    with st.expander('Some data services need attention', expanded=False):
        for name, issues in failures.items():
            for issue in issues:
                st.warning(f'{name}: {issue}')

LOCATION_COLORS = {
    "Port O'Connor": ('#156e70', '#e6f2f1'),
    'Port Aransas': ('#b46d35', '#fcf1e8'),
    'South Padre Island': ('#456aa1', '#eaf1fc'),
}
st.markdown('''<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;margin-bottom:2px">
<span style="padding:7px 12px;background:#e6f2f1;color:#156e70;border-left:4px solid #156e70;border-radius:8px;font-weight:700;font-size:.8rem">Port O'Connor</span>
<span style="padding:7px 12px;background:#fcf1e8;color:#a45c27;border-left:4px solid #b46d35;border-radius:8px;font-weight:700;font-size:.8rem">Port Aransas</span>
<span style="padding:7px 12px;background:#eaf1fc;color:#456aa1;border-left:4px solid #456aa1;border-radius:8px;font-weight:700;font-size:.8rem">South Padre Island</span></div>''', unsafe_allow_html=True)

st.markdown('<div class="sectionhead">Your 10-day outlook</div><div class="muted">Select any score to open its full explanation below. Gray days are excluded by your personal fishing schedule.</div>', unsafe_allow_html=True)
if 'selected' not in st.session_state:
    st.session_state.selected = (results[0]['date'], list(REGIONS)[0])

with st.container(key="desktop_scoreboard"):
    headers = st.columns([1.15, 1.55, 1.55, 1.55], gap='small')
    for col, label in zip(headers, ['DAY', "PORT O’CONNOR", 'PORT ARANSAS', 'SOUTH PADRE']):
        with col:
            st.markdown(f'<div class="scorelabel">{label}</div>', unsafe_allow_html=True)

    for offset in range(10):
        dt = date.today() + timedelta(days=offset)
        dtstr = dt.isoformat()
        weekend = dt.weekday() >= 5
        cols = st.columns([1.15, 1.55, 1.55, 1.55], gap='small', vertical_alignment='center')
        with cols[0]:
            st.markdown(
                f'<div style="font-weight:750;color:{"#a4acaa" if weekend else "#173943"}">{dt:%a} <span style="font-weight:500">{dt:%b %d}</span></div>',
                unsafe_allow_html=True,
            )
        for col, name in zip(cols[1:], REGIONS):
            r = lookup[(dtstr, name)]
            score = r['score']
            star = ' *' if r['coverage_pct'] < 85 else ''
            label = 'Excluded' if weekend else ('No data' if score is None else f"{score:.1f}{star}  {'★' if r['eligible_for_alert'] else '·'}")
            with col:
                btn_type = 'primary' if st.session_state.selected == (dtstr, name) and not weekend else 'secondary'
                if st.button(label, key=f'cell_{dtstr}_{name}', use_container_width=True, type=btn_type):
                    st.session_state.selected = (dtstr, name)

# A compact score view specifically for narrow portrait screens.
# The desktop comparison remains available and unmodified on larger devices.
with st.container(key="mobile_scoreboard"):
    st.markdown('**Phone-friendly daily scores**')
    mobile_region = st.selectbox('Fishing region', list(REGIONS), key='mobile_region', on_change=lambda: st.session_state.update(selected=(st.session_state.get('mobile_day',date.today()).isoformat(),st.session_state.mobile_region)))
    st.caption('Tap a day to see its detailed forecast below.')
    for offset in range(10):
        mobile_day = date.today() + timedelta(days=offset)
        mobile_dtstr = mobile_day.isoformat()
        mobile_r = lookup[(mobile_dtstr, mobile_region)]
        excluded = mobile_day.weekday() >= 5
        mobile_score = 'Excluded' if excluded else ('No data' if mobile_r['score'] is None else f"{mobile_r['score']:.1f} / 10")
        tag = ' ★' if mobile_r['eligible_for_alert'] else ''
        label = f"{mobile_day:%a, %b %d}    ·    {mobile_score}{tag}"
        selected_mobile = st.session_state.selected == (mobile_dtstr, mobile_region)
        if st.button(label, key=f'mobile_day_{mobile_dtstr}_{mobile_region}', use_container_width=True,
                     type='primary' if selected_mobile else 'secondary'):
            st.session_state.selected = (mobile_dtstr, mobile_region)

st.caption('★ Qualified opportunity (subject to marine safety). * Under 85% weighted input coverage. Weekend scores are intentionally hidden; Monday is a recovery day.')
name_tabs = st.tabs(list(REGIONS))
for tab, name in zip(name_tabs, REGIONS):
    with tab:
        region = REGIONS[name]
        st.markdown(f'**{name}** · {region["zones"]}')
        these = [r for r in results if r['location'] == name and r['weekday'] in ('Tuesday', 'Wednesday', 'Thursday', 'Friday') and r['score'] is not None]
        if these:
            best = max(these, key=lambda r: r['score'])
            st.markdown(f'Best eligible weekday: **{datetime.fromisoformat(best["date"]):%A, %b %d}** · **{best["score"]:.1f}/10** · {best["confidence"]} confidence')
        else:
            st.write('No rated eligible mornings available.')

chosen_date, chosen_location = st.session_state.selected
r = lookup[(chosen_date, chosen_location)]
dt = datetime.fromisoformat(chosen_date)
weather = raw_sources[chosen_location]['weather']
marine = raw_sources[chosen_location]['marine']
hi, lo, sunrise, sunset = daily_air(weather, dt.date())
water_temp = water_temp_for_day(marine, dt.date())
phase = moon_phase_name(dt.date())
illum = round(approximate_illumination(dt.date()) * 100)

st.markdown('<div class="sectionhead">Inside the forecast</div>', unsafe_allow_html=True)
score_str = f"{r['score']:.1f} / 10" if r['score'] is not None else 'Unavailable'
st.markdown(
    f'<div class="details"><div class="date">{dt:%A, %B %d, %Y} · {html.escape(r["confidence"])} confidence</div><div class="place">{html.escape(chosen_location)}</div><div class="score">{score_str}</div><div class="sub">{r["coverage_pct"]}% of weighted model inputs available · provisional forecast</div></div>',
    unsafe_allow_html=True,
)

# Daily conditions strip
st.markdown('<div class="sectionbar">Daily conditions snapshot</div>', unsafe_allow_html=True)
card_cols = st.columns(5, gap='small')
with card_cols[0]:
    st.markdown(f'<div class="metric-card"><div class="label">Sunrise</div><div class="value">{fmt_time(sunrise)}</div><div class="sub">Local time</div></div>', unsafe_allow_html=True)
with card_cols[1]:
    st.markdown(f'<div class="metric-card"><div class="label">Sunset</div><div class="value">{fmt_time(sunset)}</div><div class="sub">Local time</div></div>', unsafe_allow_html=True)
with card_cols[2]:
    temp_str = (f'{round(hi):.0f}° / {round(lo):.0f}°F' if hi is not None and lo is not None else '—')
    st.markdown(f'<div class="metric-card"><div class="label">Air high / low</div><div class="value">{temp_str}</div><div class="sub">Daily forecast</div></div>', unsafe_allow_html=True)
with card_cols[3]:
    wt_str = f'{water_temp:.1f}°F' if water_temp is not None else 'Pending'
    wt_sub = 'Marine forecast' if water_temp is not None else 'Not currently available'
    st.markdown(f'<div class="metric-card"><div class="label">Water temperature</div><div class="value">{wt_str}</div><div class="sub">{wt_sub}</div></div>', unsafe_allow_html=True)
with card_cols[4]:
    st.markdown(f'<div class="metric-card"><div class="label">Moon phase</div><div class="value"><span class="moonicon">{moon_icon(phase)}</span> {phase}</div><div class="sub">Approx. illumination {illum}%</div></div>', unsafe_allow_html=True)

if r['weekday'] in ('Saturday', 'Sunday'):
    st.info('Weekend excluded: this day is not eligible for a fishing recommendation.')
elif r['weekday'] == 'Monday':
    st.info('Monday recovery day. Rating capped at 7.0; no alerts.')
elif r['eligible_for_alert']:
    st.success('Strong opportunity. Review conditions, forecast confidence, and marine safety information before calling a guide.')
else:
    st.markdown('<div class="quicknote">Below Sweet Spot alert criteria or insufficient data coverage. This is still a useful morning comparison.</div>', unsafe_allow_html=True)

available = sorted(((k, v) for k, v in r['factors'].items() if v is not None), key=lambda x: x[1], reverse=True)
if available:
    strengths = [k for k, v in available if v >= 8]
    weaknesses = [k for k, v in available if v < 6]
    st.write(('**In its favor:** ' + ', '.join(strengths) + '. ') if strengths else '**In its favor:** No high-scoring measured factor yet. ')
    st.write(('**Holding it back:** ' + ', '.join(weaknesses) + '.') if weaknesses else '**Holding it back:** No individually low-scoring verified factors; review missing inputs and weekday rules.')

st.markdown('<div class="sectionbar">Environmental breakdown</div>', unsafe_allow_html=True)
for factor, weight in WEIGHTS.items():
    value = r['factors'].get(factor)
    label = f'{factor} · {round(weight*100)}% weight · ' + (f'{value:.1f}/10' if value is not None else 'not verified')
    with st.expander(label, expanded=factor in ('Wind & drift', 'Tide movement')):
        if value is not None:
            st.progress(min(100, max(0, int(value * 10))))
        st.write(r['reasons'].get(factor, 'No supporting data available.'))

for flag in r['flags']:
    st.warning(flag)

with st.expander('Data sources and model limitations'):
    for source, url in data_links[chosen_location].items():
        st.markdown(f'[{source.title()} data request]({url})')
    st.write(
        'Morning weather uses 7–11 a.m. rather than exact sunrise. NOAA station tide movement is a proxy for back-bay circulation, not current velocity. '
        'The moonlight score is an experimental phase/cloud proxy without moon elevation. Water temperature is shown using near-coast marine guidance when available. '
        'Salinity, water clarity, and red tide are not scored. Ratings are not validated catch predictions. Regional wind direction is a proxy, not location-specific fetch modeling.'
    )

# Favorite data lives in a small JSON file editable through GitHub's pencil icon.
try:
    favorites = json.loads((Path(__file__).parent / 'favorites.json').read_text(encoding='utf-8'))
except (OSError, ValueError):
    favorites = {}

st.markdown('<div class="sectionhead">My coastal favorites</div>', unsafe_allow_html=True)
st.caption('Guides, lodging and restaurants organized by fishing destination.')
BANNER_FILES = {
    "Port O'Connor": None,
    'Port Aransas': 'port_aransas_real.png',
    'South Padre Island': 'south_padre_real.png',
}
GROUP_NAMES = [('guides', 'Fishing guides'), ('lodging', 'Lodging'), ('restaurants', 'Restaurants')]
for favorite_name, (accent, background) in LOCATION_COLORS.items():
    banner_name = BANNER_FILES.get(favorite_name)
    banner_file = (ASSETS / banner_name) if banner_name else None
    encoded = base64.b64encode(banner_file.read_bytes()).decode('ascii') if banner_file and banner_file.exists() else ''
    bgstyle = (
        f'background-image:linear-gradient(90deg,rgba(5,36,43,.78),rgba(5,36,43,.18)),url(data:image/png;base64,{encoded});background-position:center;background-size:cover;'
        if encoded else f'background:linear-gradient(120deg,{accent},#7faeb0);'
    )
    st.markdown(
        '<div style="height:118px;border-radius:15px;margin:24px 0 10px;'
        f'{bgstyle}'
        'display:flex;align-items:end;padding:18px 22px;">'
        f'<div style="font-family:Georgia,serif;font-size:1.65rem;font-weight:700;color:white">{html.escape(favorite_name)}</div>'
        '</div>',unsafe_allow_html=True)
    groups = favorites.get(favorite_name, {})
    cols = st.columns(3, gap='medium')
    for col,(key,title) in zip(cols,GROUP_NAMES):
        with col:
            st.markdown(f'<div style="font-weight:800;color:{accent};margin:.25rem 0 .45rem">{title}</div>',unsafe_allow_html=True)
            entries = groups.get(key, [])
            if not entries:
                st.caption('Add a favorite when ready.')
            for entry in entries:
                label=html.escape(str(entry.get('name','Favorite')))
                desc=html.escape(str(entry.get('description','')))
                url=str(entry.get('url',''))
                if url.startswith(('https://','http://')):
                    st.markdown(f'**[{label}]({url})**')
                else:
                    st.markdown(f'**{label}**')
                if desc:
                    st.caption(desc)

# Seasonal species are reference information, not automatic catch predictions.
st.markdown('<div class="sectionhead">Texas Gulf fishing seasons</div>', unsafe_allow_html=True)
st.caption('Seasonal patterns are approximate and not fishing regulations.')
seasonal = [
    ('Bull redfish run', 'bull_redfish.png', 'September–October', 'Fall concentrations of mature red drum near passes and Gulf-facing shorelines.', 'https://tpwd.texas.gov/huntwild/wild/species/reddrum/'),
    ('Redfish', 'redfish.png', 'Year-round', 'Inshore red drum are available throughout the year; shallow-water patterns often shine in spring and fall.', 'https://tpwd.texas.gov/huntwild/wild/species/reddrum/'),
    ('Speckled trout', 'trout.png', 'Spring–fall', 'Shallow grass-bed opportunities in warmer weather; fish shift habitat as temperatures change.', 'https://tpwd.texas.gov/huntwild/wild/species/strout/'),
    ('Southern flounder', 'flounder.png', 'October–December', 'Autumn migration from bays toward passes and Gulf waters. Check current seasonal harvest rules.', 'https://tpwd.texas.gov/huntwild/wild/species/flounder/'),
    ('Tarpon', 'tarpon.png', 'Summer–early fall', 'Warm-season Gulf Coast migratory opportunities, especially near passes and coastal waters.', 'https://tpwd.texas.gov/huntwild/wild/species/tarpon/'),
    ('Snook', None, 'Spring–fall', 'Warm-water inshore opportunities around the Lower Laguna Madre and South Texas coast.', 'https://tpwd.texas.gov/huntwild/wild/species/snook/'),
]
for row_start in range(0, len(seasonal), 3):
    season_cols = st.columns(3, gap='small')
    for column, (species, filename, season, description, url) in zip(season_cols, seasonal[row_start:row_start+3]):
        with column:
            with st.container(border=True):
                if filename and (ASSETS / filename).exists():
                    st.image(str(ASSETS / filename), use_container_width=True)
                st.markdown(f'**{species}**')
                st.caption(season)
                st.caption(description)
                st.markdown(f'[Species details ↗]({url})')

st.markdown('<div class="sectionhead">Sponsored by</div>', unsafe_allow_html=True)
if (ASSETS / 'ortizowitz_farms.png').exists():
    st.image(str(ASSETS / 'ortizowitz_farms.png'), width=360)

st.divider()
st.caption("Putey's Bay Fishing Outlook V2.5 · Live weather, marine temperature guidance, and NOAA predicted tides when available. Missing components receive a neutral 5/10 provisional contribution; an 8+ alert requires wind, tide, ecosystem, and data coverage gates. Existing ChatGPT alerts are separate from this website. Never substitute this model for marine hazard bulletins.")
