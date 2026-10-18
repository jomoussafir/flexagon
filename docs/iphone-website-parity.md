# iPhone and website parity check — 13 October 2026

**Follow-up:** The Debug app now embeds the local WordPress website for simulator testing, using its normal sign-in and shared data. See [the iPhone testing guide](../ios/README.md). The findings below still describe the inherited native reader used by Release builds.

At the time of this audit, the community iPhone app did **not** yet match the WordPress website. It is the
copied reader foundation, with its old public catalogue address removed. Website
work has not yet been integrated into this native client.

Scope: `ios/Flexagon.xcodeproj` in this repository. The original project in
`Documents/ChatGPT/Flexagon` was not changed. This is a comparison and
build/test verification; it does not implement the missing integration.

## Findings

| Area | Website | Community iPhone app |
| --- | --- | --- |
| Icon | Shared Poincaré disk artwork | Matches byte for byte |
| Accounts | Registration, confirmation, sign-in, reset, profile and deletion | Not implemented |
| Problem database | Authenticated WordPress records and approved snapshots | Empty bundled catalogue; no server configured |
| Data format | WordPress overview/detail API, named languages and LaTeX | Legacy public JSON catalogue containing pre-rendered HTML; incompatible with the website API |
| Navigation | About, Problem, Progress, Submit and account menu | Home, Explore, Today and My library |
| Landing | About manifesto | Source counts and catalogue refresh |
| Filters | Search, mathematical category, difficulty, source and progress | Similar basic reader filters, but not the website layout or collection sorting |
| Progress | All, Unseen, Bookmarked, Attempted, Solved and Unsolved; compact grouped grids | Bookmarks, Attempted and Solved lists; no grouped Progress grid |
| Progress storage | Per WordPress member | Device-only UserDefaults; does not synchronize with the website |
| Languages | Up to 20 user-named versions | Catalogue validation rejects anything except EN/FR and more than two versions |
| Submission and review | LaTeX editor, figures, review, approval and publication | Not implemented |
| Reference PDFs | Administrator-only original page viewer | No connection to the website's protected reference viewer |
| Mathematics and figures | Shared LaTeX renderer and protected assets | Older offline HTML reader; no authenticated transport for website figures |
| Profile and notification preferences | Available in member profile | Not implemented |

Evidence: `ios/Flexagon/App/LibraryStore.swift` (legacy catalogue loading and
local progress), `LibraryViews.swift` (navigation and saved lists), `Models.swift`
(EN/FR-only catalogue validation), and `ProblemDetailView.swift` (offline reader).
Compare `wordpress/themes/flexagon/src/app.ts` and `shared/api/README.md`.

The native bundle also still contains the 40 inherited pilot problem fixtures and
PDFs even though its visible published catalogue is empty. Move these into test-only
resources before distributing the community app.

## Verification

- Branding synchronization check passes.
- Xcode 26.0.1 built the app and test target successfully.
- All 18 existing tests passed on iPhone 17 Pro / iOS 26 simulator, with zero failures.
- Reader tests loaded all 40 offline fixtures, checked mathematics/images and phone
  width, and checked that the downloaded HTML reader blocks injected scripts.
- Test results: `/private/tmp/lpdj-ios-parity-check-results.xcresult`.
- These tests validate the existing reader; they do not establish website parity.
- No physical iPhone verification or WordPress login in the native app was possible
  because the native account integration does not exist.

## Required integration

Use the website's WordPress accounts, published snapshots, protected assets and
per-member progress as the common source for both clients. The current catalogue
address field cannot connect to this API simply by changing its URL.

Implement the member session and authenticated data transport first, then match
About/Problem/Progress navigation and grouping. Add named-language rendering,
submission/profile screens and the administrator workflow. Keep draft access and
publication permissions enforced by WordPress, and test account switching, logout,
approval boundaries and cross-client progress synchronization.

The current website is a Mac-local preview bound to `127.0.0.1:9400`. Physical-phone
integration also needs an explicitly configured reachable development or hosted
website address; the Mac's loopback URL is not an iPhone server address.
