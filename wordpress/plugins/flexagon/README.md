# Flexagon plugin

Activate alongside the matching theme. Requires PHP 8.2+, DOM/XML and mbstring, and
WordPress 6.8+; tested with PHP 8.3 and WordPress 7.1.3 locally.

Records use non-public WordPress post types with protected metadata. Draft state and
published snapshots are separate. A revision counter plus per-record lock rejects
stale saves and uploads. Admins can publish only checked language versions; members cannot
forge approval or edit another member's draft. Approval survives the first Save & Publish.

Figure uploads accept a conservative SVG subset, validated PNG/JPEG and one-page PDFs
(static drawings only: catalog dictionaries with actions, scripts, links or embedded files
are refused, and a PDF needs its rendered preview image), with 2 MiB per file, 20 figures
per problem and 200 image records per account. Files are served through an authenticated
endpoint; `format=pdf` returns the vector master. No public `wp-content/uploads` paths
expose private figures.

The private figure library (`LPDJ_FIGURE_DIR`, defaulting to a `figures` directory
beside the reference directory) is traced from the reference books by
`tools/extract-figures.py` and redrawn by `tools/redraw-figures.py`; only manifest
entries with a `redrawn` block are served. Administrators list it, preview it and attach entries to a
problem through `GET /figures` and `POST /problems/{id}/figures`; attaching copies the
PDF and SVG into a protected asset named `<figure-id>.pdf`. Like the books, the library
is never served to members; encrypted storage works as for the references.

WordPress mail is used for confirmation/reset and opted-in first-publication notices.
Administrator alerts are enabled by default under **Settings → General →
Flexagon — email alerts**. They use the current WordPress administration
email address (`admin_email`), independently of a member's publication preference.
A completed email confirmation sends one new-user alert. Entering the submitted
state sends one review alert with an authenticated editor link; resubmitting after
changes or a return sends a new alert. Draft saves, repeated Submit while already
submitted, and imports do not send alerts. Existing users/problems are not backfilled.
Each alert is attempted immediately. WordPress mail failures are retried up to three
times at ten-minute intervals through WP-Cron; successful attempts are not repeated.
Disabling an alert also cancels its queued retries. A successful mail call means the
host accepted the message, not proof of inbox delivery.
The local launcher explicitly sets both `WP_ENVIRONMENT_TYPE=local` and
`LPDJ_LOCAL_PREVIEW=true`, enabling a captured mailbox accessible only to an admin.
Do not set those constants in production. Delivery of notifications uses WP-Cron;
configure a reliable scheduled runner on the production host if traffic is low.

Deactivating the plugin preserves content. There is no destructive uninstall hook.

Administrators have a Members roster (`GET /users`, the theme's `#/membres` page) listing
every account's email with the number of problems it submitted for review and the number
published. Counts are cached per catalogue version; the account list is read fresh. From
it an administrator can delete (`DELETE /users/{id}`, with confirmation) a non-admin
account that has no published problems; its drafts and submissions go with it, and
publications are never affected. A per-member "No review" flag (`POST /users/{id}`,
default on for new accounts) lets a member publish their own problems directly; toggling
it only affects future publishing and never publishes problems already submitted.

Original source PDFs are served only to administrators by `lpdj_reference`. Configure
`LPDJ_REFERENCE_DIR` to a private directory outside the web root with `manifest.json`
and the matching PDF files. The local launcher mounts the ignored private library.
Reference metadata is never included in published snapshots or member responses.
