# Shared LaTeX and figures

Copied from the original validation website's renderer. Includes the vendored KaTeX
module and its license, plus the existing mathematical-text and figure regression tests.

Supported figure workflow: `\includegraphics`, `\begin{figure}`, `\centering`, plain
captions, `\label` and `\ref`, with numbering local to each problem. Width can be a
fraction of `\linewidth` or `\textwidth`. This is a supported LaTeX subset, not a full
TeX engine or arbitrary package/TikZ compiler.

The caller must supply a trusted mapping of uploaded figure filenames to approved
image URLs or embedded data. Never pass user-supplied arbitrary URLs as trusted files.
SVG uploads will need validation before being stored and served.

This source is not yet connected to WordPress. Browser packaging, protected uploads
and server-side publication validation remain implementation work. The iPhone reader
already supports HTML statements and included figures.

Run `npm run test:latex` from the repository root.
