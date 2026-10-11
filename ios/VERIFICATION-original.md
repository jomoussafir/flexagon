## Unified source groups

All 15 simulator tests pass after grouping all IMO years, Animath years and Yaglom volumes. Both app source menus and category filters use the same groups as the review website. Other source names and categories remain unchanged. The source selector lists only sources represented in published app content; categories include IMO, Animath and Yaglom even before publication.

## 20 September 2026 — categories, progress and Pick one

All 14 iPhone 17 Pro / iOS 26 simulator tests pass. New checks cover IMO/Animath grouping and dated titles, all four progress choices across relaunch, migration of existing bookmarks/notes, combined progress filters, and exclusion of bookmarked/attempted/solved problems from the unseen selection pool. Existing cache, bilingual publication and offline mathematics checks also pass. Test caches are isolated from downloaded app data; the reader check waits for stylesheets before assessing math fonts.

Manually checked Explore with published IMO and Animath records, Today’s category/level/source menus and Pick one navigation, and the four visible progress choices on the problem page. The app build is ready locally; no App Store or physical-device release was made.

# Review workflow update — 20 September 2026

The updated app builds in Xcode and all 11 simulator tests pass on iPhone 17 Pro / iOS 26. Tests include English/French fallback and selection, language-aware filtering, rejection of invalid catalogue variants, atomic refresh, offline cache recovery, withdrawal without loss of progress, downloaded HTML loading with bundled KaTeX styling and injected scripts blocked, plus the prior pilot reader and persistence checks. The 80 pilot language drafts contain 558 strictly parsed KaTeX expressions.

No App Store submission, distribution signing or physical-device installation was performed. Source OCR and draft translations still need human review. The initial public feed contains zero problems because no version has been approved.

# iPhone app verification

18 September 2026. Xcode 26.0.1; iPhone 17 Pro simulator; iOS 26.0.

## Build and automated tests

The native application builds and installs successfully. Six XCTest cases pass:

1. All 40 unique catalogue records have bundled PDF and HTML assets, without runtime scripts.
2. Combined topic/difficulty/language/source filters and accent-insensitive search return expected problems.
3. Corrupt saved progress is reported and not silently overwritten.
4. The daily problem is stable across launches/input ordering and throughout a calendar day at each selected difficulty.
5. Bookmarks, notes and solving status survive reloading and remain independent.
6. All 40 HTML reader pages load locally in WKWebView at 320-point width, with expected
   MathML, loaded diagrams, KaTeX styling and no horizontal overflow of the overall page.
   Wide display equations scroll within their own container. Prose-only problems need no math markup.

Build-time export also successfully parsed all 287 mathematical expressions with strict KaTeX rendering.
The test result bundle is `/private/tmp/leprobleme-tests-final.xcresult` (temporary local build artifact).

## Manual simulator checks

- Explore screen, category chips, problem cards and filter sheet visually checked.
- A French problem with a wide fraction opened correctly in the adaptable reader.
- Bookmarking and marking that problem solved made it appear in My library with both states.
- Those temporary demo changes were reversed afterwards.
- Today and My library screens visually checked; app left open in Explore.

The initial install failure was traced to using a top-level folder named Resources in the
application bundle. Renaming the bundled content folder to Content fixed installation.

## Boundaries

No physical iPhone run or distribution signing was performed. No developer account settings
were changed. iOS 17 is the deployment target; this run used iOS 26.0. VoiceOver mathematical
speech and large accessibility font sizes still need dedicated device review. Content difficulty
and independent human mathematical review remain provisional/pending as recorded in the catalogue.

### Today progress filter — 21 September 2026

- Today now defaults to all progress states; Progress offers All, Unseen, Bookmarked, Attempted and Solved.
- Category, level, source and progress combine in the random selection pool. Empty results explain how to reset filters.
- Pick one pushes a problem onto an explicit navigation path, allowing repeated picks after returning to Today.
- The 15-test simulator suite passed, including every progress choice, missing records treated as unseen, combined filters and empty pools.
- Physical-device tap behavior still requires confirmation on the user's iPhone.

### Downloaded statement reader — 21 September 2026

- Downloaded HTML now loads from a temporary local document with an explicit WebKit read-access grant; bundled KaTeX styles and fonts are copied alongside it. File navigation checks resolve symlinks consistently.
- Reader fills its available space. Navigation failures display a retry action; a terminated web-content process gets one automatic reload.
- All 15 simulator tests passed. The downloaded-reader test checks the local file URL, visible reader bounds, statement text, math styling and blocked injected scripts.
- Physical-iPhone display needs user confirmation; simulator results alone do not establish the reported device-only failure is resolved.

### Subjects, sources and Home — 21 September 2026

- Category is limited to five mathematical subjects. Source grouping retains IMO, Animath and Yaglom across years/volumes. Cached records containing the former source-category values use their original imported subjects.
- Home is the initial tab, showing the app icon, total downloaded published problems and per-source counts, including zero-count known sources. Each source opens a filtered Explore tab. Multiple references and translations do not duplicate counts.
- All 17 simulator tests pass, including source counting and legacy published-category compatibility. Signed device build succeeded; Xcode was waiting for Octave to be unlocked before launch.

### Source grouping and order — 21 September 2026

- Challenging Problems In Algebra and Challenging Problems In Geometry share the source group “Challenging Problems in Geometry and Algebra”. Original references remain intact.
- Home counts and Explore/Today source filters use: Moscow, Colossal, Animath, Challenging Problems, Yaglom, Stanford, IMO. The validation overview, counts and reference menu use the same ordering.
- All 18 simulator tests pass. Updated signed app built, installed and launched on Octave.
