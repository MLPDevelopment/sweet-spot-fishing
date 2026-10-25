# Putey's Bay Fishing Outlook — V1.8

## What's new

- Illustrated sunrise hero featuring the new approved artwork, with a header option to switch to the original wading photo.
- Five illustrated Gulf Coast fish: bull redfish run, redfish, speckled trout, southern flounder, tarpon.
- Compact, below-the-forecast seasonal cards including approximate windows and TPWD species links.
- Existing location colors and bottom-of-page guides/lodging/restaurants placeholders retained.
- Forecast, NOAA tide and scoring code retained from V1.7.

## Updating the current GitHub/Streamlit site

**Important: V1.8 adds an `assets` subfolder.** The images must be in `assets/` within your GitHub repository, not in the root.

1. Download and unzip the package.
2. On GitHub open your existing `sweet-spot-fishing` repository.
3. In the root of the repository, replace `app.py`, `engine.py`, `sources.py`, `test_engine.py`, `requirements.txt`, `README.md` with the supplied files and commit changes.
4. In the repository, choose **Add file → Upload files**. Drag the **entire `assets` folder** onto the GitHub uploader (from your computer's file explorer), checking that the path displayed is `assets/...` before committing. If GitHub uploads only individual images at the root, use **Add file → Create new file**, and enter `assets/.gitkeep` first, then use **Add file → Upload files** from inside the `assets` directory to upload the seven images.
5. Confirm `assets/hero_illustrated.jpg`, `assets/hero_personal.jpg`, and the five fish PNGs are present. Streamlit should redeploy automatically.

## Notes

- The illustrated sunrise banner has lettering embedded in the artwork. The original-photo option uses accessible live text over the photograph.
- Seasonal windows are broad Texas Coast patterns, not catch promises or regulations.
- User's favorite guides, lodging and restaurants remain unfilled so no links or endorsements are fabricated.
- Images are kept locally in the repo so Streamlit doesn't depend on third-party hotlinked photos.
