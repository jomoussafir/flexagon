# Project tools

- `start-web.mjs`: persistent, loopback-only WordPress Playground preview; local email capture.
- `build-web.mjs`: browser assets and matching math fonts for the WordPress theme. It
  deletes and recreates `assets/katex` and `assets/pdfjs` on every run, so stray copies
  never reach a package; `package-web.py` also refuses Finder duplicates such as `pdf 2.mjs`.
- `package-web.py`: deployment ZIPs containing only the plugin and theme.
- `sync_branding.py`: copy/check the common logo for iOS and WordPress.

Run these through the root package scripts. `Open Website.command` is the Finder shortcut.
The local database and credentials are excluded from source control. Migration of the
old editorial database remains a separate step; no export/import is silently performed.

## OVH catalogue migration

- `export-catalogue.py`: read-only snapshot of the current local WordPress content,
  selected metadata and reference checksums; excludes account/password/session data.
- `encrypt-ovh-library.mjs`: AES-256-GCM encryption for the checked export and private
  PDFs on hosts without a writable directory outside the web root. Key/config stay
  under ignored `private-data/ovh-transfer/`; never add them to Git or plugin ZIPs.
- `lpdj-catalogue-transfer/`: temporary administrator-only WordPress importer with
  resumable transactional batches and record-by-record verification before restoring
  existing publication snapshots. Only imports into an empty community catalogue.
  Deactivate after completion. It sends no publication notifications.
- `Connect OVH.command` and `ovh-sftp-ssh.sh`: user-entered SFTP authentication with
  a reusable connection while the terminal stays open; no stored password.

`tests/catalogue-transfer.test.mjs` is an opt-in isolated test against the private
export. It does not modify the working local site or OVH. Set `LPDJ_ENCRYPTED_TEST=1`
to verify encrypted interoperability, tamper rejection and the full import.
See `docs/ovh-setup.md` for deployment and backup details.
