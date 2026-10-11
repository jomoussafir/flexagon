# Le Problème du Jour theme

Responsive French interface using the original Poincaré disk logo, with bilingual
problem content and accessible form labels. Vanilla TypeScript is bundled with esbuild;
the shared KaTeX renderer supplies mathematics, uploaded figures and local references.

Run `npm run build:web` from the repository root after modifying `src/`. The generated
assets and local math fonts are packaged by `npm run package:web`.

The matching plugin must be active. Routes use URL fragments so the frontend works
without custom server rewrite rules. REST URLs support both plain and pretty WordPress
permalinks. Logged-in pages and API responses are marked private/no-store.
