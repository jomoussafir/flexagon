# Flexagon deployment target

Canonical website: https://www.flexagon.fr/. The project was renamed on 18 October 2026.
The deployment history below describes the predecessor installation; its domain references
have been updated as configuration targets, not as evidence of a verified Flexagon deployment.
Live OVH domain mapping, HTTPS, WordPress address changes and package installation still require verification.

# OVH installation

## Deployment status — 13 October 2026

The plugin and Vermeer theme (0.2.0) are installed and active on
https://www.flexagon.fr/. The domain uses a valid HTTPS certificate.
The hosted homepage, problem list and administrator review page load successfully.
WordPress is 7.1.3 and OVH currently runs PHP 8.5.

The full current local catalogue was migrated and verified record by record:
**1,856 problems, three protected figures and three WordPress history records**.
Exactly two publication snapshots were preserved: **Uneven Floor** and
**Equidistant lines**. The admin review page shows the full collection; the member
problem list shows those two publications. No publication notification was sent.
The temporary Catalogue Transfer plugin is now deactivated.

The 103 PDF files plus their manifest passed SHA-256 verification on OVH. The
reference viewer was checked on Colossal Book PDF page 258. The signed-out problem
API and source PDF endpoint return HTTP 401; the storage configuration returns 404
when accessed directly. Static encrypted files are downloadable as ciphertext only.
The hosted session has local preview disabled. Homepage/session/API responses use
private/no-store headers. WordPress uses its query REST route on this installation
(`?rest_route=/lpdj/v1/...`); do not assume `/wp-json/...` pretty permalinks are enabled.

OVH generated a full pre-migration backup on 13 October at 23:10 Paris time and
reported that its download link would be emailed to the account owner. Download and
retain that backup. A restoration has not been tested. Keep a fresh hosting backup
of the migrated database, private ciphertext and key configuration together.

SFTP works through `tools/Connect OVH.command` at
`00950f03e7-sftp.0ea.mcms.ovh.net:2222`. Commander One reported a generic I/O error;
the built-in SFTP client successfully transferred the files. The launcher stores no
password. Keep its window open while transferring, then type `bye` to close it.
The temporary shared connection socket and host-key file are in ignored
`.local/ovh-sftp/`. Its SSH wrapper handles the macOS SFTP client's control-master
option so another transfer can reuse the user-authenticated session.

The data-only export and audit are in ignored `private-data/ovh-transfer/`.
The export excludes accounts, passwords, sessions, progress and email queues.
Its SHA-256 is `9db27fd5cfda9606551e7f17310a52901c195b849b1eb4c6cd0acf295705b1f1`.
Plain and encrypted isolated imports both passed full round-trip checks; all 48
website integration checks and all 22 iPhone tests passed. The iPhone smoke test
loaded the hosted page in WebKit and confirmed sign-in is required for problems.

The Debug iPhone app now uses **https://www.flexagon.fr/** on both simulator
and physical iPhone. Run the updated project from Xcode and sign in with a hosted
WordPress account; local preview accounts were not migrated. It no longer needs
the local website running. The Release native reader remains a separate foundation.

The host’s standard outgoing mail delivered the approved test to the owner’s iCloud
inbox, confirmed on 14 October. Still pending before inviting members: an end-to-end
account-confirmation/reset check, operator/contact details and a tested backup
restoration. A dedicated sender mailbox can be configured later if desired.

## Follow-up checks — 14 October 2026

The live admin collection still contains 1,856 problems (1,852 awaiting review,
two drafts and two publications). Three Squares retains its checked English
version and renders its SVG through `\includegraphics` with Figure 1 referencing.
Anonymous checks reject the draft, its figure and reference PDF (HTTP 401/403).
HTTPS and private/no-store headers remain correct; local-preview access is off.

With the owner's explicit permission, one test message was submitted to
`msfr@mac.com` at **07:23:47 Paris time**. WordPress accepted it through the host's
`mail` transport, with sender `wordpress@flexagon.fr`. The message was
found in the iCloud inbox at 07:23, and the owner confirmed seeing it on 14 October.
The earlier search was scoped to Junk. This confirms delivery of the test message;
the complete account-confirmation/reset flow still needs its own check.
The one-time diagnostic was deactivated, removed from the inactive transfer utility,
and that utility's original source was restored and reloaded to verify an exact match.
No accounts, passwords or problems were changed by the test.

The previous shared SFTP session expired overnight. Future file transfers require
the user to reopen `tools/Connect OVH.command` and sign in again. No password was
stored. The browser upload helper was unavailable, so this diagnostic used the
existing WordPress editor; no new browser permission was needed.

## Before installing

