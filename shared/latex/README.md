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

This source is bundled into the WordPress theme. The plugin serves protected uploads
and validates publication permissions, figure names and label references. KaTeX has
been updated to 0.19.0 with matched fonts to resolve the prior trust-guard advisory.
The iPhone reader already supports HTML statements and included figures, but its
new authenticated WordPress integration is still pending.

Run `npm run test:latex` from the repository root.
