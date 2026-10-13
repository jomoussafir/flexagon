# Agreed community edition

## Platforms and ownership

One private GitHub repository for iOS, WordPress customisations, shared code/assets
and a future Android client. OVH hosts the WordPress website. WordPress owns the
accounts, problem database and publication workflow. Supabase is not required.
The GitHub owner and remote URL have not yet been supplied.

## Accounts and roles

Users register with pseudonym, email and password and confirm their email before
using the service. A profile can include an uploaded picture or drawing. Registered
members read published problems and submit their own problems. Admins can also submit,
review, edit, return and publish. Roles cannot be self-assigned. Password reset,
account deletion, and opt-in new-problem notifications are planned. Production email
delivery will be configured and tested. Mobile sign-in needs a supported integration.

## Problems and publication

LaTeX text with uploaded figures referenced through `\includegraphics`, captions and
local `\label` / `\ref`; support SVG, PNG and JPEG with appropriate validation.
Authors can add and name several language versions. Each version has its own title,
LaTeX statement and approval. Display the only published language when just one exists;
provide a selector with language names when several are published. Figures are shared.
Keywords, difficulty 1–5, mathematical category and source references are editable.

The workflow is draft → submitted → published, or returned for changes. Admins may
make minor corrections and publish directly. Substantial mathematical changes should
be returned with an explanation. Preserve author attribution and revision history.
Changes to a published problem must be reviewed before replacing its published version.

## Initial content and user experience

Start with an empty published catalogue. Copy the full existing editorial collection
later as private unpublished records, preserving review information. Importing does
not automatically publish. Both mobile clients use exactly the published versions
available to signed-in website members. Retain the existing app logo with a white
exterior, source grouping/order, five mathematical categories and progress choices.

The landing page opens About with the text “Curated list of mathematical puzzles”,
without a repeated About heading. Its banner shows the icon, “Le Problem du jour”,
and About, Problem, Sign In and Create Account links. Problem opens the selection
page after sign-in. Members also see Submit a problem, Progress and an account menu.
Progress defaults to solved problems, with All, Unseen, Bookmarked, Attempted, Solved
and Unsolved filters; Unsolved combines the first three unfinished states. Search and filters by
category, difficulty or source combine with grouping by the same fields. Clickable cards
show title, numeric difficulty, status and source. Dense cards start at 152 px wide
and 94 px high on desktop, with full titles/source information in tooltips. Difficulty colours run from pale blue
to purple; group counts and bars show completion. Load 24 cards per group at a time.

## Status

The WordPress website implements the accounts, submission, review and publication
workflow locally. The historic import contains 1,854 unpublished records; one remaining
record awaits authenticated export. OVH deployment, real email delivery and native mobile
authentication/API integration remain pending. See verification.md.