Create a WordPress site in your OVH account using the managed WordPress plan already
discussed. It can use the temporary site address before the final domain is connected.
Use HTTPS and PHP 8.3 or later with DOM/XML and mbstring enabled.

## Upload the project

1. In this project run `npm run build:web` and `npm run package:web`.
2. Sign into the OVH site's WordPress administration.
3. Under Plugins → Add new → Upload, select
   `dist/flexagon-plugin-<version>.zip` and activate it (choose **Replace current
   with uploaded** when updating).
4. Under Appearance → Themes → Add new → Upload, select
   `dist/flexagon-theme-<version>.zip` and activate it.
5. Open the site's homepage. WordPress provides the existing administrator account;
   local-preview credentials are not uploaded.
6. Configure a sender address and authenticated outgoing email with your chosen mail
   provider/OVH settings. Test an actual confirmation, reset and notification email.
7. Create a member test account and verify that only administrators can publish.
8. Add the site operator/contact details and appropriate legal notices before launch.
9. Enable host backups and verify a restoration procedure for the WordPress database.

Only the ZIP packages are deployed. Do not upload the entire repository, `.local`,
`Local access.txt`, or the development WordPress installation.

## Accounts and administrators

Members register through the website and confirm their email. To promote a trusted
reviewer, use WordPress Administration → Users → Edit user → Role → Administrator.
Administrators can edit and publish any problem. Other members cannot change roles.

## Private configuration constants — plugin 0.2.2

`wp-content/lpdj-private-storage.php` (never packaged) may define, besides the storage key:

- `LPDJ_TRUSTED_PROXY_HEADER`: for example `'HTTP_X_FORWARDED_FOR'`. Leave undefined
  until confirmed. Sign-in, registration and upload throttles are counted per client
  address; behind OVH's TLS proxy `REMOTE_ADDR` may be the proxy itself, which would
  make one busy member lock everyone out for fifteen minutes. To check, sign in as an
  administrator and read `window.LPDJ.session.addresses` in the browser console: when
  `remote` is not your own public address but `forwarded` ends with it, define the
  constant. Only the last forwarded entry is used, because that is the hop the proxy
  appended; earlier entries are visitor-supplied.
- `LPDJ_LEGACY_REVIEW_URL`: the predecessor review/PDF viewer linked from the admin
  editor. Define it as `''` once that external service is retired; the link disappears
  without a code change.

## Scheduled tasks (WP-Cron)

Publication notices, administrator alert retries and the overview refresh rely on
WP-Cron, which only runs when a page is requested. On OVH create a scheduled task
(hosting panel → Scheduled tasks / cron) that fetches
`https://flexagon.fr/wp-cron.php?doing_wp_cron` every five minutes, then add
`define('DISABLE_WP_CRON', true);` to `wp-config.php` so visitors no longer trigger it.
This has not yet been configured on the live site.

## Overview cache

Problem overviews (`scope=published` and `scope=review`) are built once and kept in a
transient until any save, publication, upload, deletion, import, display-name change or
account deletion bumps `_lpdj_catalogue_version`. No manual flush is needed; if the
database is restored from a backup, the first request rebuilds it. Member-specific
lists (`scope=mine`) are never cached.

## Mail and caching

The application calls standard `wp_mail`; it does not bundle SMTP credentials. Use a
maintained mail integration or your host's supported configuration. Confirm delivery
to real email addresses in your chosen environment before inviting members.

WP-Cron sends opt-in notices on first publication. Set up your host's scheduled
WordPress cron runner if needed so delivery does not depend on a visitor arriving.
Each recipient receives a separate message. Profile notification preferences provide
the opt-out control.

Exclude authenticated pages, `/wp-json/lpdj/*`, and the protected image action
`admin-ajax.php?action=lpdj_asset` and `admin-ajax.php?action=lpdj_reference` from CDN/page caching. The application also sends
private/no-store headers. Draft content must not be exposed through public caches.

## Private reference PDFs

Admin review has a reference-PDF link for every recorded source occurrence. These
open the recorded PDF page in an administrator-only viewer, with page navigation,
zoom, Open PDF and links back to Admin review/the problem editor. Large books retain
their original page numbering across separate PDF parts. The native PDF download
also requires an administrator session; ordinary members never receive reference links.

The local launcher mounts `private-data/references` outside WordPress. It contains
`manifest.json` and 103 existing PDF parts for 78 source entries. These files are
excluded from Git and both deployment ZIPs. The collection's 1,863 occurrences all
map to an existing file and page. The viewer code is included in the theme package.

For a host with a writable directory outside the web root, use the original
plaintext mode and set `LPDJ_REFERENCE_DIR` to that private directory.

