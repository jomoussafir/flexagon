# Shared branding

The logo is copied without modification from the original iPhone app:
the Poincaré disk with the regular {7,3} tiling associated with the Klein quartic,
with white outside the disk.

- `logo.png`: original opaque 1024 × 1024 app icon.
- `logo.svg`: original vector artwork from the validation website.
- `favicon.png`: existing small browser icon.
- `manifest.json`: SHA-256 hashes of the inherited files.

Run `python3 tools/sync_branding.py` from the repository root to update the iOS and
WordPress copies. Add Android export targets when that project exists.
