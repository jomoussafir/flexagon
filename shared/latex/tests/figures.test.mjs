import {test} from 'node:test';
import assert from 'node:assert/strict';
import {render,figureNames} from '../render.ts';
const figures={'map.svg':'data:image/svg+xml;base64,PHN2Zy8+'};
test('inline vector figures and forward references use local numbering',()=>{
 const s=String.raw`See Figure~\ref{fig:map}.
\begin{figure}
\centering
\includegraphics[width=0.65\linewidth]{map.svg}
\caption{The map}
\label{fig:map}
\end{figure}
Then $x^2$.`;
 const html=render(s,figures);
 assert.ok(html.includes('See Figure 1.'));assert.ok(html.includes('width:65%'));assert.ok(html.includes('Figure 1 — The map'));assert.equal((html.match(/<img /g)||[]).length,1);assert.ok(!html.includes('<p><figure'));assert.ok(html.includes('class="katex"'));
 assert.deepEqual(figureNames(s),['map.svg']);assert.ok(render(s,figures).includes('Figure 1'));
});
test('two figures receive distinct numbers',()=>{
 const html=render(String.raw`See \ref{second}.
\begin{figure}\includegraphics{map.svg}\label{first}\end{figure}
\begin{figure}\includegraphics{map.svg}\label{second}\end{figure}`,figures);
 assert.ok(html.includes('See 2.'));assert.ok(html.includes('Figure 1'));assert.ok(html.includes('Figure 2'));
});
test('unknown files, external paths, labels and unsafe width options are rejected',()=>{
 for(const s of [String.raw`\includegraphics{https://bad.example/x.svg}`,String.raw`\ref{missing}`,String.raw`\includegraphics[onerror=alert(1)]{map.svg}`,String.raw`\begin{figure}\includegraphics{map.svg}\label{x}\end{figure}\begin{figure}\includegraphics{map.svg}\label{x}\end{figure}`])assert.throws(()=>render(s,figures));
});
