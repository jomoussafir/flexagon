# Deployment hygiene and performance fixes — 18 October 2026

- Theme assets: 1,138 Finder duplicate files (for example `pdf 2.mjs`, `LICENSE 3`,
  duplicated KaTeX fonts and CMaps) were deleted. The build now recreates the vendored
  `katex` and `pdfjs` directories on every run and the packager refuses such names.
  The theme ZIP shrank from 19.4 MB (0.2.1) to 4.1 MB (0.2.2) with identical content.
- Local port references corrected from 9400 to 9410 in the legacy import guard, the
  iPhone guide and two audit documents.
- Plugin and theme 0.2.2: overview lists for `published` and `review` are served from
  a transient invalidated by every write path; `editable` no longer loads each post
  separately. Throttles use `lpdj_client_ip()`, which honours a trusted proxy header
  only when `LPDJ_TRUSTED_PROXY_HEADER` is defined. The legacy review link reads
  `LPDJ_LEGACY_REVIEW_URL`. KaTeX stylesheet versioning uses the file time.
- Emails link to English addresses (`#/confirm`, `#/reset`, `#/problem`, `#/profile`,
  `#/edit`); the French names remain aliases in the router.
- Results: website build and both 0.2.2 ZIPs; 60 isolated WordPress integration checks,
  8 LaTeX checks and 7 progress checks passed; branding check passed. Local preview
  smoke test as administrator: review overview returned 1,856 records with no
  statements or image data, 2 publications, correct `editable`/`progress`; session
  `addresses` reported for the administrator only.
- Not changed here: the OVH cron task and the proxy header decision require the live
  host; PDF.js CMaps, standard fonts and wasm are kept because no reference PDF was
  found to need them but the saving is under 4 MB uncompressed.

# Website verification — 13 October 2026

## Current website

- Progress now offers All, Unseen, Bookmarked, Attempted, Solved and Unsolved.
  Browser checks on disposable sample data verified each added status, empty results,
  combined source filtering, 24-to-26-card expansion and card-to-reader navigation.
  The compact grid fits seven columns at 1280 px and two at 390 px without document
  overflow; no console errors. The user's catalogue and personal progress were untouched.

- Private reference links are present in Admin review and the problem editor.
  All 1,863 recorded occurrences across 1,854 imports resolve to one existing PDF
  part/page; the 103 copied PDFs (78 source entries) match the originals by SHA-256.
- Five additional integration checks cover admin-only reference metadata/downloads,
  split-PDF page mapping, missing pages/indices, traversal rejection and publication
  excluding private reference metadata. Ordinary members and anonymous visitors
  cannot download the PDFs even when the corresponding problem is published.
- Browser checks opened Moscow Puzzles at PDF page 46 and Three Squares at its
  recorded PDF page 138; verified Next/Problem page controls and the Colossal Book
  transition from PDF page 140 to 141 (first page of the next part). The PDF viewer
  rendered at 1280 px and 390 px with no horizontal document overflow or console errors.
  Source links open in a new tab; the viewer links back to Admin review/the editor.

- Landing-page follow-up: the icon now has “Le Problem du jour” beside it; both
  home and About show the manifesto without an About heading. Typography is smaller.
  The rebuilt theme was checked at 1280 px and 390 px, with no horizontal overflow.

- WordPress 7.1.3 / PHP 8.3 running in the official local Playground runtime.
- 48 isolated integration checks pass: email confirmation, cookie/nonces, member/admin
  permissions, private drafts and images, safe/unsafe SVG uploads, stale revision
  rejection, FR/EN publication, first Save & Publish approval preservation, published
  snapshot isolation, personal progress, revision history, return notes, profile
  images, opt-out notifications, password reset and account/draft deletion; legacy
  import permissions, preserved LaTeX/figures/history and duplicate/overwrite prevention.
- Named-language checks cover submissions without English/French, custom identifiers,
  independent approval, private edits/removals, preserved history, label validation,
  member publication denial and current per-user progress in overview responses.
- All 7 Progress model tests pass: solved/unsolved grouping, numeric difficulty and
  source ordering, combined filters, translated-title searches and immutable inputs, each independent status filter,
  combined metadata/status filters and filtered counts.
- Browser verification on a separate disposable collection covered the four-link
  landing banner, About manifesto, member sign-in, Progress grouping/filtering,
  24-card pagination, card-to-reader navigation, language selection, marking solved
  and returning to the updated grid, and submitting English/Occitan versions.
  Layouts were inspected at 1280 px and 390 px; the mobile page has no horizontal overflow.
- All 8 shared LaTeX tests pass after the KaTeX 0.19.0 security update.
- Website asset build succeeds; npm audit reports zero known vulnerabilities.
- Plugin/theme deployment ZIPs are generated and checked for archive integrity.
- The original logo matches the iOS and website copies byte for byte.
- Browser inspection covered signed-out landing/registration, administrator sign-in,
  the empty collection, editing, first-save publication, math/currency preview and
  the published reader. Desktop (1280 px) and narrow/mobile (390 px) layouts checked.
