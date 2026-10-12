import { build } from 'esbuild';
import { cp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const theme=path.join(root,'wordpress/themes/le-probleme-du-jour');
await mkdir(path.join(theme,'assets'),{recursive:true});
await build({entryPoints:[path.join(theme,'src/app.ts'),path.join(theme,'src/app.css')],outdir:path.join(theme,'assets'),bundle:true,minify:true,target:['safari16','chrome110'],logLevel:'info'});
// Keep the font assets matched to the established vendored KaTeX renderer.
await cp(path.join(root,'node_modules/katex/dist/fonts'),path.join(theme,'assets/katex/fonts'),{recursive:true});
await cp(path.join(root,'node_modules/katex/dist/katex.min.css'),path.join(theme,'assets/katex/katex.min.css'));
await cp(path.join(root,'shared/latex/KATEX-LICENSE'),path.join(theme,'assets/katex/LICENSE'));
// Load the PDF renderer only on the administrator reference page.
const pdf=path.join(root,'node_modules/pdfjs-dist'), pdfOut=path.join(theme,'assets/pdfjs');
await mkdir(pdfOut,{recursive:true});
for(const name of ['pdf.mjs','pdf.worker.mjs'])await cp(path.join(pdf,'legacy/build',name),path.join(pdfOut,name));
for(const name of ['cmaps','standard_fonts','wasm'])await cp(path.join(pdf,name),path.join(pdfOut,name),{recursive:true});
await cp(path.join(pdf,'LICENSE'),path.join(pdfOut,'LICENSE'));
console.log('WordPress theme built.');
