// @ts-ignore Vendored KaTeX, shared by previews and publication.
import katex from './katex.mjs';
export const escapeHTML=(s:string)=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
export const figureNames=(statement:string)=>Array.from(statement.matchAll(/\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}/g),m=>m[1]);
export function render(statement:string,figures:Record<string,string>={}){
 const tokens:string[]=[];
 const blocks:string[]=[];
 const labels=new Map<string,number>();
 let number=0;
 const image=(code:string,n:number)=>{
  const match=/\\includegraphics(?:\[([^\]]*)\])?\{([^}]+)\}/.exec(code);
  if(!match)throw Error('Each figure needs an includegraphics command.');
  const src=figures[match[2]];
  if(!src)throw Error('Unknown figure: '+match[2]+'. Use an attached figure filename.');
  let width=100;
  if(match[1]){
   const size=/^width=(0?\.\d+|1(?:\.0+)?)\\(?:textwidth|linewidth)$/.exec(match[1].replace(/\s/g,''));
   if(!size||Number(size[1])<=0)throw Error('Use a width such as width=0.7\\linewidth.');
   width=Number(size[1])*100;
  }
  const caption=/\\caption\{([^{}]*)\}/.exec(code)?.[1];
  const label=/\\label\{([^{}]+)\}/.exec(code)?.[1];
  if(label){if(labels.has(label))throw Error('Duplicate figure label: '+label);labels.set(label,n)}
  const rest=code.replace(/\\includegraphics(?:\[[^\]]*\])?\{[^}]+\}|\\caption\{[^{}]*\}|\\label\{[^{}]+\}|\\centering/g,'').trim();
  if(rest)throw Error('Unsupported figure content. Use includegraphics, caption and label.');
  return '<figure style="margin:1.5em auto;text-align:center"><img style="display:block;width:'+width+'%;max-width:100%;height:auto;margin:auto" alt="'+escapeHTML(caption||'Figure '+n)+'" src="'+escapeHTML(src)+'"><figcaption>Figure '+n+(caption?' — '+escapeHTML(caption):'')+'</figcaption></figure>';
 };
 // Number figures in statement order; resolve labels after every figure is known.
 let text=statement.replace(/\\begin\{figure\}(?:\[[^\]]*\])?([\s\S]*?)\\end\{figure\}|\\includegraphics(?:\[[^\]]*\])?\{[^}]+\}/g,(match,body)=>{
  const token='@@FIGURE'+blocks.length+'@@';blocks.push(image(body??match,++number));return '\n\n'+token+'\n\n';
 });
 text=text.replace(/\\ref\{([^}]+)\}/g,(_,label)=>{const n=labels.get(label);if(!n)throw Error('Unknown figure label: '+label);return String(n)}).replace(/~(?=\d)/g,' ');
 text=text.replace(/\\\$|\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)|\$\$([\s\S]*?)\$\$|\$((?:\\.|[^$\\])+)\$/g,(match,display,paren,dd,inline)=>{
  const token=`@@MATH${tokens.length}@@`;tokens.push(match==='\\$'?'$':katex.renderToString(display??paren??dd??inline,{displayMode:display!==undefined||dd!==undefined,throwOnError:true,trust:false,output:'htmlAndMathml',strict:'error',maxExpand:1000,maxSize:20}));return token;
 });
 text=escapeHTML(text).replace(/\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g,(_,body)=>'<ul>'+body.split('\\item').slice(1).map((s:string)=>'<li>'+s.trim()+'</li>').join('')+'</ul>');
 text=text.split(/\n\s*\n/).map(s=>'<p>'+s.trim()+'</p>').join('\n').replace(/@@MATH(\d+)@@/g,(_,n)=>tokens[Number(n)]).replace(/<p>@@FIGURE(\d+)@@<\/p>/g,(_,n)=>blocks[Number(n)]);
 if(/\\(?:begin|end|item)/.test(text))throw Error('Unsupported LaTeX environment. Use paragraphs, $…$, \\[ … \\] and itemize lists.');return text;
}