- The original temporary browser-test problem was removed. The local admin collection
  now contains 1,854 unpublished imports (one long legacy record awaits sign-in),
  plus local user drafts, which were preserved.
- Import verification compares all 1,854 original records and both language versions,
  34 historical revisions and 3 figure assets; zero mismatches, zero publications.
- Browser verification of the English admin workspace covered all source counts,
  50-row pagination, Yaglom filtering and difficulty sorting. Three Squares retains
  its checked EN version, inline SVG, figure reference, source page and two saved
  revisions. No slogans or generic heading subtitles remain.
- Local emails are captured in an admin-only mailbox. No real email was sent.

The integration suite uses a separate disposable database on port 9401. The persistent
preview is on port 9410 and is bound to loopback only. Local state and credentials are
ignored by Git and excluded from deployment packages.

## Remaining environment checks

No OVH deployment, production SMTP delivery, production MySQL staging test, physical
iPhone browser test, native mobile account integration, completion of one remaining legacy record,
Android build or GitHub upload has been performed. Production operator/contact details
must be supplied before the legal/privacy page is finalized for a public launch.
The website supports a documented LaTeX subset; it does not compile arbitrary TeX/TikZ.

## Earlier foundation checks

The copied iPhone app had a successful simulator Debug build in the initial foundation
step. Its bundle ID is isolated and its original public feed is unset. No native app
code was changed during this website implementation and no iOS rebuild was needed.
The historical files under ios describe the original app, not the new WordPress client.

## Local iPhone connection — 13 October 2026

- Debug iPhone app uses the local website in WKWebView with WordPress cookie sign-in.
- 22 simulator tests pass with no failures or skips: 18 inherited reader checks,
  3 URL/origin-policy checks and a real local WebKit/unauthorized-API smoke check.
- The anonymous API still returns 401; no new public feed or permission bypass exists.
- Native Back, Home and Reload controls and JavaScript confirmations are supported.
- The local administrator signed in through the simulator, and a published problem
  opened from WordPress; the app catalogue displayed the same 2 published problems.
  No problem content or publication state was changed.
- Mobile touch form text uses at least 16 px to avoid iPhone focus zoom; ordinary
  page typography and desktop filter sizing stay unchanged.
- Loopback HTTP exceptions and the embedded website are Debug-only. Release retains
  the native foundation; physical-phone networking/production integration is pending.

### Profile and submission layout

The separate My profile page heading is removed; the profile panel remains. My
submissions opens directly on Your problems, with no separate page heading, top
summary counter or source count chips. The filtered submission count remains beside
the list controls. The shared website screens give the connected Debug app the same
layout on reload.

## Vibrant palette — 13 October 2026

- Website build and deployment ZIP packaging succeed; `git diff --check` passes.
- Desktop Problem page checked at 1280 × 900, mobile Progress and problem reader
  at 390 × 844. No horizontal overflow; compact controls and difficulty labels
  remain visible. Browser viewport override reset after verification.
- Body, muted text, action buttons, active navigation, links, placeholder text,
  coloured statistics and all five difficulty text/background pairs exceed a
  4.5:1 contrast ratio (lowest checked pair 4.79:1).
- Debug iOS simulator build succeeds. Installed and opened on iPhone 17 Pro / iOS 26;
  the website header, About panel, background and native navigation bar show the
  matching palette. No physical iPhone colour check was performed.
- Screenshots saved under the ignored `private-data/verification/` directory as
  `vibrant-palette-desktop.jpg`, `vibrant-palette-mobile.jpg` and
  `vibrant-palette-iphone.png`. No problem or publication data was changed.

## Saved Basquiat and Vermeer trial — 13 October 2026

- The saved `palettes/basquiat.css` was compared byte-for-byte with the previously
  committed active stylesheet; it matches exactly. Both native colour presets
  are retained in the Debug client.
- Website build, deployment package generation and Debug simulator build succeed.
- Desktop collection checked at 1280 × 900; mobile Progress and reader at 390 × 844.
  No horizontal overflow. The header menu retains dark text on its light popup.
- Checked text/background pairs exceed 4.5:1: body, muted text, header navigation,
  active navigation, both primary button styles, links, coloured statistics,
  placeholders and all five difficulty levels. Lowest checked contrast: 5.27:1.
- Updated build installed and opened on iPhone 17 Pro / iOS 26 simulator. The
  blue/ochre header, ivory page and native blue navigation controls are visible.
- Screenshots: `private-data/verification/vermeer-palette-desktop.jpg`,
  `vermeer-palette-mobile.jpg`, `vermeer-palette-iphone.png` (ignored by Git).
- Only presentation changed. No problem, progress or publication data was changed.
