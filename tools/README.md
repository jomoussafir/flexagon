# Project tools

- `start-web.mjs`: persistent, loopback-only WordPress Playground preview; local email capture.
- `build-web.mjs`: browser assets and matching math fonts for the WordPress theme.
- `package-web.py`: deployment ZIPs containing only the plugin and theme.
- `sync_branding.py`: copy/check the common logo for iOS and WordPress.

Run these through the root package scripts. `Open Website.command` is the Finder shortcut.
The local database and credentials are excluded from source control. Migration of the
old editorial database remains a separate step; no export/import is silently performed.
