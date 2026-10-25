# WordPress API v1

Base URL: the site's `rest_url('lpdj/v1/')`, normally `/wp-json/lpdj/v1/`.

| Method and endpoint | Purpose |
| --- | --- |
| `GET /session` | Current member, CSRF tokens, category/source definitions; administrators also receive `addresses` (client/remote/forwarded) to verify the proxy setting |
| `POST /auth/register` | Email, pseudo, password, consent and notification preference |
| `POST /auth/verify` | Single-use email confirmation token |
| `POST /auth/login`, `/auth/logout` | Website cookie session |
| `POST /auth/resend`, `/auth/forgot`, `/auth/reset` | Verification resend and password recovery |
| `GET /problems?scope=published\|mine\|review` | Overview records; review is administrator-only |
| `GET /users` | Admin-only roster: each account's email, confirmed/admin flags, and submitted/published problem counts |
| `POST /users/{id}` | Admin-only: set a member's `noReview` flag. It only affects the member's future publishing and never publishes existing submissions |
| `DELETE /users/{id}` | Admin-only: delete a non-admin account that has no published problems; its drafts and submissions are removed |
| `POST /problems` | Create an empty private draft |
| `GET /problems/{id}` | Published snapshot only |
| `GET /problems/{id}?context=edit` | Author/admin draft with current revision |
| `POST /problems/{id}` | Save, submit, publish, return or unpublish |
| `DELETE /problems/{id}` | Delete an unpublished draft and its assets/history |
| `GET /problems/{id}/reference?index=0&page=…` | Admin-only source PDF metadata; page defaults to the recorded occurrence |
| `GET /problems/{id}/history` | Author/admin revision history |
| `POST /problems/{id}/progress` | Personal unseen/bookmarked/attempted/solved state |
| `POST /assets` | Multipart file, problem ID, current revision; problem 0 for avatar. A `.pdf` file needs a `preview` image part |
| `GET /figures?problem=…&source=…&page=…&default=1` | Admin-only private library of redrawn reference-book figures; with `default=1` the filter opens on the problem's own source page (`source`, `page` in the response) |
| `DELETE /problems/{id}/assets/{name}` | Detach a figure from the draft at the current `revision`; the record is deleted unless the published snapshot still shows it |
| `POST /problems/{id}/figures` | Admin-only: attach library figure `figure` at the current `revision` as asset `<figure-id>.pdf` |
| `POST /profile` | Pseudo, notifications, optional owned avatar ID |
| `DELETE /account` | Member account deletion, requiring current password |

Every problem/asset/profile route requires a confirmed authenticated account.
Browser requests send WordPress cookies and `X-WP-Nonce`. Public account forms require
a same-origin `Origin` and `X-LPDJ-Form` nonce. Login returns fresh session tokens.
API responses are not public cache entries.

A draft contains `id`, `revision`, `state`, `category`, `difficulty` (1–5), `source`,
`keywords`, `versions` (language key → `language`, `title`, `latex`, `approved`), `assets` (filename →
ID/mime/url, plus `pdf` for a PDF figure whose `url` is its preview image), `reviewNote`, `updated` and `author` (public pseudonym only).

Versions support 1–20 user-named languages, including languages outside the suggested
list. Keys are stable lowercase identifiers (`en`, `es`, `pt-br`, or `und-xxxxxxxx`
for a custom language); the `language` field is the displayed name, up to 60 characters.
Each name must be unique (case-insensitive). Each title is limited to 300 characters
and each statement to 60 KB, with a 600 KB limit across all statements. Missing
language names on old FR/EN records are presented as French/English. New drafts
start with one English version, which the author may rename. Submitting a versions
map replaces the draft's language set; omitted languages remain in an existing
published snapshot until the administrator explicitly republishes. No language is
required, and clients must not assume FR/EN exist.

The published overview includes the current user's `progress` and language names,
but omits full statements. Published and review overviews are served from a shared
cache that every write route invalidates; `progress` and `editable` are added per request. It supplies the website's personal Progress grids;
`unseen`, `bookmarked` and `attempted` all count as unsolved.

Save requests contain the current revision and action `save`, `submit`, `publish`,
`return` or `unpublish`. A stale revision receives HTTP 409. Administrators may
approve/publish/return/unpublish any problem; a member whose account carries the
`noReview` flag may also publish (and self-approve) their own problems. `return` and
`unpublish` remain administrator-only. The session user carries `canPublish`. Non-admin edits invalidate affected approvals.
Only approved languages and their referenced assets enter the published snapshot;
draft edits never replace it until another explicit publication.

Assets are returned with protected same-origin URLs. A mobile client must use an
authenticated image transport; these are not a public CDN. WordPress Application
Passwords over HTTPS are compatible with member-authorized REST routes, but the
native sign-in/authorization experience and image loading still need implementation.
The website account-form endpoints intentionally enforce browser same-origin rules;
do not embed the WordPress administrator credentials in an app.

## Original reference books

Only admin review overviews and admin edit responses include `references` (source ID,
title, occurrence index, PDF page, printed page and problem number). Publication never
copies these into the reader snapshot. The reference endpoint selects a part from the
private file manifest and returns the total page count, part range, page inside the
part and an authenticated PDF URL. The protected `lpdj_reference` admin-ajax action
checks administrator permissions on every download and sends `private, no-store`.
There is no public reference endpoint, file upload or arbitrary-path download route.

## Website addresses in email

Confirmation, reset, publication and review emails link to `#/confirm`, `#/reset`,
`#/problem/{id}`, `#/profile` and `#/edit/{id}`. The historic French addresses
(`#/confirmer`, `#/reinitialiser`, `#/probleme`, `#/profil`, `#/editer`) remain
valid aliases so links in older messages keep working.
