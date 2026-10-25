# Sweet Spot V1.4 — Coastal UI Refresh

A polished 10-day Texas bay fishing forecast for Port O'Connor, Port Aransas and South Padre Island, retaining the existing live weather/NOAA tide and scoring model.

## Updating your EXISTING Streamlit website

1. Download and unzip `Sweet_Spot_V1_4_GitHub_Update.zip`.
2. Open your GitHub repo: https://github.com/MLPDevelopment/sweet-spot-fishing
3. Open the `app.py` file and click the pencil icon **Edit this file**.
4. Replace its entire contents with the contents of the new `app.py` file from the ZIP.
5. Click **Commit changes** and confirm. Your existing Streamlit website should redeploy automatically.

Or use GitHub **Add file → Upload files** and drag all six unzipped files to the repository root, then commit to replace matching filenames. If GitHub refuses a duplicate-file upload, use the pencil method for `app.py`.

Your existing site address remains https://sweet-spot-fishing.streamlit.app/ . No new repository or Streamlit app is necessary.

## What's new
- Coastal-colored hero with improved typography and whitespace
- Summary cards for the best eligible morning, top system and qualified candidates
- Native clickable day × location scores (30 clickable cells)
- Gray/excluded weekends and Monday recovery rules
- Region tabs and a clearer selected-day details view
- Factor progress indicators, explanations, input-coverage notices
- Live refresh using existing data collection, no simulated forecast numbers

## Limitations
- Score logic and external integrations unchanged; this release is primarily visual.
- The weather/tide calls still need to succeed on the Streamlit server.
- Lunar data and ecosystem-stability inputs are provisional, measured salinity/water temperature still incomplete.
- The site does not independently send email or text alerts; the separate ChatGPT task remains active.

## Local tests for developers (optional)
`pip install -r requirements.txt && pytest -q && streamlit run app.py`
