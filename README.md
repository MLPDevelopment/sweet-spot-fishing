# Putey’s Bay Fishing Outlook V2.2 — real photograph + lodging favorites

This is a visual/favorites-only update. **The V2.1 scoring engine remains unchanged.**

- Replaces the generated title image with the actual user-supplied wide photo of the wading angler (`assets/hero_personal.jpg`). The site applies a modest dark overlay for heading legibility, with no AI retouching.
- Adds Bay Flats Lodge (Seadrift, Port O’Connor area), Redfish Lodge Port O’Connor (the separate property at redfishpoc.com), and Redfish Lodge on Copano Bay (Rockport, Port Aransas/Aransas Bay area).
- Ad-tracking parameters removed from the user's Port O’Connor URL. The originally supplied redfishlodge.com points to the Rockport property, NOT the Port O’Connor location.
- Displays **V2.2 REAL PHOTO** prominently for deployment verification.

## Install

Open the existing GitHub repository, select **main**, and upload all files at the root while keeping the `assets/` directory intact. Commit **directly to main** or merge the pull request if GitHub requires one. Streamlit will redeploy. You may also update only `app.py`, `favorites.json`, and `assets/hero_personal.jpg` for this visual-only release.
