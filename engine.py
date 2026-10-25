"""Putey's Bay Fishing Outlook V1.5: transparent coastal fishing decision rules."""
from datetime import date, datetime, timedelta
from statistics import mean
from math import atan2, cos, sin, radians, degrees

WEIGHTS = {
    'Wind & drift': .20,
    'Tide movement': .20,
    'Ecosystem stability': .15,
    'Air comfort': .15,
    'Water temperature': .10,
    'Sky & sunrise': .10,
    'Prior-night moonlight': .10,
}

REGIONS = {
    "Port O'Connor": {
        'lat': 28.446,
        'lon': -96.405,
        'station': '8773701',
        'reference_range_ft': .69,
        'zones': 'Espiritu Santo / San Antonio / Matagorda bays',
    },
    'Port Aransas': {
        'lat': 27.833,
        'lon': -97.061,
        'station': '8775237',
        'reference_range_ft': .90,
        'zones': 'Redfish / Aransas bays',
    },
    'South Padre Island': {
        'lat': 26.075,
        'lon': -97.165,
        'station': '8779770',
        'reference_range_ft': 1.0,
        'zones': 'Lower Laguna Madre / South Bay',
    },
}


def clamp(v, lo=0.0, hi=10.0):
    return max(lo, min(hi, float(v)))


def value_at(hourly, key, idx, default=None):
    try:
        return hourly[key][idx] if hourly[key][idx] is not None else default
    except (KeyError, IndexError, TypeError):
        return default


def morning_items(weather, day):
    hourly = weather.get('hourly', {})
    return [
        i for i, t in enumerate(hourly.get('time', []))
        if t[:10] == day.isoformat() and 7 <= int(t[11:13]) <= 11
    ]


def previous_night_items(weather, day):
    hourly = weather.get('hourly', {})
    yesterday = (day - timedelta(days=1)).isoformat()
    return [
        i for i, t in enumerate(hourly.get('time', []))
        if (t[:10] == yesterday and int(t[11:13]) >= 20)
        or (t[:10] == day.isoformat() and int(t[11:13]) <= 5)
    ]


