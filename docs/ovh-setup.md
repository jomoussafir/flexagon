# OVH installation

The website is built locally. No OVH account changes or deployment have been performed.

## Before installing

Create a WordPress site in your OVH account using the managed WordPress plan already
discussed. It can use the temporary site address before the final domain is connected.
Use HTTPS and PHP 8.3 or later with DOM/XML and mbstring enabled.

## Upload the project

1. In this project run `npm run build:web` and `npm run package:web`.
2. Sign into the OVH site's WordPress administration.
3. Under Plugins → Add new → Upload, select
   `dist/le-probleme-du-jour-plugin-0.2.0.zip` and activate it.
4. Under Appearance → Themes → Add new → Upload, select
   `dist/le-probleme-du-jour-theme-0.2.0.zip` and activate it.
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

For OVH, copy the private reference directory to a directory **outside the web root**
using your hosting file transfer, and add this line to the production `wp-config.php`
with that directory's actual absolute path:

```php
define('LPDJ_REFERENCE_DIR', '/absolute/private/path/references');
```

Do not put reference books in WordPress Media/uploads, the theme, or a public static
folder. Include this private directory in backups. Check PDF access with both an
administrator and an ordinary member after deployment. If the library is not installed,
the reference viewer reports that the PDF is unavailable instead of using a public copy.

## Data and next integrations

Production uses the host's standard WordPress MySQL database. The local preview uses
SQLite through the official WordPress Playground runtime. This implementation was
tested locally; run the account/submission/publication checks again on OVH staging.

The local collection contains 1,854 imported, unpublished problems. Follow
`migration.md` when moving the private review data to production. The existing native iPhone reader
still requires member authentication and the new API integration. The public feed from
the old app is intentionally not enabled in the community edition.
