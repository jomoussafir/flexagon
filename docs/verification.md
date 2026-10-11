# Website verification — 11 October 2026

## Current website

- WordPress 7.1.3 / PHP 8.3 running in the official local Playground runtime.
- 34 isolated integration checks pass: email confirmation, cookie/nonces, member/admin
  permissions, private drafts and images, safe/unsafe SVG uploads, stale revision
  rejection, FR/EN publication, first Save & Publish approval preservation, published
  snapshot isolation, personal progress, revision history, return notes, profile
  images, opt-out notifications, password reset and account/draft deletion.
- All 8 shared LaTeX tests pass after the KaTeX 0.19.0 security update.
- Website asset build succeeds; npm audit reports zero known vulnerabilities.
- Plugin/theme deployment ZIPs are generated and checked for archive integrity.
- The original logo matches the iOS and website copies byte for byte.
- Browser inspection covered signed-out landing/registration, administrator sign-in,
  the empty collection, editing, first-save publication, math/currency preview and
  the published reader. Desktop (1280 px) and narrow/mobile (390 px) layouts checked.
- The temporary browser-test problem was removed; the delivered catalogue starts empty.
- Local emails are captured in an admin-only mailbox. No real email was sent.

The integration suite uses a separate disposable database on port 9401. The persistent
preview is on port 9400 and is bound to loopback only. Local state and credentials are
ignored by Git and excluded from deployment packages.

## Remaining environment checks

No OVH deployment, production SMTP delivery, production MySQL staging test, physical
iPhone browser test, native mobile account integration, historic editorial import,
Android build or GitHub upload has been performed. Production operator/contact details
must be supplied before the legal/privacy page is finalized for a public launch.
The website supports a documented LaTeX subset; it does not compile arbitrary TeX/TikZ.

## Earlier foundation checks

The copied iPhone app had a successful simulator Debug build in the initial foundation
step. Its bundle ID is isolated and its original public feed is unset. No native app
code was changed during this website implementation and no iOS rebuild was needed.
The historical files under ios describe the original app, not the new WordPress client.
