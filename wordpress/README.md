# WordPress community website

The custom plugin and theme are implemented and runnable locally. Start from the
repository root with `npm start`, or double-click `Open Website.command`.

The plugin owns accounts, private problem records, revisions, images and publication.
The theme provides registration, login/reset, catalogue, submission/editor, review,
profile, help and privacy pages. All problem read endpoints require a verified account.
Only users with WordPress `manage_options` (administrators) can publish.

The frontend uses WordPress cookies and REST nonces. Each account starts as
`lpdj_member`, a role with only the core `read` capability. Email confirmation is
required before sign-in. The ordinary WordPress self-registration route is disabled;
the plugin's registration form applies verification and the correct role.

The public theme is French; problem content supports French and English separately.
Images are stored as bounded, base64-encoded records in the database, not publicly
accessible Media Library files. Access is checked on each image request. This simple
storage model is suitable for an initial small community; large image collections
will need protected object storage or a private filesystem adapter later.

## Build and deploy

Run `npm run build:web` and `npm run package:web`. Upload the two generated ZIPs through
WordPress's plugin/theme upload controls. See [OVH setup](../docs/ovh-setup.md).

The server does not need Node.js. The browser bundle and math fonts are built before
packaging. The WordPress runtime, accounts, database, local mail and credentials are
excluded from packages.

This is a supported LaTeX subset, not a TeX compiler. Math rendering is browser-side
using KaTeX with `trust:false`. The server validates publication permissions, required
fields, figure ownership/existence and label references. The editor validates rendering
before submission/publication; arbitrary TeX packages and TikZ are not compiled.
