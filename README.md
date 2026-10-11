# Le Problème du Jour

![Le Problème du Jour](shared/branding/logo.png)

One repository for the new community edition: a WordPress website hosted at OVH,
a native iPhone app, and a future Android app sharing the same accounts and problems.

## Project status

This is the project foundation. The existing iPhone reader and the existing LaTeX
figure renderer have been copied into this repository. The original project remains
separate. WordPress accounts, submissions, review, email confirmation and authenticated
mobile access still need implementation; no OVH deployment or GitHub repository has
been created by this setup.

The new iPhone bundle identifier is `com.leproblemedujour.community` so it can coexist
with the original app. Its visible catalogue starts empty and its server address is
unset. Historical offline reader fixtures are retained for regression tests; they are
not the new published catalogue or the full editorial database.

## Layout

| Folder | Purpose |
| --- | --- |
| [ios](ios/README.md) | Existing SwiftUI reader and Xcode project, isolated for the new edition |
| [wordpress](wordpress/README.md) | Custom plugin and theme development for OVH; folders prepared |
| [android](android/README.md) | Reserved for the future Android client |
| [shared/branding](shared/branding/README.md) | Original PNG logo, SVG source and browser favicon |
| [shared/latex](shared/latex/README.md) | Reused rendering of mathematics, figures and references |
| [shared/api](shared/api/README.md) | Planned shared website/mobile data contract |
| [tools](tools/README.md) | Branding sync and future migration utilities |
| [docs](docs/specification.md) | Agreed requirements, hosting and migration notes |

## Open the iPhone app

Open `ios/ProblemOfTheDay.xcodeproj`, choose the `ProblemOfTheDay` scheme and an iPhone
simulator, then Run. The new WordPress service will be connected during implementation.

## Verify the shared renderer

Use Node.js 22.18+ or 24+. KaTeX is included with its MIT license; no install is required.

```sh
npm run test:latex
python3 tools/sync_branding.py --check
```

## Content and deployment

WordPress core, live accounts, passwords, uploaded figures, private reference PDFs,
database exports and hosting credentials do not belong in this code repository.
The complete editorial collection will be copied separately, using the live review
data rather than only the public iPhone catalogue. See [migration](docs/migration.md).

Use a private GitHub repository when the owner account is chosen. This folder contains
one local Git repository and has no remote configured yet.

Setup checks are recorded in [verification](docs/verification.md).