def score_weather(weather, day, lunar_illumination=None, water_temp_f=None):
    h = weather.get('hourly', {})
    indexes = morning_items(weather, day)
    if not indexes:
        return {}, {}, ['Missing hourly morning weather data']

    def avg(key):
        vals = [float(x) for i in indexes if (x := value_at(h, key, i)) is not None]
        return mean(vals) if vals else None

    wind = avg('wind_speed_10m')
    gust = avg('wind_gusts_10m')
    temp = avg('temperature_2m')
    humidity = avg('relative_humidity_2m')
    cloud = avg('cloud_cover')
    rain = avg('precipitation_probability')
    first = value_at(h, 'wind_speed_10m', indexes[0])
    last = value_at(h, 'wind_speed_10m', indexes[-1])

    scores, descriptions, flags = {}, {}, []

    if wind is not None:
        def hourly_score(speed, hour):
            # Zero mph at sunrise is nearly ideal. 15 mph = 5; 20 mph = 0.
            ideal = 2 if hour <= 8 else 5 if hour == 9 else 7
            if speed <= ideal:
                return clamp(10 - .12 * (ideal - speed))
            if speed <= 15:
                return clamp(10 - (speed - ideal) * 5 / (15 - ideal))
            return clamp(5 - (speed - 15))

        samples = [(float(x), int(h['time'][i][11:13])) for i in indexes
                   if (x := value_at(h, 'wind_speed_10m', i)) is not None]
        scores['Wind & drift'] = mean(hourly_score(speed, hour) for speed, hour in samples)
        gust_penalty = min(2.0, max(0, (gust or wind) - wind - 8) * .18)
        directions = [float(x) % 360 for i in indexes
                      if (x := value_at(h, 'wind_direction_10m', i)) is not None]
        direction_penalty, bearing_text = 0, 'unknown'
        if directions:
            x = mean(cos(radians(d)) for d in directions)
            y = mean(sin(radians(d)) for d in directions)
            bearing = (degrees(atan2(y, x)) + 360) % 360
            bearing_text = ['N','NE','E','SE','S','SW','W','NW'][round(bearing/45) % 8]
            turn = max(abs((d - directions[0] + 180) % 360 - 180) for d in directions)
            if wind >= 8 and turn > 75:
                direction_penalty += .9
            elif wind >= 8 and turn > 45:
                direction_penalty += .4
            if wind >= 12 and (bearing >= 315 or bearing <= 45):
                direction_penalty += .7
        scores['Wind & drift'] = clamp(scores['Wind & drift'] - gust_penalty - direction_penalty)
        descriptions['Wind & drift'] = (
            f'Wind 7–11 a.m.: {wind:.1f} mph mean, {first:.1f} mph early → {last:.1f} mph late; '
            + (f'mean hourly gust forecast {gust:.1f} mph; ' if gust is not None else '')
            + f'predominantly from {bearing_text}. Gust penalty {gust_penalty:.1f}, direction/shift penalty {direction_penalty:.1f}. '
            + 'Profile rewards glassy sunrise followed by a gentle build to 15 mph. '
            + 'Direction is a rough frontal/shift proxy; it does not model shoreline-specific fetch or waves.'
        )
        if gust is not None and gust >= 28:
            flags.append('Very strong gusts; rough-water comfort cap applies')
        if wind >= 20:
            flags.append('Sustained morning winds >=20 mph; rough-water comfort cap applies')

    if temp is not None:
        comfort = clamp(10 - max(0, 60 - temp) * .48 - max(0, temp - 78) * .36)
        if humidity is not None:
            comfort = clamp(comfort - max(0, humidity - 75) * .08)
        scores['Air comfort'] = comfort
        descriptions['Air comfort'] = (
            f'Morning average {temp:.1f}°F'
            + (f'; relative humidity {humidity:.0f}%.' if humidity is not None else '.')
        )

    if cloud is not None:
        scores['Sky & sunrise'] = clamp(
            10 - max(0, cloud - 45) * .075 - max(0, 15 - cloud) * .03 - max(0, (rain or 0) - 20) * .065
        )
        descriptions['Sky & sunrise'] = (
            f'Average cloud cover {cloud:.0f}%'
            + (f'; mean hourly precipitation probability {rain:.0f}%.' if rain is not None else '.')
        )

    night = previous_night_items(weather, day)
    cloud_n = [float(value_at(h, 'cloud_cover', i)) for i in night if value_at(h, 'cloud_cover', i) is not None]
    overnight_cloud = mean(cloud_n) if cloud_n else None
    if lunar_illumination is not None and overnight_cloud is not None:
        exposure = lunar_illumination * (1 - overnight_cloud / 100)
        scores['Prior-night moonlight'] = clamp(9.5 - 5.5 * exposure)
        descriptions['Prior-night moonlight'] = (
            f'Experimental darkness proxy: lunar illumination ~{lunar_illumination*100:.0f}%, '
            f'overnight clouds ~{overnight_cloud:.0f}%. '
            'Moon-above-horizon timing is not directly included; this remains an unproven morning-bite hypothesis.'
        )

    recent = [
        i for i, t in enumerate(h.get('time', []))
        if (day - timedelta(days=2)).isoformat() <= t[:10] < day.isoformat()
    ]
    rain_vals = [float(value_at(h, 'precipitation', i)) for i in recent if value_at(h, 'precipitation', i) is not None]
    if rain_vals:
        rain_48 = sum(rain_vals)
        scores['Ecosystem stability'] = clamp(9 - max(0, rain_48 - 5) * .20)
        descriptions['Ecosystem stability'] = (
            f'Prior 48h modeled precipitation ~{rain_48:.1f} mm (local weather-grid proxy only). '
            'River discharge and front timing are not yet fully incorporated.'
        )

    if water_temp_f is not None:
        wt = float(water_temp_f)
        # Very broad comfort-oriented score, not a species-specific catch model.
        wt_score = clamp(10 - max(0, 66 - wt) * 0.18 - max(0, wt - 84) * 0.28)
        scores['Water temperature'] = wt_score
        descriptions['Water temperature'] = (
            f'Approximate near-coast water temperature {wt:.1f}°F from marine forecast guidance. '
            'Used as a comfort and seasonal-context input, not an exact back-bay observation.'
        )

    return scores, descriptions, flags


