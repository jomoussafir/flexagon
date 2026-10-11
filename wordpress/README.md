# WordPress website

Prepared for an OVH Managed Hosting for WordPress installation.

`plugins/le-probleme-du-jour/` will contain the custom accounts, problem records,
submission/review workflow, protected figure delivery and mobile endpoints.
`themes/le-probleme-du-jour/` will contain the website presentation. The existing app
logo, its SVG source and favicon are already copied into the theme assets folder.

These are development folders, not yet an installable plugin or theme. Do not upload
this whole repository into the web root. WordPress core is installed and maintained
on OVH; only finished custom plugin/theme packages will be deployed.

The site will use WordPress as the single account and publication system. Supabase
is not part of the chosen architecture. Email verification and mobile sign-in need
additional integration. The shared TypeScript renderer is reusable source; it is not
a PHP plugin and will need a browser build/integration for WordPress.

See `../docs/specification.md` and `../docs/ovh-setup.md`.
