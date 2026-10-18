> Current app update: Explore filters by Category, Level, Source and Progress (Unseen, Bookmarked, Attempted, Solved), with Language also available. Category contains Algebra, Geometry, Number Theory, Combinatorics and Logic. IMO, Animath and Yaglom are grouped sources; competition titles retain their dates. Home shows the app icon and published counts by source and in total. Today’s “Pick one” opens a random problem matching Category, Level, Source and Progress. Progress defaults to All, with Unseen, Bookmarked, Attempted and Solved also available. Progress is a single saved choice; legacy attempted/solved records retain that progress, while bookmark-only records become Bookmarked. All 18 simulator tests pass.

> September 2026 update: the app now reads the remote approved catalogue. Content updates do not need another binary release after this version is distributed. The initial approved bundle is empty until reviewers publish. See `../docs/editorial-workflow.md` for the current workflow; pilot descriptions below document the earlier offline prototype.

# Le Problème — iPhone app

Native SwiftUI app for iPhone and iPad, iOS 17 or later. Open
`Flexagon.xcodeproj` and select the **Flexagon** scheme.

## Included

- Explore all 40 problems, search their statements/titles/sources, and combine category,
  difficulty, language and source filters.
- Today picks a random problem using the selected filters, with an explicit navigation path for repeat selections.
- My library contains bookmarks, attempted problems and solved problems.
- A mobile reader with offline LaTeX typesetting, MathML and original geometry diagrams.
- PDF viewing and sharing, source details and personal notes.
- Device-local saved progress; no account, network dependency or analytics.
- Light/dark appearances, scalable reading text and accessible labels.

The interface is English; original problem statements remain French or English.
The bundled pilot is private review content, with provisional difficulty ratings and
independent human mathematical review still pending. Hints and solutions are not included.

## Run in the simulator

1. Open `Flexagon.xcodeproj` in Xcode.
2. Select the **Flexagon** scheme and an iPhone simulator.
3. Press **⌘R**. No Apple developer account is needed for the simulator.

This machine's default developer tools point to Command Line Tools. The shell commands
below use `DEVELOPER_DIR` only for this command and do not change system configuration:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  xcodebuild -project ios/Flexagon.xcodeproj -scheme Flexagon \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,OS=26.0' \
  -derivedDataPath /private/tmp/leprobleme-ios-build CODE_SIGNING_ALLOWED=NO build
```

Run the same command with `test` instead of `build` for the bundled XCTest suite.

Verified on iPhone 17 Pro / iOS 26.0: all six tests pass, including offline loading of
all 40 reader pages at 320-point width. See [verification details](VERIFICATION.md).

## Run on your iPhone

1. Connect your iPhone to this Mac and select it as the Xcode destination.
2. In the app target's **Signing & Capabilities**, choose your Apple development team.
   If necessary, use your own unique bundle identifier.
3. Enable Developer Mode on the phone if Xcode asks, then press **⌘R**.

Signing is intentionally unconfigured; no account, certificate or provisioning profile
was created. The simulator build is not an installable App Store/physical-device IPA.
This is a private development build, not an App Store submission.

## Content and storage

The app reads a compact bundled JSON catalogue exported from the canonical problem data.
This first release uses the JSON snapshot rather than SQLite at runtime; no database
service is necessary for 40 records. The original SQLite catalogue remains the editorial
source export. Bookmarks, notes and progress are saved separately in UserDefaults under
`problemProgress.v1`. Content updates therefore do not replace progress.
Deleting the app deletes its local data; cloud sync and progress export are not yet built.

The exporter uses KaTeX 0.16.22 to pre-render 287 mathematical expressions into HTML and
MathML. It bundles CSS and fonts; the reader needs no CDN, scripts or network access.
Displayed mathematics can scroll horizontally within the equation on narrow screens.
Source website links open only when requested. No original desktop filesystem paths are
packaged in the mobile catalogue.

```sh
# From the repository root, after rebuilding the catalogue:
node scripts/export_ios.cjs
```

KaTeX is vendored under `Flexagon/Content/Reading/katex/`, including its MIT license.
The JS file is used by the build-time exporter; it is not executed by reader documents.
Project settings can be regenerated with `python3 scripts/make_xcode_project.py`.
Avoid regenerating over manual signing changes without recording those changes first.

## Remaining work

Human content review and difficulty calibration; native UI localization; solution import;
VoiceOver testing with mathematical speech; optional progress export/sync; public content
permissions; physical-device testing and distribution signing.
