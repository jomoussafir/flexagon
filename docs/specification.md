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
French and English versions can be approved and published separately. Show the only
published language when just one exists; provide EN/FR selection when both exist.
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

## Status

The WordPress website implements the accounts, submission, review and publication
workflow locally. OVH deployment and real email delivery, the historic database import,
and native mobile authentication/API integration remain pending. See verification.md.
