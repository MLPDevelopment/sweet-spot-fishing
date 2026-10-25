# Putey’s Bay Fishing Outlook V2.1 — clean refresh

The ZIP contains application files at the top level, plus the `assets` folder. No nested `puteys_v19` directory.

1. Open https://github.com/MLPDevelopment/sweet-spot-fishing and select the **main** branch.
2. Choose **Add file → Upload files** and drag in the extracted files and the entire `assets` folder. Verify paths start `assets/`.
3. At the bottom, choose **Commit directly to the main branch** rather than creating a patch branch. Commit changes.
4. If GitHub prevents overwriting files, use GitHub’s edit (pencil) button for those files or merge an update branch into main through a pull request.
5. Open https://sweet-spot-fishing.streamlit.app/ and hard-refresh with Ctrl+Shift+R. In Streamlit app controls, reboot if necessary.
6. Verify the page explicitly shows **V2.1 CLEAN REFRESH • BUILD 2026-10-25-v21**. If not, Streamlit is still running older files.

Contains calibrated wind direction/gust scoring and 8+ qualification gates from V2.0, South Padre bridge aerial, species art, and favorites. Live forecast values may remain similar even when the deployment succeeds.
