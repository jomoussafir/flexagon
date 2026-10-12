# Le Problème du Jour plugin

Activate alongside the matching theme. Requires PHP 8.2+, DOM/XML and mbstring, and
WordPress 6.8+; tested with PHP 8.3 and WordPress 7.1.3 locally.

Records use non-public WordPress post types with protected metadata. Draft state and
published snapshots are separate. A revision counter plus per-record lock rejects
stale saves and uploads. Admins can publish only checked language versions; members cannot
forge approval or edit another member's draft. Approval survives the first Save & Publish.

Figure uploads accept a conservative SVG subset and validated PNG/JPEG, with 2 MiB per
image, 20 figures per problem and 200 image records per account. Files are served through
an authenticated endpoint. No public `wp-content/uploads` paths expose private figures.

WordPress mail is used for confirmation/reset and opted-in first-publication notices.
The local launcher explicitly sets both `WP_ENVIRONMENT_TYPE=local` and
`LPDJ_LOCAL_PREVIEW=true`, enabling a captured mailbox accessible only to an admin.
Do not set those constants in production. Delivery of notifications uses WP-Cron;
configure a reliable scheduled runner on the production host if traffic is low.

Deactivating the plugin preserves content. There is no destructive uninstall hook.