def tide_score(predictions, day, reference_range):
    try:
        pts = [(datetime.strptime(r['t'], '%Y-%m-%d %H:%M'), float(r['v'])) for r in predictions]
        pts = [(t, v) for t, v in pts if t.date() == day and 6 <= t.hour <= 11]
        if len(pts) < 3:
            return None, 'No sufficient NOAA hourly tide predictions for morning.'
        vals = [v for _, v in pts]
        movement = max(vals) - min(vals)
        net = vals[-1] - vals[0]
        normalized = movement / max(.25, reference_range)
        score = clamp(2 + min(1, normalized) * 8)
        direction = 'rising' if net > .05 else 'falling' if net < -.05 else 'nearly flat overall'
        return score, (
            f'NOAA station predicted movement {movement:.2f} ft between 6–11 a.m. ({direction}); '
            f'normalized to ~{reference_range:.2f} ft local reference range. '
            'Station movement is not equivalent to back-bay current speed.'
        )
    except (KeyError, ValueError, TypeError):
        return None, 'NOAA tide predictions could not be parsed.'


def calculate(day, location, weather, tide_predictions=None, lunar_illumination=None, water_temp_f=None):
    region = REGIONS[location]
    factors, reasons, flags = score_weather(weather, day, lunar_illumination, water_temp_f)

    if tide_predictions is not None:
        s, why = tide_score(tide_predictions, day, region['reference_range_ft'])
        if s is not None:
            factors['Tide movement'] = s
        reasons['Tide movement'] = why
    reasons.setdefault('Tide movement', 'NOAA prediction unavailable; not scored.')
    reasons.setdefault(
        'Water temperature',
        'No verified nearby water-temperature estimate is currently integrated. Not scored; the remaining available factors are normalized transparently.'
    )

    complete_weight = sum(WEIGHTS[k] for k in factors)
    measured_sum = sum(WEIGHTS[k] * v for k, v in factors.items())
    raw = round(measured_sum / complete_weight, 1) if complete_weight else None

    weekday = day.weekday()
    eligible = weekday in (1, 2, 3, 4)
    caps = []
    if weekday == 0:
        caps.append(7.0)
    if weekday == 4:
        caps.append(8.5)
    if any('rough-water comfort cap applies' in f for f in flags):
        caps.append(4.0)
    if 'Tide movement' not in factors:
        flags.append('NOAA tides unavailable: rating is weather-only')
    if complete_weight < .70:
        flags.append('Low input coverage: rating highly provisional')

    final = round(min([raw] + caps), 1) if raw is not None else None
    if weekday in (5, 6):
        eligible = False

    return {
        'location': location,
        'date': day.isoformat(),
        'score': final,
        'raw_score': raw,
        'factors': factors,
        'reasons': reasons,
        'coverage_pct': round(complete_weight * 100),
        'eligible_for_alert': bool(eligible and final is not None and final >= 8 and complete_weight >= .70 and 'Tide movement' in factors),
        'flags': flags,
        'weekday': day.strftime('%A'),
        'confidence': 'Lower (8–10 days)' if (day - date.today()).days >= 8 else 'Moderate (4–7 days)' if (day - date.today()).days >= 4 else 'Higher (1–3 days)',
    }
