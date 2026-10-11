# Editorial migration plan

No live database migration has been performed during repository setup.

1. Export the latest private editorial catalogue: it combines seed records and saved
   database edits. A copy of seed JSON alone misses subsequent reviewer corrections.
2. Export revision history and copy figure assets and their stable filenames. Keep
   source PDF references and reviewer-only originals available through protected access.
3. Preserve IDs, both language versions, original LaTeX, validation flags, sources,
   categories, difficulty, notes, figures and provenance.
4. Import into the new system as unpublished records, retaining validation information
   separately. Publication in the new edition remains an explicit admin action.
5. Compare record counts, language coverage, figure links and representative problem
   previews, including references and PDF page associations.
6. Keep the old app and editorial website available throughout the copy. Plan any final
   switch separately so edits made during migration are reconciled.

The public iPhone feed contains only published content and cannot replace this export.
Store temporary exports under ignored `private-data/` or `exports/`, with access limited
to reviewers. Do not commit user records, reference books or private database backups.
The small inherited iOS pilot files are regression fixtures, not the live database.
