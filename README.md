# Putey's Bay Fishing Outlook (V1.6)

This package updates the hosted Streamlit app with:

- **Branding:** Putey's Bay Fishing Outlook
- **10-day outlook:** Port O'Connor, Port Aransas, South Padre Island
- **Daily conditions panel:** sunrise, sunset, air high/low, water temperature (when available), moon phase
- **Live sources:** Open-Meteo weather, Open-Meteo marine temperature guidance, NOAA CO-OPS tides
- **Scoring changes:** salinity omitted, water clarity omitted, red tide omitted

## Update GitHub / Streamlit

1. Download and extract this ZIP.
2. Open the existing GitHub repository: `sweet-spot-fishing`.
3. Use **Add file → Upload files** and upload the extracted files, replacing the existing files.
4. Commit the changes.
5. Streamlit should redeploy automatically.

Main app file: `app.py`

## Notes

- Weekend days remain excluded from fishing recommendations.
- Monday remains a recovery day capped at 7.0.
- Friday remains capped at 8.5.
- The moonlight factor remains experimental.
- Water temperature is sourced from marine forecast guidance when available and may not exactly represent back-bay conditions.

## V1.6 changes

Wind now rewards glassy mornings and a gradual build toward 15 mph. 15 mph maps to 5/10, 20 mph to 0/10 before gust and direction adjustments; this applies per hour, so a build to 15 mph late does not automatically score 5 for the whole morning. Directional shifts and brisk northerlies introduce small penalties (not a local fetch model). The app requests hourly wind direction. Seasonal TPWD tiles for bull reds, speckled trout, and flounder are informational and link to TPWD. A future guide/lodging section is reserved.