This OVH Managed WordPress installation exposes only the WordPress directory and
has no writable parent directory. Its library therefore uses **AES-256-GCM
authenticated encryption**. Run `tools/encrypt-ovh-library.mjs` against the checked
export and original PDFs to prepare `private-data/ovh-transfer/encrypted/`.
The dedicated 32-byte storage key and generated PHP config remain private and are
excluded from Git and deployment packages.

Production layout (relative to the SFTP root):

- `/wp-content/lpdj-private-storage/`: `catalogue.json.lpdj` and encrypted references.
- `/wp-content/lpdj-private-storage/references/`: `manifest.json.lpdj` and 103 `.pdf.lpdj` files.
- `/wp-content/lpdj-private-storage.php`: key and directory configuration, guarded
  by `ABSPATH` so direct requests return 404. Included by the main plugin.

Storage directories use permissions 700 and files/config use 600. The serving
process can still read ciphertext; encryption protects it even when a direct
static URL is accessible. Never put plaintext books or the export in this directory.
Decryption happens only inside the existing administrator-authorized PDF endpoint.
Files are authenticated against their original basenames to reject substitutions.

**Back up the PHP key configuration and ciphertext together** along with the
WordPress database. Losing the key makes the encrypted files unrecoverable.
Do not put reference books or the key in WordPress Media, the theme, or Git.
The ordinary local preview continues using its original private plaintext library.

## Source figure library — prepared, not yet uploaded

Figures traced from the reference books (`tools/extract-figures.py`) form a second
private library, read by plugin 0.2.3+ through `LPDJ_FIGURE_DIR`. It is not on OVH yet.
To deploy it:

1. Trace the pages you need locally (`npm run figures:extract -- --all --problems`),
   check `private-data/figures/review/`, and redraw the figures to offer
   (`npm run figures:redraw`); only redrawn figures appear in the editor.
2. Run `npm run figures:encrypt`. It reuses `private-data/ovh-transfer/storage-key`
   and writes `private-data/ovh-transfer/encrypted/figures/` plus `figures-audit.json`.
3. Over SFTP (`tools/Connect OVH.command`) upload that directory to
   `/wp-content/lpdj-private-storage/figures/` with permissions 700/600, keeping the
   `manifest.json.lpdj` and per-book subdirectories.
4. Add `define('LPDJ_FIGURE_DIR', LPDJ_TRANSFER_DIR . '/figures');` to
   `/wp-content/lpdj-private-storage.php`.
5. Install the plugin and theme packages that contain the figure picker, then open a
   problem in the editor and check **Source figures**.

Figures attached to problems are copied into the WordPress database like uploaded
images, so the migrated catalogue carries them even without the library. Re-upload
the encrypted directory after tracing more pages; the audit file lists SHA-256 sums.

## Data and next integrations

Production uses the host's standard WordPress MySQL database. The local preview uses
SQLite through the official WordPress Playground runtime. The current-data migration
and delivery of the approved email test have been verified on OVH.

The local collection now contains 1,856 problems, including two published problems.
The historical import described in `migration.md` must not replace newer WordPress
edits or publication snapshots during deployment. The Debug iPhone client displays
the shared website and can use the hosted HTTPS URL through `CommunityWebsiteURL`.
The Release native reader still requires authentication and API integration. The
public feed from the old app is not enabled in the community edition.

## Administrator email alerts — plugin 0.2.1

Implemented locally; production installation is pending verification.
Under **Settings → General → Flexagon — email alerts**, two switches
control alerts for new confirmed users and problems submitted for review. Both
start enabled and send to the current, confirmed WordPress `admin_email` setting.
No alerts are generated for existing users, the imported catalogue, draft saves or
repeated Submit clicks while a problem is already submitted. Resubmission after
changes or an administrator return generates a fresh alert. Review links require
administrator authentication. A mail failure gets up to three WP-Cron retries.

The live administrator login is **msfr@mac.com**; **ovhadmin** is its display name,
not its login. Production passwords are not stored in this repository.

## Sign-in layout — 16 October 2026

Theme 0.2.1 is deployed on OVH. The sign-in page no longer renders the large
Poincaré icon, and the form is centered at a maximum width of 440 px. The small
header icon and the other account pages are unchanged. The build and local preview
passed, and the live page was checked: zero images in the sign-in layout and one
header image. The existing admin session was used in the WordPress theme editor
because Chrome's file upload helper still lacks file-URL permission. The saved
JavaScript was reloaded and matched the local build exactly.

This deployed the theme only. The separately prepared administrator email-alert
plugin 0.2.1 remains pending installation (60 isolated integration checks passed).
