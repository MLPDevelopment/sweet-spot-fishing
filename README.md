# Sweet Spot — hosted prototype (V1.3)

A 10-day morning fishing outlook for Port O’Connor, Port Aransas, and South Padre Island.

## No-code deployment

1. Create a GitHub repository named `sweet-spot-fishing` (private if preferred).
2. Upload ALL files from this folder **to the repository root** (not within a nested folder).
3. In [Streamlit Community Cloud](https://share.streamlit.io), click **Create app**, then **Yup, I have an app**.
4. Choose the new repository, branch `main`, and **Main file path `app.py`**, then deploy.
5. When the app loads, use **Refresh live forecasts** and check for missing-data warnings.

If the GitHub web uploader does not accept a ZIP archive as source code, extract this package first and select the *individual* files, not the ZIP.

## Notes

- Server requests hourly weather from Open-Meteo and hourly station tide predictions from NOAA. External APIs must be reachable by the hosting service.
- The first deployment requires checking which tide stations support `datum=MLLW` and hourly predictions. A missing feed is shown as an error, not fictional data.
- Each day/location has selectable factor explanations, cited raw API links, and a stated data coverage percentage.
- Water clarity is not rated. Water temperature and salinity are planned but not yet implemented; scores are explicitly provisional and prorated across available factors.
- Red tide is not an automatic gate. User independently checks official notices if relevant.
- The prior-night darkness hypothesis is experimental; present lunar estimate omits true moonrise/moonset.
- This **does not** deploy or synchronize the separately scheduled ChatGPT alert.
- Not a marine safety or navigation forecast. Always check local marine warnings and advisories before departure.

## Files

- `app.py`: Streamlit UI
- `engine.py`: scoring rules
- `sources.py`: remote data sources
- `test_engine.py`: sanity checks
- `requirements.txt`: packages Streamlit installs automatically
