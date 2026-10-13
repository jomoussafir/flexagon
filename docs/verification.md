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
preview is on port 9400 and is bound to loopback only. Local state and credentials are
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
