# Putey’s Bay Fishing Outlook V1.9

This release cleans up the five fish illustrations, removes redundant text above the species cards, adds three location-specific illustrated coastal banners, and introduces an editable favorites file.

## Uploading to GitHub

Upload **all six Python/text files**, the new `favorites.json`, and the **entire `assets/` folder** to the repository root. Make sure GitHub shows `assets/port_oconnor_banner.jpg`, `assets/port_aransas_banner.jpg`, etc. Streamlit redeploys the existing website automatically.

## Adding your own favorites (no Python required)

1. In GitHub, open `favorites.json` in the root of your repository.
2. Click the pencil icon **Edit this file**.
3. Add an entry within the desired location's `guides`, `lodging`, or `restaurants` list using the existing guide as an example.
4. Select **Commit changes**. Streamlit will update the favorites section.

Example:

```json
{"name": "Your favorite place", "description": "A short personal note", "url": "https://example.com/"}
```

For multiple favorites within the same list, separate entries with commas. Do not remove the quote marks, brackets, or braces.

## Current favorite

Port O’Connor → Fishing guides → **Kim Goulden Fishing** (https://www.portoconnorfishingtrip.com/), verified official website with guided wade and drift trips using artificial lures.

## Notes

Seasonal summaries are descriptive, approximate, and are not current regulations. Imagery is illustrative and should not be construed as a photograph of a specific exact shoreline. Fishing scoring and data integrations are unchanged from V1.8.
