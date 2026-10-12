# Le Problème du Jour

One repository for the community edition: a WordPress website for OVH, the iPhone
reader foundation and a future Android client. The original app logo is shared.

## Launch the website

Double-click **Open Website.command**, or run:

```sh
npm ci
npm start
```

Open **http://127.0.0.1:9400/**. Administrator credentials are in **Local access.txt**,
created on launch and excluded from Git. Your database persists in `.local/wordpress`.
See [START-HERE.md](START-HERE.md) for a non-technical walkthrough.

## Implemented website

- English interface with WordPress email/password accounts, display names, email confirmation and password reset.
- Member-only catalogue; private drafts, submissions and admin review.
- French and English versions, independent approval and publication.
- LaTeX editor/import, live preview, protected SVG/PNG/JPEG figures with
  `\includegraphics`, captions and local `\label` / `\ref` numbering.
- Categories, difficulty 1–5, sources, keywords, filters and FR/EN validation sorting.
- Per-member progression: unseen, bookmarked, attempted and solved.
- Version history; editing a published problem leaves its approved snapshot online.
- Profile images, opt-in new-publication email and account deletion.
- A local WordPress runtime, private test mailbox, deployment ZIP packages and tests.

The local admin collection contains 1,854 imported problems, all unpublished. One long
record (A Map-Coloring Game) awaits a complete authenticated export; see docs/migration.md.
The previous app/site are unchanged. OVH deployment, production mail configuration and
native app authentication/integration remain separate next steps. There is no
GitHub remote yet.

## Layout

| Folder | Purpose |
| --- | --- |
| `wordpress/plugins/le-probleme-du-jour` | Accounts, permissions, problem workflow, protected assets and REST API |
| `wordpress/themes/le-probleme-du-jour` | Responsive community website |
| `ios` | Copied SwiftUI reader, not yet connected to the member-only WordPress API |
| `android` | Reserved for a future Android app |
| `shared/branding` | Original logo and favicon |
| `shared/latex` | LaTeX/figure renderer and its regression tests |
| `tools` | Local launcher, asset build, branding sync and deployment packaging |
| `tests` | Isolated real-WordPress integration suite |
| `docs` | Requirements, verification, hosting and migration notes |

## Development

Node.js 22.18+ can install/build the project. `npm start` and `npm run test:web` use
the project-local Node 24.18 runtime required by WordPress Playground. No system PHP,
Docker or MySQL install is needed for the local preview. Production runs on standard
WordPress/PHP and MySQL at OVH; Playground is only a development dependency.

```sh
npm run build:web
npm run test:latex
npm run test:web
python3 tools/sync_branding.py --check
npm run package:web
```

`npm run test:web` creates a disposable database on port 9401. It never uses the
preview database on port 9400. The local server binds only to 127.0.0.1.

Do not commit `.local`, credentials, database exports, private reference books,
uploaded content or WordPress core. The website packages contain only the custom
plugin and theme. The logo synchronization check covers both WordPress and iOS.
