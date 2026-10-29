# Local submission review

From the Programming repository:

```sh
admin/.venv/bin/python tools/local-admin/review.py --serve
```

Open <http://127.0.0.1:8766/admin/>. The course header shows **Admin** only on localhost. This server binds to 127.0.0.1, never your LAN address.

Put each UNIPA export in `admin/week02`, `admin/week03`, etc. Keep the exported filenames. Click **フォルダを再読み込み** to index new files. Unchanged notebooks reuse cached replay results. Student IDs in filenames associate notebooks and attachments; multiple notebooks are kept separately. An export spreadsheet is not required.

Place the student roster in `admin/roster.csv`. The importer finds the student-table header (even below course information), matches 学籍番号 to 学生氏名/氏名, and displays names. UTF-8 and CP932 exports are supported. Missing or conflicting matches remain explicitly marked rather than guessed. The roster stays local and ignored by Git.

The entire `admin/` folder is ignored by Git: originals, exports, generated pages, review JSON, and the Python environment must never be committed or copied to GitHub Pages. Public notebook excerpts are exported separately (see below).

## Public student work

The **みんなの作品 / Student work** menu opens `gallery.html`. Cards preview the notebook; selecting one opens the full notebook in cell order with inline outputs.

Each project preview offers a `.ipynb` download at the top and bottom. Downloads contain the sanitized public code, saved outputs, and embedded notebook attachments, not private originals, student IDs, local paths, or separate source attachments. Submissions without a notebook have no download. Required external data files are not bundled.

- **All submissions are shown**, with student names and readings, as authorized by Yoh. **♥ means featured**, not public/private: featured works appear first with a highlight. Removing a heart removes the highlight, not the project. Adding or removing a heart exports the feed, commits only `submissions/gallery.json`, and pushes to `origin/main`. A failed publication is reported in Admin; retry the heart action.
- Featured selections remain in ignored `admin/.gallery-hearts.json`. Student IDs and local user paths are redacted. The roster, admin notes, diagnostics, and source attachments are never exported. Images already embedded in notebook outputs are part of the public preview. Submissions without a readable notebook receive an explicit unavailable-preview card.
- **フォルダを再読み込み** imports and republishes all submissions, including new ones, while preserving featured selections.
- Local gallery content changes as soon as the export is written. Public visibility changes after GitHub Pages deploys the push; it cannot be instantaneous on static hosting. An open gallery checks for updates every 10 seconds while visible.
- Hearts no longer control visibility. Do not use this workflow for confidential submissions or credentials. The exporter blocks common literal API-key formats, but this is not a comprehensive secret scanner.

## Preview and execution

- **提出時の出力:** outputs saved inside the original notebook.
- **ローカル再実行:** the submitted code replayed in a disposable per-student directory, under a macOS sandbox. Network access and access to personal files are denied. Package-install lines are skipped. Shell commands, unsupported imports, and dynamic introspection are not executed. Each notebook has a 40-second timeout and a 25-second CPU limit.
- A trusted importer can pre-fetch literal public API URLs from an explicit host/path allowlist (Open-Meteo, Apple Music, JSONPlaceholder, PokéAPI, and Japanese Wikipedia). It never executes notebook code to discover URLs, follows no redirects, uses no credentials, and limits response sizes. Inside the sandbox, `urlopen` reads only those cached JSON responses. Each replay labels this as re-fetched data, with retrieval timestamps; it is not the student's original API response. Cache files remain under ignored `admin/_review/api-cache`. Dynamic URLs that cannot be resolved stay unavailable rather than guessed.
- Matplotlib charts render as static PNG outputs. A single Dropdown with up to 20 choices can be pre-rendered in the sandbox and switched in the browser, with a reconstruction label. Other widgets still require a real Jupyter kernel. Missing files and unsupported code remain explicitly reported, not silently repaired.
- Jupyter's implicit `display()` is available. A Windows absolute path can resolve only to a same-name attachment from that student's export, with a replay notice. This never searches other student folders. Execution caches are invalidated when the worker implementation or submitted files change.
- Export filename prefixes are removed only in temporary copies. If one CSV/TXT attachment exists and the notebook expects another CSV filename, a temporary alias is created and explicitly noted. Missing or ambiguous files remain errors, not silently replaced with another student's or the course dataset.
- HTML/Folium outputs render in sandboxed opaque-origin iframes with a restricted content security policy. Map backgrounds need Internet access from the browser. Nonstandard map CDNs may be blocked.
- OSM's volunteer tile service blocks opaque-origin requests. For display only, its standard background tile URL is replaced by Esri World Topo Map tiles, with a source/attribution link next to the preview. The original notebook and its code/data are unchanged.
- Execution issues are diagnostics, not grades. Originals are never edited, fixed, or overwritten. Local replays cannot prove the submission ran unchanged on a student's computer.

For a fresh setup, create the ignored environment and install trusted packages before starting:

```sh
python3 -m venv admin/.venv
admin/.venv/bin/python -m pip install folium pandas matplotlib
```

Replay requires macOS `sandbox-exec`. If isolation is unavailable, the tool keeps submitted outputs and records replay as unavailable; it never falls back to unrestricted execution.
