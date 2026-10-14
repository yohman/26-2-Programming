# Local submission review

From the Programming repository:

```sh
admin/.venv/bin/python tools/local-admin/review.py --serve
```

Open <http://127.0.0.1:8766/admin/>. The course header shows **Admin** only on localhost. This server binds to 127.0.0.1, never your LAN address.

Put each UNIPA export in `admin/week02`, `admin/week03`, etc. Keep the exported filenames. Click **フォルダを再読み込み** to index new files. Unchanged notebooks reuse cached replay results. Student IDs in filenames associate notebooks and attachments; multiple notebooks are kept separately. An export spreadsheet is not required.

The entire `admin/` folder is ignored by Git: originals, exports, generated pages, review JSON, and the Python environment must never be committed or copied to GitHub Pages. Only the reusable tool and the local-only menu code are tracked.

## Preview and execution

- **提出時の出力:** outputs saved inside the original notebook.
- **ローカル再実行:** the submitted code replayed in a disposable per-student directory, under a macOS sandbox. Network access and access to personal files are denied. Package-install lines are skipped. Shell commands, unsupported imports, and dynamic introspection are not executed. Each notebook has a 40-second timeout and a 25-second CPU limit.
- Export filename prefixes are removed only in temporary copies. If one CSV/TXT attachment exists and the notebook expects another CSV filename, a temporary alias is created and explicitly noted. Missing or ambiguous files remain errors, not silently replaced with another student's or the course dataset.
- HTML/Folium outputs render in sandboxed opaque-origin iframes with a restricted content security policy. Map backgrounds need Internet access from the browser. Nonstandard map CDNs may be blocked.
- OSM's volunteer tile service blocks opaque-origin requests. For display only, its standard background tile URL is replaced by Esri World Topo Map tiles, with a source/attribution link next to the preview. The original notebook and its code/data are unchanged.
- Execution issues are diagnostics, not grades. Originals are never edited, fixed, or overwritten. Local replays cannot prove the submission ran unchanged on a student's computer.

For a fresh setup, create the ignored environment and install trusted packages before starting:

```sh
python3 -m venv admin/.venv
admin/.venv/bin/python -m pip install folium pandas
```

Replay requires macOS `sandbox-exec`. If isolation is unavailable, the tool keeps submitted outputs and records replay as unavailable; it never falls back to unrestricted execution.
