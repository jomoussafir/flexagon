# Editorial migration — 12 October 2026

The local WordPress administrator workspace has 1,854 imported problems. All are
unpublished. The original editorial site has 1,855 records: the remaining
`local-2ef4179b3388-11-15` (A Map-Coloring Game) is held back until its complete current
record and five historical revisions can be exported after original-site sign-in.
The database connector truncates these long JSON cells; truncated records are never
imported or silently replaced by older seed text.

## Preserved data

The import merges seed records with complete saved database overrides and applies
the original site's source/title and vector-figure upgrades. Both language versions,
LaTeX, saved verification flags, difficulty and categories are retained. Stable legacy
IDs, complete source citations, PDF page associations, notes and original revision
history remain in private metadata. The editor exposes original source details and
a link to the original protected review/PDF viewer. Source books remain there;
no private PDFs are copied into publicly accessible WordPress uploads.

The 17 recovered edited records and 34 complete history entries are included. Attached
figures are copied into protected WordPress assets, retaining their filenames so
`\includegraphics` and local references continue working. Original verification
flags stay checked, but no published snapshot is created: **Save & publish** remains
an explicit administrator action in the new edition. No notification emails are sent.

Sources are grouped and ordered as Moscow Puzzles, Colossal Book, Animath,
Challenging Problems in Geometry and Algebra, Yaglom, Stanford and IMO. Dated
competition titles and the five mathematical categories are retained.

## Repeating or completing the local import

The private `private-data/legacy-export/import.json` bundle uses format
`lpdj-legacy-v1`, with `problems`, `figures` and `history`. Do not commit it.

Stop the local website, then run:

```sh
node_modules/node/bin/node tools/import-legacy.mjs private-data/legacy-export/import.json
npm start
```

The tool backs up the SQLite database to ignored `backups/`, imports by stable legacy
ID and checks all imported records. It writes `wordpress-ids.json` and
`verification.json` beside the input. Existing records are skipped, preserving edits
made in WordPress; rerunning an updated bundle adds missing records without duplicates.
It does not reconcile later changes from the old site into existing WordPress drafts.

The plugin's administrator-only `lpdj_import_legacy($records, $figures, $history)`
function also runs under WordPress on OVH (e.g. an administrator WP-CLI migration).
There is deliberately no bulk-import HTTP endpoint. Keep the input outside the web
root and import in batches. Code ZIP packages do not contain the private database,
figures, history or reference books; production data migration is a separate step.

The old app, publication feed and editorial website remain unchanged. The public
feed contains only published problems and is not used as the import database.
