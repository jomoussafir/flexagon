# WordPress API v1

Base URL: the site's `rest_url('lpdj/v1/')`, normally `/wp-json/lpdj/v1/`.

| Method and endpoint | Purpose |
| --- | --- |
| `GET /session` | Current member, CSRF tokens and category/source definitions |
| `POST /auth/register` | Email, pseudo, password, consent and notification preference |
| `POST /auth/verify` | Single-use email confirmation token |
| `POST /auth/login`, `/auth/logout` | Website cookie session |
| `POST /auth/resend`, `/auth/forgot`, `/auth/reset` | Verification resend and password recovery |
| `GET /problems?scope=published\|mine\|review` | Overview records; review is administrator-only |
| `POST /problems` | Create an empty private draft |
| `GET /problems/{id}` | Published snapshot only |
| `GET /problems/{id}?context=edit` | Author/admin draft with current revision |
| `POST /problems/{id}` | Save, submit, publish, return or unpublish |
| `DELETE /problems/{id}` | Delete an unpublished draft and its assets/history |
| `GET /problems/{id}/history` | Author/admin revision history |
| `POST /problems/{id}/progress` | Personal unseen/bookmarked/attempted/solved state |
| `POST /assets` | Multipart file, problem ID, current revision; problem 0 for avatar |
| `POST /profile` | Pseudo, notifications, optional owned avatar ID |
| `DELETE /account` | Member account deletion, requiring current password |

Every problem/asset/profile route requires a confirmed authenticated account.
Browser requests send WordPress cookies and `X-WP-Nonce`. Public account forms require
a same-origin `Origin` and `X-LPDJ-Form` nonce. Login returns fresh session tokens.
API responses are not public cache entries.

A draft contains `id`, `revision`, `state`, `category`, `difficulty` (1–5), `source`,
`keywords`, `versions` (language key → `language`, `title`, `latex`, `approved`), `assets` (filename →
ID/mime/url), `reviewNote`, `updated` and `author` (public pseudonym only).

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
but omits full statements. It supplies the website's personal Progress grids;
`unseen`, `bookmarked` and `attempted` all count as unsolved.

Save requests contain the current revision and action `save`, `submit`, `publish`,
`return` or `unpublish`. A stale revision receives HTTP 409. Only an administrator may
approve/publish/return/unpublish. Non-admin edits invalidate affected approvals.
Only approved languages and their referenced assets enter the published snapshot;
draft edits never replace it until another explicit publication.

Assets are returned with protected same-origin URLs. A mobile client must use an
authenticated image transport; these are not a public CDN. WordPress Application
Passwords over HTTPS are compatible with member-authorized REST routes, but the
native sign-in/authorization experience and image loading still need implementation.
The website account-form endpoints intentionally enforce browser same-origin rules;
do not embed the WordPress administrator credentials in an app.
