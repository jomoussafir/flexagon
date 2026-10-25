import { render, escapeHTML as esc } from '../../../../shared/latex/render.ts';
import { mountReference } from './reference.ts';
import { problemTitle, progressGroups, type ProgressFilters } from './progress.ts';

declare global { interface Window { LPDJ: any } }
const cfg = window.LPDJ;
let session = cfg.session;
const root = document.querySelector('#app')!;
const categories: Record<string,string> = {Algebra:'Algebra',Geometry:'Geometry','Number Theory':'Number Theory',Combinatorics:'Combinatorics',Logic:'Logic'};
const progress: Record<string,string> = {unseen:'Unseen',seen:'Seen',bookmarked:'Bookmarked',attempted:'Attempted',solved:'Solved'};
const progressModes:Record<ProgressFilters['mode'],string>={all:'All',unseen:'Unseen',seen:'Seen',bookmarked:'Bookmarked',attempted:'Attempted',solved:'Solved',unsolved:'Unsolved'};
const statuses: Record<string,string> = {draft:'Draft',submitted:'Awaiting review',returned:'Changes requested',published:'Published'};
const triages: Record<string,string> = {unseen:'Unseen',nice:'Nice',later:'Later'};
// Custom sort orders (not alphabetical); category/difficulty/source/language are filters, not sorts.
const triageSortOrder = ['nice','unseen','later'];
const statusSortOrder = ['returned','draft','submitted','published'];
const actions: Record<string,string> = {save:'Saved',submit:'Submitted',publish:'Published',return:'Returned to author',unpublish:'Unpublished'};
const knownLanguages:Record<string,string> = {en:'English',fr:'French',es:'Spanish',de:'German',it:'Italian',pt:'Portuguese',ar:'Arabic',zh:'Chinese',ja:'Japanese',ko:'Korean',ru:'Russian',uk:'Ukrainian',pl:'Polish',nl:'Dutch',sv:'Swedish',da:'Danish',no:'Norwegian',fi:'Finnish',el:'Greek',tr:'Turkish',he:'Hebrew',fa:'Persian',hi:'Hindi',bn:'Bengali',ta:'Tamil',vi:'Vietnamese',id:'Indonesian',ro:'Romanian',hu:'Hungarian',cs:'Czech',sw:'Swahili',la:'Latin'};
const languageName=(key:string,v:any)=>v?.language||knownLanguages[key]||key.toUpperCase();
const languageCode=(key:string,v:any)=>Object.entries(knownLanguages).find(([,name])=>name.toLocaleLowerCase()===languageName(key,v).toLocaleLowerCase())?.[0]||languageName(key,v).slice(0,3);
const languageApproved=(p:any,name:string)=>Object.entries(p.versions).some(([key,v]:any)=>languageName(key,v)===name&&v.approved);
let listing: any = null, problem: any = null, language = 'en', editorLanguage = 'en', dirty = false, routeSequence = 0;
let filters = {search:'',category:'',difficulty:'',source:'',progress:'',status:'',triage:'',sort:'newest'};
let lastRoute = location.hash || '#/';
let avatar = 0;
let listPage = 1;
const pageSize = 50;
let progressItems:any[]=[];
let progressFilters:ProgressFilters={groupBy:'category',mode:'solved',search:'',category:'',difficulty:'',source:''};
let progressExpanded:Record<string,number>=Object.create(null);
let readerOrigin='';
// Remember exactly where the member was in a list when they opened a problem,
// so the problem page can offer a "back to problem list" link that restores it.
let listReturn:{hash:string,filters:any,page:number,scroll:number}|null=null;
let backRestore=false;
// Administrator picker of figures traced from the reference books (private library).
let library:{open:boolean,source:string,page:string,fresh:boolean}={open:false,source:'',page:'',fresh:true};
let disposeReference:(()=>void)|undefined;
const $ = (selector: string) => document.querySelector(selector) as any;
const value = (id: string) => ($('#'+id) as HTMLInputElement)?.value ?? '';
const checked = (id: string) => !!($('#'+id) as HTMLInputElement)?.checked;
const titleOf = problemTitle;
const date = (s: string) => new Date(s).toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
const option = (val:string, label:string, selected:string) => `<option value="${esc(val)}" ${selected===val?'selected':''}>${esc(label)}</option>`;
function toast(message:string) { const t=$('#toast'); t.textContent=message; t.classList.add('visible'); setTimeout(()=>t.classList.remove('visible'),5000); }
function message(text:string, error=false) { const e=$('#form-message'); if(e){e.textContent=text;e.className='notice '+(error?'error':'success');e.focus();}else toast(text); }
function routeTo(path:string) { location.hash='#'+path; }
async function api(path:string, data?:any, method?:string) {
    const url=new URL(cfg.api+path,location.href);
    // Also support WordPress installations using plain permalinks (?rest_route=...).
    if(cfg.api.includes('?rest_route=')) { const [p,q]=path.split('?'); const base=new URL(cfg.api); base.searchParams.set('rest_route',base.searchParams.get('rest_route')!+p); new URLSearchParams(q).forEach((v,k)=>base.searchParams.set(k,v)); url.href=base.href; }
    const headers:Record<string,string>={'X-WP-Nonce':session.nonce,'X-LPDJ-Form':session.formNonce};
    if(data && !(data instanceof FormData))headers['Content-Type']='application/json';
    const response=await fetch(url,{method:method||(data?'POST':'GET'),headers,credentials:'same-origin',body:data?(data instanceof FormData?data:JSON.stringify(data)):undefined});
    // A firewall, proxy or server error can return HTML or text instead of JSON; report it plainly.
    const body=await response.text();
    let result:any;
    try{result=JSON.parse(body);}catch{
        throw new Error(response.ok?'The server returned an unexpected response. Please try again.':`The request was blocked or rejected by the server${response.status?' ('+response.status+')':''}. If this keeps happening, a server or firewall rule may need adjusting.`);
    }
    if(!response.ok)throw new Error(result.message||'Something went wrong. Please try again.');
    return result;
}
function shell(content:string, active='', minimal=false) {
    const user=session.user;
    root.innerHTML=`${session.local&&!minimal?`<div class="local-banner"><span class="local-dot"></span>Local preview · Emails stay on this Mac${user?.admin?'<a href="#/courrier">Test inbox ↗</a>':''}</div>`:''}
    <div class="masthead"><header class="header container simple-header"><a class="brand" href="#/" aria-label="Flexagon — Home" title="Flexagon"><img src="${cfg.logo}" alt="" width="52" height="52"><span>Flexagon</span></a>
    <nav aria-label="Main navigation"><a ${active==='about'?'aria-current="page"':''} href="#/about">About</a><a ${active==='collection'?'aria-current="page"':''} href="#/problems">Problem</a>${user?`<a ${active==='progress'?'aria-current="page"':''} href="#/progress">Progress</a><button class="button small" data-action="new">Submit a problem</button><details class="account-menu"><summary aria-label="Account menu">${esc(user.pseudo)} <span aria-hidden="true">⌄</span></summary><div><a href="#/mes-propositions">My submissions</a>${user.admin?'<a href="#/administration">Admin review</a><a href="#/membres">Members</a>':''}<a href="#/profil">My profile</a><button data-action="logout">Sign out</button></div></details>`:`<a href="#/connexion">Sign In</a><a class="button small" href="#/inscription">Create Account</a>`}</nav></header></div>
    <main id="main" class="container ${minimal?'landing':active==='progress'?'progress-page':''}" tabindex="-1">${content}</main>
    ${minimal?'':`<footer class="footer container"><span>Flexagon</span><a href="#/aide">LaTeX & figures</a><a href="#/confidentialite">Privacy & contributions</a></footer>`}`;
}
function intro(title:string,extra='') { return `<div class="page-heading"><h1>${title}</h1>${extra}</div>`; }
function notice() { return '<div id="form-message" role="alert" tabindex="-1"></div>'; }
function field(id:string,label:string,type='text',extra='') { return `<label for="${id}">${label}<input id="${id}" name="${id}" type="${type}" ${extra}></label>`; }
function langSquares(p:any) { const entries=Object.entries(p.versions);return `<span class="language-squares" aria-label="Language versions">${entries.slice(0,3).map(([key,v]:any)=>`<span class="lang-square level-${p.difficulty} ${v.title?'':'absent'}" aria-label="${esc(languageName(key,v))}: ${v.approved?'verified':'not verified'}" title="${esc(languageName(key,v))} · ${v.approved?'verified':'not verified'} · level ${p.difficulty}">${esc(languageCode(key,v).toUpperCase())}${v.approved?'<b aria-hidden="true">✓</b>':''}</span>`).join('')}${entries.length>3?`<span class="small" title="${esc(entries.slice(3).map(([k,v])=>languageName(k,v)).join(', '))}">+${entries.length-3}</span>`:''}</span>`; }
function sourceOrder(a:string,b:string) { const names=session.sources;const x=names.indexOf(a),y=names.indexOf(b);return (x<0?99:x)-(y<0?99:y)||a.localeCompare(b,'en'); }
function empty(title:string,text:string,button='') { return `<div class="empty"><div class="empty-symbol" aria-hidden="true">∅</div><h2>${title}</h2><p>${text}</p>${button}</div>`; }
function landing() { about(); }
function about() { shell('<article class="manifesto"><p>Curated list of mathematical puzzles</p></article>', 'about', true); }
function gated(section='Problems', destination='/problems') {
    shell(intro(section)+empty('Sign in to continue','',`<a class="button" href="#/connexion?next=${encodeURIComponent(destination)}">Sign In</a> <a class="button secondary" href="#/inscription">Create Account</a>`),section==='Progress'?'progress':'collection');
}
async function collection(scope='published', restore=false) {
    if(!session.user){gated();return;}
    if(scope==='review'&&!session.user.admin){shell(empty('Restricted access','This page is for administrators.'));return;}
    if(!(scope==='review'?['newest','title','triage','status']:['newest','title']).includes(filters.sort))filters.sort='newest';
    const seq=routeSequence;
    const heading=scope==='mine'?'':intro(scope==='published'?'Problems':'Admin review');
    shell(heading+'<p class="loading">Loading…</p>',scope==='published'?'collection':scope==='mine'?'mine':'review');
    listing=await api('problems?scope='+scope);if(seq!==routeSequence)return;listPage=1;
    const total=listing.published, pending=listing.items.filter((p:any)=>p.state==='submitted').length;
    const admin=!!session.user?.admin;
    const sourceCounts:Record<string,number> = scope==='published'?listing.sources:listing.items.reduce((counts:any,p:any)=>{counts[p.source]=(counts[p.source]||0)+1;return counts;},{});
    // The source is an internal curation detail: members never see it.
    const secondStat=scope==='review'?`<div><strong>${pending.toLocaleString('en-GB')}</strong><span>awaiting review</span></div>`:admin?`<div><strong>${Object.keys(listing.sources).length.toLocaleString('en-GB')}</strong><span>sources</span></div>`:'';
    const summary=scope==='mine'?'':`<section class="stats"><div><strong>${(scope==='published'?total:listing.total).toLocaleString('en-GB')}</strong><span>${scope==='published'?'published problems':'submissions'}</span></div>${secondStat}<div><strong>1–5</strong><span>difficulty levels</span></div></section>`;
    shell(heading+summary+`
    ${listing.total&&scope!=='mine'&&admin?`<div class="source-counts">${Object.entries(sourceCounts).sort(([a],[b])=>sourceOrder(a,b)).map(([s,c])=>`<button data-source="${esc(s)}">${esc(s)} <b>${c}</b></button>`).join('')}</div>`:''}
    <section class="collection"><div class="section-label"><h2>${scope==='published'?'Browse problems':scope==='mine'?'Your problems':'All submissions'}</h2>${scope==='published'?'<button class="text-link" data-action="pick">Pick one ↗</button>':''}</div>
    <div class="filters ${scope==='review'?'filters-review':''}"><label class="search-label" for="search">Search<input id="search" type="search" placeholder="Title, keyword…" value="${esc(filters.search)}"></label>
    <label for="category">Category<select id="category">${option('','All',filters.category)}${Object.entries(categories).map(([v,l])=>option(v,l,filters.category)).join('')}</select></label>
    <label for="difficulty">Difficulty<select id="difficulty">${option('','All levels',filters.difficulty)}${[1,2,3,4,5].map(n=>option(String(n),`Level ${n}`,filters.difficulty)).join('')}</select></label>
    ${admin?`<label for="source">Source<select id="source">${option('','All sources',filters.source)}${[...new Set(listing.items.map((p:any)=>p.source))].sort(sourceOrder).map((s:any)=>option(s,s,filters.source)).join('')}</select></label>`:''}
    ${scope==='review'?`<label for="triage">Triage<select id="triage">${option('','All',filters.triage)}${Object.entries(triages).map(([v,l])=>option(v,l,filters.triage)).join('')}</select></label>`:''}
    <label for="${scope==='published'?'progress':'status'}">${scope==='published'?'Progress':'Status'}<select id="${scope==='published'?'progress':'status'}">${option('','All',scope==='published'?filters.progress:filters.status)}${Object.entries(scope==='published'?progress:statuses).map(([v,l])=>option(v,l,scope==='published'?filters.progress:filters.status)).join('')}</select></label></div>
    <div class="list-tools"><span id="result-count" aria-live="polite"></span><label for="sort">Sort by <select id="sort">${[['newest','Newest'],['title','Title'],...(scope==='review'?[['triage','Triage'],['status','Status']]:[])].map(([v,l])=>option(v,l,filters.sort)).join('')}</select></label><button class="text-link" data-action="reset-filters">Clear filters</button></div><div id="problem-list" data-scope="${scope}"></div></section>`,scope==='published'?'collection':scope==='mine'?'mine':'review');
    drawList();
    if(restore&&listReturn){if(listReturn.page>1){listPage=listReturn.page;drawList(false);}const y=listReturn.scroll;requestAnimationFrame(()=>window.scrollTo(0,y));}
}
function filtered() {
    return listing.items.filter((p:any)=>!filters.search||[...Object.values(p.versions).map((v:any)=>v.title),...p.keywords].join(' ').toLocaleLowerCase().includes(filters.search.toLocaleLowerCase())).filter((p:any)=>!filters.category||p.category===filters.category).filter((p:any)=>!filters.difficulty||p.difficulty===Number(filters.difficulty)).filter((p:any)=>!filters.source||p.source===filters.source).filter((p:any)=>!filters.progress||p.progress===filters.progress).filter((p:any)=>!filters.status||p.state===filters.status).filter((p:any)=>!filters.triage||(p.triage||'unseen')===filters.triage).sort((a:any,b:any)=>{const s=filters.sort,byTitle=titleOf(a).localeCompare(titleOf(b),'en');return s==='title'?byTitle:s==='triage'?triageSortOrder.indexOf(a.triage||'unseen')-triageSortOrder.indexOf(b.triage||'unseen')||byTitle:s==='status'?statusSortOrder.indexOf(a.state)-statusSortOrder.indexOf(b.state)||byTitle:b.id-a.id;});
}
function referenceLinks(p:any, detailed=false) {
    if(!p.references?.length)return '';
    return `<div class="reference-links ${detailed?'reference-links-detail':''}" aria-label="Reference PDFs"><span>Reference PDF:</span>${p.references.map((ref:any)=>`<a href="#/reference/${p.id}?index=${ref.index}" target="_blank" rel="noopener" title="${esc(ref.title)} — PDF page ${ref.page}" aria-label="Open ${esc(ref.title)}, PDF page ${ref.page}">${detailed?esc(ref.title)+' · ':''}PDF · p. ${ref.page}${ref.printedPage&&ref.printedPage!==String(ref.page)?' (printed '+esc(ref.printedPage)+')':''} ↗</a>`).join('')}</div>`;
}
async function referencePage(id:string,params:URLSearchParams) {
    if(!session.user){routeTo('/connexion?next='+encodeURIComponent('/reference/'+id+'?'+params));return;}
    if(!session.user.admin){shell(empty('Restricted access','Reference PDFs are available to administrators.'));return;}
    const seq=routeSequence, index=params.get('index')||'0';
    shell(intro('Reference PDF')+'<p class="loading">Loading…</p>');
    const path='problems/'+id+'/reference?index='+encodeURIComponent(index);
    const info=await api(path);if(seq!==routeSequence)return;
    shell(`<div class="reader-heading"><a class="text-link" href="#/administration">← Admin review</a><a class="text-link" href="#/editer/${Number(id)}">Back to problem →</a></div>${intro(esc(info.title))}<p class="reference-context">${info.number?'Problem '+esc(info.number)+' · ':''}PDF page ${info.originalPage}${info.printedPage?' · Printed page '+esc(info.printedPage):''}</p><section id="reference-viewer" aria-label="Reference PDF viewer"></section>`,'review');
    disposeReference=mountReference($('#reference-viewer'),info,page=>api(path+'&page='+page),cfg.pdfAssets);
}
function drawList(reset=true) {
    if(reset)listPage=1;
    const all=filtered(),scope=$('#problem-list').dataset.scope;
    const pages=Math.max(1,Math.ceil(all.length/pageSize));listPage=Math.min(listPage,pages);
    const items=all.slice((listPage-1)*pageSize,listPage*pageSize);
    $('#result-count').textContent=`${all.length.toLocaleString('en-GB')} ${scope==='mine'?'submission':'problem'}${all.length!==1?'s':''}`;
    $('#problem-list').innerHTML=items.length?`<div class="problem-table">${items.map((p:any)=>`<div class="review-row"><a class="problem-row" href="#/${scope==='published'?'probleme':'editer'}/${p.id}"><span class="problem-name"><strong>${esc(titleOf(p))}</strong><small>${esc(categories[p.category])}${session.user?.admin?` <span>·</span> ${esc(p.source)}`:''}${scope!=='published'?` <span>·</span> ${esc(p.author)}`:''}</small></span><span class="level-label">Level ${p.difficulty}</span>${langSquares(p)}<span class="status ${scope==='published'?p.progress:p.state}">${scope==='published'?progress[p.progress]:statuses[p.state]}</span><span class="row-arrow">↗</span></a>${scope==='review'?`<div class="review-row-tools"><div class="segmented triage-buttons" role="group" aria-label="Triage">${Object.entries(triages).map(([key,label])=>`<button data-triage="${key}" data-triage-id="${p.id}" aria-pressed="${(p.triage||'unseen')===key}">${label}</button>`).join('')}</div>${referenceLinks(p)}</div>`:''}</div>`).join('')}</div>`:listing.total?empty('No results','Try different filters.','<button class="button secondary" data-action="reset-filters">Clear filters</button>'):empty(scope==='published'?'No published problems':'No submissions','');
    if(pages>1)$('#problem-list').insertAdjacentHTML('beforeend',`<nav class="pagination" aria-label="Problem list pages"><button class="button secondary small" data-action="previous-page" ${listPage===1?'disabled':''}>← Previous</button><span>Page ${listPage} of ${pages}</span><button class="button secondary small" data-action="next-page" ${listPage===pages?'disabled':''}>Next →</button></nav>`);
}
async function progressPage() {
    if(!session.user){gated('Progress','/progress');return;}
    const seq=routeSequence;
    shell(intro('Progress')+'<p class="loading">Loading…</p>','progress');
    const data=await api('problems');if(seq!==routeSequence)return;
    progressItems=data.items;
    shell(`${intro('Progress')}<div id="progress-summary" class="stats"></div>
    <section class="progress-controls"><div><span class="control-label">Show</span><div class="segmented progress-status-options" role="group" aria-label="Progress status">${Object.entries(progressModes).map(([key,label])=>`<button data-progress-mode="${key}" aria-pressed="${progressFilters.mode===key}">${label}</button>`).join('')}</div></div>
    <div><span class="control-label">Group by</span><div class="segmented" role="group" aria-label="Group problems by">${[['category','Category'],['difficulty','Difficulty'],...(session.user?.admin?[['source','Source']]:[])].map(([key,label])=>`<button data-group-by="${key}" aria-pressed="${progressFilters.groupBy===key}">${label}</button>`).join('')}</div></div></section>
    <section class="filters progress-filters" aria-label="Filter progress"><label for="progress-search">Search<input id="progress-search" type="search" placeholder="Title, keyword…" value="${esc(progressFilters.search)}"></label>
    <label for="progress-category">Category<select id="progress-category">${option('','All categories',progressFilters.category)}${Object.keys(categories).map(c=>option(c,c,progressFilters.category)).join('')}</select></label>
    <label for="progress-difficulty">Difficulty<select id="progress-difficulty">${option('','All levels',progressFilters.difficulty)}${[1,2,3,4,5].map(n=>option(String(n),`Level ${n}`,progressFilters.difficulty)).join('')}</select></label>
    ${session.user?.admin?`<label for="progress-source">Source<select id="progress-source">${option('','All sources',progressFilters.source)}${[...new Set(progressItems.map(p=>p.source))].sort(sourceOrder).map(s=>option(s,s,progressFilters.source)).join('')}</select></label>`:''}</section>
    <div class="progress-legend"><span>Difficulty</span>${[1,2,3,4,5].map(n=>`<span class="level-key level-${n}">${n}</span>`).join('')}<span>✓ Solved · ○ Unsolved</span><button class="text-link" data-action="reset-progress">Clear filters</button></div>
    <div id="progress-grid" aria-live="polite"></div>`,'progress');
    drawProgress();
}
function drawProgress() {
    const view=progressGroups(progressItems,progressFilters,sourceOrder);
    $('#progress-summary').innerHTML=`<div><strong>${view.solved.toLocaleString('en-GB')}</strong><span>solved</span></div><div><strong>${view.unsolved.toLocaleString('en-GB')}</strong><span>unsolved</span></div><div><strong>${view.shown.toLocaleString('en-GB')}</strong><span>matching problems</span></div>`;
    document.querySelectorAll<HTMLElement>('[data-progress-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.progressMode===progressFilters.mode)));
    document.querySelectorAll<HTMLElement>('[data-group-by]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.groupBy===progressFilters.groupBy)));
    $('#progress-grid').innerHTML=view.groups.length?view.groups.map(g=>{
        const limit=progressExpanded[g.key]||24;
        const heading=progressFilters.groupBy==='difficulty'?`Level ${g.key}`:g.key;
        return `<section class="progress-group"><div class="progress-group-heading"><h2>${esc(heading)}</h2><span>${g.solved} / ${g.total} solved</span><progress max="${g.total}" value="${g.solved}" aria-label="${esc(heading)}: ${g.solved} of ${g.total} solved"></progress></div>
        <div class="problem-grid">${g.items.slice(0,limit).map(p=>`<a class="problem-tile level-${p.difficulty} ${p.progress==='solved'?'is-solved':''}" href="#/probleme/${p.id}?from=progress" title="${esc(titleOf(p))} — ${esc(p.category)}${session.user?.admin?' · '+esc(p.source):''}" aria-label="${esc(titleOf(p))} — Level ${p.difficulty} — ${progress[p.progress]}"><div class="tile-top"><span>Level ${p.difficulty}</span><span class="tile-status">${p.progress==='solved'?'✓ Solved':'○ '+progress[p.progress]}</span></div><strong dir="auto">${esc(titleOf(p))}</strong><small>${esc(p.category)}${session.user?.admin?' · '+esc(p.source):''}</small></a>`).join('')}</div>${g.items.length>limit?`<button class="button secondary small more-problems" data-more-group="${esc(g.key)}">Show ${Math.min(24,g.items.length-limit)} more (${g.items.length-limit} remaining)</button>`:''}</section>`;
    }).join(''):empty(!progressItems.length?'No published problems':!view.total?'No matching problems':progressFilters.mode==='solved'?'No solved problems yet':`No ${progressModes[progressFilters.mode].toLowerCase()} problems`,!progressItems.length?'Published problems will appear here.':'',progressItems.length&&progressFilters.mode==='solved'?'<button class="button secondary" data-progress-mode="unsolved">Browse unsolved problems</button>':'');
}
function auth(kind:string,params:URLSearchParams) {
    const signup=kind==='inscription', login=kind==='connexion', forgot=kind==='mot-de-passe', resend=kind==='renvoyer', reset=kind==='reinitialiser', verify=kind==='confirmer';
    const heading=signup?'Create account':login?'Sign in':forgot?'Reset password':resend?'Confirm your email':reset?'Choose a password':'Confirm your account';
    shell(`<div class="auth-layout${login?' auth-layout-signin':''}">${login?'':`<aside><img src="${cfg.logo}" alt="Poincaré disk tiling" width="240" height="240"></aside>`}<section class="auth-card"><h1>${heading}</h1>${notice()}<form id="auth-form" data-kind="${kind}">
    ${signup?field('pseudo','Display name','text','required minlength="2" maxlength="40" autocomplete="nickname"'):''}
    ${!reset&&!verify?field('email','Email address','email','required autocomplete="email"'):''}
    ${signup||login||reset?field('password','Password','password',`required ${login?'':'minlength="12"'} maxlength="200" autocomplete="${login?'current-password':'new-password'}"`)+(!login?'<p class="field-help">At least 12 characters.</p>':''):''}
    ${signup?'<label class="check"><input id="accept" type="checkbox" required><span>I accept the <a href="#/confidentialite" target="_blank">contribution and privacy terms</a>.</span></label><label class="check"><input id="notifications" type="checkbox"><span>Email me when a new problem is published.</span></label>':''}
    ${login?'<label class="check"><input id="remember" type="checkbox"><span>Remember me on this device</span></label>':''}
    <button class="button full" type="submit">${signup?'Create account':login?'Sign in':verify?'Confirm email':reset?'Save password':'Send link'} <span>→</span></button></form>
    <div class="auth-links">${login?'<a href="#/mot-de-passe">Forgot password?</a><a href="#/renvoyer">Resend confirmation</a><p>No account yet? <a href="#/inscription">Create account</a></p>':'<a href="#/connexion">← Back to sign in</a>'}</div></section></div>`);
    $('#auth-form').onsubmit=async(e:Event)=>{
        e.preventDefault();const form=e.currentTarget as HTMLFormElement;const btn=form.querySelector('button')!;btn.disabled=true;
        try{
            const result=await api('auth/'+({inscription:'register',connexion:'login','mot-de-passe':'forgot',renvoyer:'resend',reinitialiser:'reset',confirmer:'verify'} as any)[kind],{pseudo:value('pseudo'),email:value('email'),password:value('password'),remember:checked('remember'),accept:checked('accept'),notifications:checked('notifications'),...Object.fromEntries(params)});
            if(login){session=result;const next=params.get('next')||'/problems';location.hash='#'+(next.startsWith('/')&&!next.startsWith('//')?next:'/problems');location.reload();}else{message(result.message);if(verify||reset)form.hidden=true;else form.reset();}
        }catch(error:any){message(error.message,true);}finally{btn.disabled=false;}
    };
}
function math(version:any,assets:any) { return render(version.latex,Object.fromEntries(Object.entries(assets||{}).map(([name,a]:any)=>[name,a.url]))); }
async function reader(id:string,origin='') {
    if(!session.user){routeTo('/connexion?next='+encodeURIComponent('/probleme/'+id));return;}
    readerOrigin=origin;
    const seq=routeSequence;problem=await api('problems/'+id);if(seq!==routeSequence)return;
    if(!problem.versions[language])language=Object.keys(problem.versions)[0];
    // Opening a problem marks it Seen, unless the reader already set a status.
    if(problem.progress==='unseen'){problem.progress='seen';void api('problems/'+problem.id+'/progress',{progress:'seen'}).catch(()=>{});}
    showReader();
}
function showReader() {
    const p=problem,v=p.versions[language];let content;
    try{content=math(v,p.assets);}catch(error:any){content=`<p class="notice error">The statement needs a rendering correction: ${esc(error.message)}</p><pre>${esc(v.latex)}</pre>`;}
    const backList=!readerOrigin&&listReturn?`<button class="text-link" data-action="back-to-list">← Back to problem list</button>`:`<a class="text-link" href="${readerOrigin==='progress'?'#/progress':'#/problems'}">← ${readerOrigin==='progress'?'Progress':'Problems'}</a>`;
    shell(`<div class="reader-heading">${backList}<span class="badge">${esc(categories[p.category])}</span><span class="muted">${session.user?.admin?esc(p.source)+' · ':''}Level ${p.difficulty}</span></div>
    <article class="reading-card"><div class="reader-top"><p class="eyebrow">FLEXAGON</p><div class="reader-top-controls">${Object.keys(p.versions).length>1?`<label class="reader-language" for="reader-language">Language<select id="reader-language">${Object.entries(p.versions).map(([key,v])=>option(key,languageName(key,v),language)).join('')}</select></label>`:`<span class="small muted">${esc(languageName(language,v))}</span>`}${session.user?.admin?`<div class="reader-triage"><span class="reader-triage-label">Triage</span><div class="segmented triage-buttons" role="group" aria-label="Triage">${Object.entries(triages).map(([key,label])=>`<button data-triage="${key}" data-triage-id="${p.id}" aria-pressed="${(p.triage||'unseen')===key}">${label}</button>`).join('')}</div></div>`:''}</div></div><h1 dir="auto">${esc(v.title)}</h1><div class="math-content" dir="auto">${content}</div><div class="tags">${p.keywords.map((k:string)=>`<span>${esc(k)}</span>`).join('')}</div><div class="reader-foot"><span>Submitted by <strong>${esc(p.author)}</strong></span>${p.editable?`<a href="#/editer/${p.id}">Edit →</a>`:''}</div></article>
    <section class="progress-card"><div><h2>Progress</h2></div><div class="segmented progress-buttons">${Object.entries(progress).map(([key,label])=>`<button data-progress="${key}" aria-pressed="${p.progress===key}">${label}</button>`).join('')}</div></section>`,'collection');
}
async function editor(id:string) {
    if(!session.user){routeTo('/connexion');return;}
    const seq=routeSequence;problem=await api('problems/'+id+'?context=edit');if(seq!==routeSequence)return;
    editorLanguage=Object.keys(problem.versions).find(k=>problem.versions[k].title)||Object.keys(problem.versions)[0];dirty=false;library={open:false,source:'',page:'',fresh:true};showEditor();
}
function collectEditor() {
    if(!$('#problem-title'))return;
    const v=problem.versions[editorLanguage];v.title=value('problem-title');v.latex=value('latex');v.language=value('language-name').trim();if(session.user.admin)v.approved=checked('approved');
    problem.category=value('edit-category');problem.difficulty=Number(value('edit-difficulty'));if(session.user.admin)problem.source=value('edit-source');problem.keywords=value('keywords').split(',').map((s:string)=>s.trim()).filter(Boolean);if(session.user.admin)problem.reviewNote=value('review-note');
}
function showEditor() {
    if(!problem.versions[editorLanguage])editorLanguage=Object.keys(problem.versions)[0];
    const p=problem,v=p.versions[editorLanguage];
    const backList=listReturn?`<button class="text-link" data-action="back-to-list">← Back to problem list</button>`:`<a class="text-link" href="${session.user.admin?'#/administration':'#/mes-propositions'}">← Back to problem list</a>`;
    shell(`<div class="reader-heading">${backList}</div>${intro(titleOf(p)==='Untitled'?'New problem':esc(titleOf(p)),`<span class="status ${p.state}">${statuses[p.state]}</span>`)}
    ${p.hasPublished?`<div class="notice soft">A version is published. Changes stay private until you publish again. <a href="#/probleme/${p.id}">View published version →</a></div>`:''}
    ${p.reviewNote&&!session.user.admin?`<div class="notice soft"><strong>Administrator’s note</strong><p>${esc(p.reviewNote)}</p></div>`:''}
    ${notice()}<div class="editor-meta"><label for="edit-category">Category<select id="edit-category">${Object.entries(categories).map(([key,label])=>option(key,label,p.category)).join('')}</select></label><label for="edit-difficulty">Difficulty<select id="edit-difficulty">${[1,2,3,4,5].map(n=>option(String(n),`${n} — ${['Introductory','Easy','Intermediate','Hard','Very hard'][n-1]}`,String(p.difficulty))).join('')}</select></label>${session.user.admin?`<label for="edit-source">Source<input id="edit-source" list="sources" value="${esc(p.source)}" maxlength="160"><datalist id="sources">${[...session.sources,'Community'].map((s:string)=>`<option value="${esc(s)}">`).join('')}</datalist></label>`:''}<label for="keywords">Keywords<input id="keywords" value="${esc(p.keywords.join(', '))}" placeholder="probability, integers…"><span class="field-help">Separate with commas.</span></label></div>
    ${referenceLinks(p,true)}
    ${p.legacy?`<details class="source-details"><summary>Original source details</summary><p>${p.legacy.sources.map((s:any)=>`${esc(s.title)} · Problem ${esc(s.number)} · PDF page ${s.page}`).join('<br>')}</p><p class="muted">${esc(p.legacy.note)}</p>${p.legacy.reviewUrl?`<a class="text-link" href="${esc(p.legacy.reviewUrl)}" target="_blank" rel="noopener">Open original review & reference PDF ↗</a>`:''}</details>`:''}
    <section class="editor-panel"><div class="editor-toolbar"><div class="segmented language-tabs" role="group" aria-label="Edit language version">${Object.entries(p.versions).map(([key,version])=>`<button data-editor-lang="${key}" aria-pressed="${key===editorLanguage}">${esc(languageName(key,version))} ${p.versions[key].approved?'✓':''}</button>`).join('')}</div>${session.user.admin?`<div class="editor-triage"><span class="reader-triage-label">Triage</span><div class="segmented triage-buttons" role="group" aria-label="Triage">${Object.entries(triages).map(([key,label])=>`<button data-triage="${key}" data-triage-id="${p.id}" aria-pressed="${(p.triage||'unseen')===key}">${label}</button>`).join('')}</div></div>`:''}<label class="import-button" for="tex-file">Import .tex ↗<input type="file" id="tex-file" accept=".tex,text/plain"></label></div>
    <div class="language-management"><details id="add-language"><summary>＋ Add a language</summary><form id="add-language-form"><label for="new-language">Language<input id="new-language" list="language-names" maxlength="60" required placeholder="Choose or type a language"></label><button class="button small" type="submit">Add language</button></form></details>${Object.keys(p.versions).length>1?'<button class="text-link danger" data-action="remove-language">Remove this version</button>':''}</div>
    <datalist id="language-names">${Object.values(knownLanguages).sort().map(name=>`<option value="${esc(name)}">`).join('')}</datalist>
    <div class="editor-title"><label for="language-name">Language name<input id="language-name" list="language-names" value="${esc(languageName(editorLanguage,v))}" maxlength="60" required dir="auto"></label><label for="problem-title">Title<input id="problem-title" value="${esc(v.title)}" maxlength="300" placeholder="Problem title" dir="auto"></label></div>
    <div class="editor-columns"><div class="latex-pane"><label for="latex">LATEX STATEMENT</label><textarea id="latex" dir="auto" spellcheck="false" placeholder="Write your statement here. Use $…$ for formulas.">${esc(v.latex)}</textarea><span class="field-help">Text, formulas and figures. <a href="#/aide" target="_blank">Supported commands ↗</a></span></div><div class="preview-pane"><p class="eyebrow">STATEMENT PREVIEW</p><div id="latex-preview" class="math-content" dir="auto"></div></div></div>
    ${session.user.admin?`<div class="approval"><label class="check"><input id="approved" type="checkbox" ${v.approved?'checked':''}><span>I have verified this ${esc(languageName(editorLanguage,v))} version and approve it for publication.</span></label><p class="field-help">Only checked versions will be published. Verify each language separately.</p></div>`:''}</section>
    <section class="attachments"><div><h2>Figures</h2><p class="muted">Plain SVG, PNG, JPEG or one-page PDF · Up to 2 MB per file</p><div class="figure-actions"><label class="button secondary small upload-label" for="figure-file">＋ Add figure<input id="figure-file" type="file" accept=".svg,.png,.jpg,.jpeg,.pdf"></label>${session.user.admin?`<button type="button" class="button secondary small" data-action="figure-library" aria-expanded="${library.open}" aria-controls="figure-library">Source figures ${library.open?'▴':'▾'}</button>`:''}</div></div><div class="asset-list">${Object.entries(p.assets).map(([name,a]:any)=>`<div class="asset"><img src="${esc(a.url)}" alt="${esc(name)}"><div><strong>${esc(name)}</strong><button class="text-link" data-insert="${esc(name)}">Insert into statement →</button>${a.pdf?`<a class="text-link" href="${esc(a.pdf)}" target="_blank" rel="noopener">PDF ↗</a>`:''}<button class="text-link danger" data-detach="${esc(name)}">Remove</button></div></div>`).join('')||'<p class="muted">No figures attached.</p>'}</div>${session.user.admin?`<div id="figure-library" class="figure-library" ${library.open?'':'hidden'}></div>`:''}</section>
    ${session.user.admin?`<label class="review-note" for="review-note">Note to author<textarea id="review-note" rows="3" placeholder="Describe any changes needed.">${esc(p.reviewNote||'')}</textarea></label>`:''}
    <div class="save-bar"><span id="save-state">${dirty?'Unsaved changes':'Last saved: '+date(p.updated)}</span><div class="button-row"><button class="button secondary" data-save="save">Save</button>${session.user.admin?'<button class="button" data-save="publish">Save & publish ↗</button><button class="text-link" data-save="return">Return to author</button>':'<button class="button" data-save="submit">Submit for review →</button>'}</div></div>
    <div class="editor-bottom"><button class="text-link" data-action="history">Revision history</button>${session.user.admin&&p.hasPublished?'<button class="text-link danger" data-save="unpublish">Unpublish</button>':!p.hasPublished?'<button class="text-link danger" data-action="delete-draft">Delete draft</button>':''}</div><div id="history"></div>`,session.user.admin?'review':'mine');
    $('#add-language-form').onsubmit=(e:Event)=>{e.preventDefault();addLanguage();};
    preview();if(library.open)void drawLibrary();
}
async function drawLibrary() {
    const host=$('#figure-library');if(!host)return;
    host.innerHTML='<p class="muted">Loading source figures…</p>';
    try{
        const query=new URLSearchParams({problem:String(problem.id)});if(library.fresh)query.set('default','1');if(library.source)query.set('source',library.source);if(library.page)query.set('page',library.page);
        const data=await api('figures?'+query);if(!$('#figure-library'))return;
        if(library.fresh){library.fresh=false;library.source=data.source||'';library.page=data.page?String(data.page):'';}
        if(!data.available){$('#figure-library').innerHTML='<p class="muted">No source figures are installed. Trace and redraw the reference books first (see START-HERE.md).</p>';return;}
        const card=(f:any)=>{const attached=!!problem.assets[f.name];return `<button type="button" class="figure-card" data-figure="${esc(f.id)}" title="${esc(f.sourceTitle)} · PDF page ${f.page} · figure ${f.index}"><img src="${esc(f.url)}" alt="" loading="lazy"><span>${esc(f.source)} · p. ${f.page} · ${f.index}</span><span class="small muted">${attached?'Insert again (refreshes the copy)':'Insert into statement →'}</span></button>`;};
        const source=data.sources.find((s:any)=>s.slug===library.source);
        $('#figure-library').innerHTML=`<form id="figure-filter" class="figure-filter"><label>Book<select id="figure-source"><option value="">All books</option>${data.sources.map((s:any)=>option(s.slug,s.title,library.source)).join('')}</select></label><label>PDF page<select id="figure-page"><option value="">Any page</option>${(source?.pages||[]).map((n:number)=>option(String(n),'p. '+n,library.page)).join('')}</select></label><span class="small muted">${data.total} figure${data.total===1?'':'s'}${data.total>data.figures.length?' · first '+data.figures.length+' shown':''}</span></form><div class="figure-grid">${data.figures.map(card).join('')||'<p class="muted">No redrawn figure on this page yet. Choose another page or book.</p>'}</div>`;
        $('#figure-source').onchange=()=>{library.source=value('figure-source');library.page='';void drawLibrary();};
        $('#figure-page').onchange=()=>{library.page=value('figure-page');void drawLibrary();};
    }catch(error:any){if($('#figure-library'))$('#figure-library').innerHTML=`<p class="notice error">${esc(error.message)}</p>`;}
}
// Insert a figure environment for an attached figure at the cursor of the statement.
function insertFigure(name:string) {
    const text=$('#latex');const label='fig:'+name.replace(/\.[^.]+$/,'');
    text.setRangeText(`\n\n\\begin{figure}\n\\centering\n\\includegraphics[width=0.7\\linewidth]{${name}}\n\\caption{A caption}\n\\label{${label}}\n\\end{figure}\n`,text.selectionStart,text.selectionEnd,'end');
    problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;dirty=true;$('#save-state').textContent='Unsaved changes';preview();text.focus();
}
// A PDF figure is displayed through a rendered image, so readers never load a PDF engine.
async function pdfPreview(file:File):Promise<Blob> {
    const pdfjs=await import(cfg.pdfAssets+'pdf.mjs');pdfjs.GlobalWorkerOptions.workerSrc=cfg.pdfAssets+'pdf.worker.mjs';
    const loading=pdfjs.getDocument({data:await file.arrayBuffer(),isEvalSupported:false,cMapUrl:cfg.pdfAssets+'cmaps/',cMapPacked:true,standardFontDataUrl:cfg.pdfAssets+'standard_fonts/',wasmUrl:cfg.pdfAssets+'wasm/'});
    try{
        const doc=await loading.promise;if(doc.numPages!==1)throw Error('Use a one-page PDF containing only the figure.');
        const page=await doc.getPage(1);const base=page.getViewport({scale:1});const viewport=page.getViewport({scale:Math.min(4,2400/Math.max(base.width,base.height))});
        const canvas=document.createElement('canvas');canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);
        const context=canvas.getContext('2d')!;context.fillStyle='#fff';context.fillRect(0,0,canvas.width,canvas.height);
        await page.render({canvas,canvasContext:context,viewport}).promise;
        return await new Promise<Blob>((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(Error('Could not render the PDF preview.')),'image/png'));
    }catch(error:any){throw Error(error?.message?.includes('one-page')?error.message:'This PDF could not be read. Export a one-page PDF figure.');}
    finally{void loading.destroy();}
}
function addLanguage() {
    collectEditor();const name=value('new-language').trim();
    if(!name||name.length>60){message('Enter a language name of up to 60 characters.',true);return;}
    if(Object.values(problem.versions).some((v:any)=>v.language.toLocaleLowerCase()===name.toLocaleLowerCase())){message('This language already has a version.',true);return;}
    if(Object.keys(problem.versions).length>=20){message('Use up to 20 language versions.',true);return;}
    const known=Object.entries(knownLanguages).find(([,label])=>label.toLocaleLowerCase()===name.toLocaleLowerCase());
    const key=known&&!problem.versions[known[0]]?known[0]:'und-'+crypto.randomUUID().slice(0,8);
    problem.versions[key]={language:known?.[1]||name,title:'',latex:'',approved:false};editorLanguage=key;dirty=true;showEditor();$('#problem-title').focus();
}
function preview(){const v={latex:value('latex')};try{$('#latex-preview').innerHTML=v.latex?math(v,problem.assets):'<p class="preview-placeholder">Statement preview</p>';}catch(error:any){$('#latex-preview').innerHTML=`<p class="notice error">${esc(error.message)}</p>`;}}
async function saveProblem(action:string) {
    collectEditor();
    if(action==='unpublish'&&!confirm('Unpublish this problem? The draft will be kept.'))return;
    if(action==='submit'||action==='publish')for(const [lang,v] of Object.entries(problem.versions) as any){if(action==='submit'||v.approved){try{math(v,problem.assets);}catch(error:any){message(`${languageName(lang,v)}: ${error.message}`,true);return;}}}
    const buttons=document.querySelectorAll<HTMLButtonElement>('[data-save]');buttons.forEach(b=>b.disabled=true);
    // Send only the fields the server reads; the legacy block and its source URLs stay in the browser.
    const payload={action,revision:problem.revision,category:problem.category,difficulty:problem.difficulty,source:problem.source,keywords:problem.keywords,reviewNote:problem.reviewNote,versions:problem.versions};
    try{problem=await api('problems/'+problem.id,payload);dirty=false;showEditor();toast(({save:'Draft saved.',submit:'Submitted for review.',publish:'Verified versions published.',return:'Returned to author.',unpublish:'Problem unpublished.'} as any)[action]);}catch(error:any){message(error.message,true);}finally{buttons.forEach(b=>b.disabled=false);}
}
function profile() {
    if(!session.user){routeTo('/connexion');return;}const u=session.user;avatar=0;
    shell(`<div class="profile-grid profile-page"><section class="panel"><h2>Your profile</h2>${notice()}<form id="profile-form"><div class="avatar-editor">${u.avatar?`<img id="avatar-preview" src="${esc(u.avatar)}" alt="Your profile image">`:`<span id="avatar-placeholder">${esc(u.pseudo.slice(0,1).toUpperCase())}</span>`}<div><label class="button secondary small upload-label" for="avatar-file">Choose image<input type="file" id="avatar-file" accept=".png,.jpg,.jpeg,.svg"></label><p class="field-help">A portrait or drawing · Up to 2 MB</p></div></div>${field('pseudo','Display name','text',`required minlength="2" maxlength="40" value="${esc(u.pseudo)}"`)}<label>Email address<input type="email" value="${esc(u.email)}" disabled></label><label class="check"><input type="checkbox" id="notifications" ${u.notifications?'checked':''}><span>Email me when a new problem is published.</span></label><button class="button">Save preferences</button></form></section><aside class="panel account-panel"><p class="eyebrow">ACCOUNT</p><h3>${u.admin?'Administrator':'Member'}</h3><a href="#/mot-de-passe">Change password →</a><button class="button secondary" data-action="logout">Sign out</button>${!u.admin?'<details class="delete-account"><summary>Delete account</summary><p>Your profile and drafts will be deleted. Published problems remain available, attributed to “Deleted account”.</p><label for="delete-password">Confirm your password<input id="delete-password" type="password" autocomplete="current-password"></label><button class="button danger" data-action="delete-account">Delete permanently</button></details>':''}</aside></div>`);
    $('#profile-form').onsubmit=async(e:Event)=>{e.preventDefault();try{const data:any={pseudo:value('pseudo'),notifications:checked('notifications')};if(avatar)data.avatar=avatar;session.user=await api('profile',data);profile();toast('Profile saved.');}catch(error:any){message(error.message,true);}};
}
function help() {shell(`${intro('LaTeX & figures')}<div class="help-grid"><section class="panel"><h2>Text and formulas</h2><p>Type a statement or import a .tex file. The preamble and document wrapper are removed on import.</p><pre>Find the integers $n$ for which $n^2 + 1$ is prime.

\\[
  a^2 + b^2 = c^2
\\]</pre><p>Inline formulas: <code>$…$</code> or <code>\\(…\\)</code>. Display formulas: <code>\\[…\\]</code> or <code>$$…$$</code>. Lists using <code>itemize</code> are supported.</p><p>For a price, write <code>\\$ 100</code>.</p></section><section class="panel"><h2>Figures in the statement</h2><p>Upload an image or a one-page PDF, then select “Insert into statement”.</p><pre>See figure~\\ref{fig:example}.

\\begin{figure}
\\centering
\\includegraphics[width=0.7\\linewidth]{figure-1.svg}
\\caption{A short caption}
\\label{fig:example}
\\end{figure}</pre><p>Numbering starts at 1 for each problem. Use the exact uploaded filename.</p></section><section class="panel"><h2>Image files</h2><p>Use plain SVG for geometric drawings, containing shapes and paths without scripts, CSS or external resources. Convert text to paths in your drawing software if needed.</p><p>PNG and JPEG are also supported. A one-page PDF keeps the vector drawing: the page shows a rendered preview and links to the PDF. Limits: 2 MB per file, 20 figures per problem. Compile TikZ separately and export the drawing as PDF, SVG or PNG.</p><p>Administrators can also open <strong>Source figures</strong> in the editor: a gallery of redrawn figures from the reference books, opened on the problem’s own source page. Clicking a figure attaches it and inserts it into the statement.</p></section><section class="panel"><h2>Languages</h2><p>Start with one language. Choose “Add a language” for another version, or type a language name of your own. Each version has its own statement and approval. Figures can be shared between versions.</p><h2>Review and publication</h2><ol><li>Save your draft.</li><li>Check the preview in each language.</li><li>Submit for review.</li><li>An administrator can edit, return or publish the verified versions.</li></ol><p>LaTeX is used for statements and mathematics. Arbitrary packages, custom macros and system commands are not executed.</p></section></div>`);}
function privacy(){shell(`${intro('Privacy & contributions')}<article class="panel prose"><h2>Your account</h2><p>Your email address is used to sign in and confirm your account. It is not shown to other members. Your display name appears beside your published problems. WordPress stores passwords as hashes.</p><h2>Your contributions</h2><p>Only submit statements and figures you are permitted to share. Include sources and credits. Submitting a problem authorises its review, correction and publication on this website and its associated apps.</p><p>Administrators may publish minor corrections directly. A substantial mathematical change should be returned to the contributor with an explanation.</p><h2>Private information</h2><p>Drafts are visible to their author and administrators. Members can read published versions. Your progress is private. Images are accessible only to people allowed to view the corresponding problem.</p><h2>Emails and account deletion</h2><p>New-problem notifications are optional and can be disabled in your profile. Deleting your account removes your profile and drafts. Published contributions remain available with anonymous attribution.</p><h2>Cookies</h2><p>The site uses the WordPress cookies required for sign-in. It includes no advertising or analytics tools.</p>${session.local?'<div class="notice soft">Local preview: no emails are sent. The site operator’s contact details and legal notice must be added before public launch.</div>':''}</article>`);}
async function members(){
    if(!session.user?.admin){routeTo('/');return;}
    const seq=routeSequence;const data=await api('users');if(seq!==routeSequence)return;
    const row=(u:any)=>`<tr><td>${esc(u.name)}${u.admin?' <span class="badge">Admin</span>':''}${u.confirmed?'':' <span class="badge warn">Unconfirmed</span>'}</td><td class="members-email">${esc(u.email)}</td><td class="num">${u.submitted}</td><td class="num">${u.published}</td></tr>`;
    shell(`${intro('Members',`<span class="muted">${data.total} account${data.total===1?'':'s'}</span>`)}
    <p class="field-help">Submitted counts problems put forward for review; Published counts those live after review.</p>
    <div class="table-wrap"><table class="members-table"><thead><tr><th scope="col">Name</th><th scope="col">Email</th><th scope="col" class="num">Submitted</th><th scope="col" class="num">Published</th></tr></thead>
    <tbody>${data.users.map(row).join('')||'<tr><td colspan="4" class="muted">No accounts yet.</td></tr>'}</tbody></table></div>`,'members');
}
async function mailbox(){if(!session.user?.admin||!session.local){routeTo('/');return;}const mail=await api('mailbox');shell(`${intro('Test inbox')}<div class="mailbox">${mail.length?mail.map((m:any)=>`<article class="panel"><p class="small muted">${esc(String(m.to))} · ${date(m.date)}</p><h2>${esc(m.subject)}</h2><pre>${esc(m.message).replace(/https?:\/\/[^\s<&]+/g,(url:string)=>`<a href="${url}" target="_blank" rel="noopener">${url}</a>`)}</pre></article>`).join(''):empty('No emails yet','Confirmation emails for test accounts appear here.')}</div>`);}
// English addresses used in emails and the iPhone client; the historic French names remain valid.
const routeAliases:Record<string,string>={confirm:'confirmer',reset:'reinitialiser',problem:'probleme',profile:'profil',edit:'editer'};
async function route(){
    const current=location.hash||'#/';if(dirty&&current!==lastRoute&&!confirm('Leave without saving your changes?')){history.replaceState(null,'',lastRoute);return;}
    disposeReference?.();disposeReference=undefined;lastRoute=current;dirty=false;routeSequence++;const [path,query]=current.replace(/^#/,'').split('?');const parts=path.split('/').filter(Boolean);const page=routeAliases[parts[0]]||parts[0]||'';document.title='Flexagon';window.scrollTo(0,0);
    const restoring=backRestore&&!!listReturn&&listReturn.hash.replace(/^#/,'').split('?')[0]===path;backRestore=false;
    if(restoring)filters={...listReturn!.filters};
    try{if(!session)session=await api('session');
        if(['connexion','inscription','mot-de-passe','renvoyer','reinitialiser','confirmer'].includes(page))auth(page,new URLSearchParams(query));
        else if(page==='mes-propositions'){if(!restoring){filters.status='';filters.progress='';filters.triage='';}await collection('mine',restoring);}
        else if(page==='administration'){if(!restoring){filters.status='';filters.progress='';}await collection('review',restoring);}
        else if(page==='reference')await referencePage(parts[1],new URLSearchParams(query));else if(page==='about')about();else if(page==='progress')await progressPage();else if(page==='problems'){if(!restoring){filters.status='';filters.triage='';}await collection('published',restoring);}
        else if(page==='probleme')await reader(parts[1],new URLSearchParams(query).get('from')||'');else if(page==='editer')await editor(parts[1]);else if(page==='profil')profile();else if(page==='aide')help();else if(page==='confidentialite')privacy();else if(page==='courrier')await mailbox();else if(page==='membres')await members();else landing();
    }catch(error:any){shell(empty('Page unavailable',esc(error.message),'<a class="button" href="#/problems">Back to problems</a>'));}
}
root.addEventListener('input',(e)=>{
    const target=e.target as HTMLInputElement;
    if(target.id==='progress-search'){progressFilters.search=target.value;progressExpanded=Object.create(null);drawProgress();}
    if(target.id==='search'){filters.search=target.value;drawList();}
    if($('#latex')&&['latex','problem-title','language-name','edit-category','edit-difficulty','edit-source','keywords','approved','review-note'].includes(target.id)){
        dirty=true;$('#save-state').textContent='Unsaved changes';
        if(['latex','problem-title','language-name'].includes(target.id)){problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;}
        if(['edit-category','edit-difficulty','edit-source','keywords'].includes(target.id)){for(const v of Object.values(problem.versions) as any)v.approved=false;if($('#approved'))$('#approved').checked=false;}
        if(target.id==='latex')preview();
    }
});
root.addEventListener('change',async(e)=>{
    const target=e.target as HTMLInputElement;
    if(target.id==='reader-language'){language=target.value;showReader();return;}
    if(['progress-category','progress-difficulty','progress-source'].includes(target.id)){(progressFilters as any)[target.id.slice(9)]=target.value;progressExpanded=Object.create(null);drawProgress();return;}
    if(['category','difficulty','source','progress','status','triage','sort'].includes(target.id)){(filters as any)[target.id]=target.value;drawList();}
    try{
        if(target.id==='tex-file'&&target.files?.[0]){if(target.files[0].size>60000)throw Error('The .tex file must be under 60 KB.');let text=await target.files[0].text();const body=/\\begin\{document\}([\s\S]*?)\\end\{document\}/.exec(text);if(body)text=body[1].trim();$('#latex').value=text;problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;dirty=true;$('#save-state').textContent='Unsaved changes';preview();}
        if((target.id==='figure-file'||target.id==='avatar-file')&&target.files?.[0]){
            const file=target.files[0];if(file.size>2*1024*1024)throw Error('Each file must be no larger than 2 MB.');
            const isFigure=target.id==='figure-file';if(isFigure)collectEditor();const data=new FormData();data.append('file',file);data.append('problem',isFigure?String(problem.id):'0');if(isFigure)data.append('revision',String(problem.revision));target.disabled=true;
            if(isFigure&&/\.pdf$/i.test(file.name)){toast('Rendering the PDF preview…');data.append('preview',await pdfPreview(file),file.name.replace(/\.pdf$/i,'.png'));}
            const uploaded=await api('assets',data);
            if(isFigure){problem.assets[uploaded.name]=uploaded.asset;problem.revision=uploaded.revision;showEditor();toast('Figure added. Select “Insert into statement”.');}
            else{avatar=uploaded.asset.id;const existing=$('#avatar-preview')||$('#avatar-placeholder');existing.outerHTML=`<img id="avatar-preview" src="${esc(uploaded.asset.url)}" alt="New profile image">`;toast('Image uploaded. Save your preferences.');}
        }
    }catch(error:any){message(error.message,true);}finally{target.disabled=false;}
});
root.addEventListener('click',async(e)=>{
    const b=(e.target as HTMLElement).closest<HTMLElement>('[data-action],[data-save],[data-reader-lang],[data-editor-lang],[data-insert],[data-figure],[data-detach],[data-progress],[data-triage],[data-source],[data-progress-mode],[data-group-by],[data-more-group]');if(!b)return;
    try{
        if(b.dataset.progressMode){progressFilters.mode=b.dataset.progressMode as any;progressExpanded=Object.create(null);drawProgress();return;}
        if(b.dataset.groupBy){progressFilters.groupBy=b.dataset.groupBy as any;progressExpanded=Object.create(null);drawProgress();return;}
        if(b.dataset.moreGroup){progressExpanded[b.dataset.moreGroup]=(progressExpanded[b.dataset.moreGroup]||24)+24;drawProgress();return;}
        if(b.dataset.action==='reset-progress'){progressFilters={...progressFilters,search:'',category:'',difficulty:'',source:''};progressExpanded=Object.create(null);for(const k of ['search','category','difficulty','source'])$('#progress-'+k).value='';drawProgress();return;}
        if(b.dataset.action==='remove-language'){collectEditor();const v=problem.versions[editorLanguage];if(Object.keys(problem.versions).length<2)return;if((v.title||v.latex)&&!confirm('Remove the '+v.language+' version from this draft? A published copy remains available until you publish again.'))return;delete problem.versions[editorLanguage];dirty=true;showEditor();return;}
        if(b.dataset.action==='previous-page'||b.dataset.action==='next-page'){listPage+=b.dataset.action==='next-page'?1:-1;drawList(false);$('#problem-list').scrollIntoView({block:'start'});return;}
        if(b.dataset.save){await saveProblem(b.dataset.save);return;}
        if(b.dataset.readerLang){language=b.dataset.readerLang;showReader();return;}
        if(b.dataset.editorLang){collectEditor();editorLanguage=b.dataset.editorLang;showEditor();return;}
        if(b.dataset.action==='figure-library'){collectEditor();library.open=!library.open;showEditor();return;}
        if(b.dataset.figure){
            // Always attach: a copy attached earlier is refreshed from the current library file.
            collectEditor();b.setAttribute('disabled','');const attached=await api('problems/'+problem.id+'/figures',{figure:b.dataset.figure,revision:problem.revision});problem.assets[attached.name]=attached.asset;problem.revision=attached.revision;showEditor();
            insertFigure(attached.name);toast('Figure inserted into the statement.');return;
        }
        if(b.dataset.insert){insertFigure(b.dataset.insert);return;}
        if(b.dataset.detach){
            const name=b.dataset.detach;const used=new RegExp('\\\\includegraphics(?:\\[[^\\]]*\\])?\\{'+name.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')+'\\}');
            if(!confirm(`Remove ${name} from this problem?`+(used.test(value('latex'))?' The statement still refers to it; delete that figure block afterwards.':'')))return;
            collectEditor();b.setAttribute('disabled','');const removed=await api('problems/'+problem.id+'/assets/'+encodeURIComponent(name),{revision:problem.revision},'DELETE');
            delete problem.assets[name];problem.revision=removed.revision;showEditor();toast('Figure removed.');return;
        }
        if(b.dataset.progress){await api('problems/'+problem.id+'/progress',{progress:b.dataset.progress});problem.progress=b.dataset.progress;showReader();return;}
        if(b.dataset.triage){const id=b.dataset.triageId!;await api('problems/'+id+'/triage',{triage:b.dataset.triage});if(problem&&String(problem.id)===id)problem.triage=b.dataset.triage;const item=listing?.items?.find((p:any)=>String(p.id)===id);if(item)item.triage=b.dataset.triage;if($('#problem-list'))drawList(false);else document.querySelectorAll<HTMLElement>(`[data-triage][data-triage-id="${id}"]`).forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.triage===b.dataset.triage)));return;}
        if(b.dataset.action==='back-to-list'){backRestore=!!listReturn;routeTo(listReturn?listReturn.hash.replace(/^#/,''):(session.user?.admin?'/administration':'/mes-propositions'));return;}
        if(b.dataset.source){filters.source=b.dataset.source;$('#source').value=b.dataset.source;drawList();return;}
        if(b.dataset.action==='new'){if(!session.user){routeTo('/connexion');return;}b.setAttribute('disabled','');const created=await api('problems',{});routeTo('/editer/'+created.id);}
        if(b.dataset.action==='reset-filters'){filters={search:'',category:'',difficulty:'',source:'',progress:'',status:'',triage:'',sort:'newest'};for(const [id,v] of Object.entries(filters))if($('#'+id))$('#'+id).value=v;drawList();}
        if(b.dataset.action==='pick'){const items=filtered();if(!items.length){toast('No problems match these filters.');return;}routeTo('/probleme/'+items[Math.floor(Math.random()*items.length)].id);}
        if(b.dataset.action==='logout'){await api('auth/logout',{});location.hash='#/';location.reload();}
        if(b.dataset.action==='delete-draft'&&confirm('Delete this draft, its figures and revision history?')){await api('problems/'+problem.id,{},'DELETE');dirty=false;routeTo('/mes-propositions');toast('Draft deleted.');}
        if(b.dataset.action==='delete-account'&&confirm('Permanently delete your account and drafts?')){await api('account',{password:value('delete-password')},'DELETE');location.hash='#/';location.reload();}
        if(b.dataset.action==='history'){const entries=await api('problems/'+problem.id+'/history');$('#history').innerHTML=`<section class="panel"><h2>History</h2>${entries.length?entries.map((entry:any)=>`<details class="history-entry"><summary>${esc(actions[entry.action]||entry.action)} · ${date(entry.date)} · ${esc(entry.by)}</summary><p>Revision ${entry.snapshot.revision} — ${esc(titleOf(entry.snapshot))}</p>${Object.entries(entry.snapshot.versions).map(([lang,v]:any)=>`<h3>${esc(languageName(lang,v))} ${v.approved?'✓':''}</h3><pre>${esc(v.title)}\n\n${esc(v.latex)}</pre>`).join('')}</details>`).join(''):'<p>No saved revisions yet.</p>'}</section>`;}
    }catch(error:any){message(error.message,true);}finally{b.removeAttribute('disabled');}
});
// Capture the list position the moment a problem row is opened (plain-anchor navigation).
root.addEventListener('click',(e)=>{
    if((e.target as HTMLElement).closest('a.problem-row')&&$('#problem-list'))listReturn={hash:location.hash,filters:{...filters},page:listPage,scroll:window.scrollY};
},true);
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
window.addEventListener('hashchange',route);
route();
